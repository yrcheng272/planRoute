import warnings
warnings.filterwarnings("ignore")

from .tools import *
# from .graph_route import plot_graph_route
from .gpx_formatter import TEMPLATE, TRACE_POINT

import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
from datetime import datetime
import folium
import os.path

from network import Network
from network.algorithms import hierholzer

ox.settings.use_cache = True
ox.settings.log_console = True

CUSTOM_FILTER = (
    '["highway"]["area"!~"yes"]["highway"!~"bridleway|bus_guideway|bus_stop|construction|cycleway|elevator|footway|'
    'motorway|motorway_junction|motorway_link|escalator|proposed|construction|platform|raceway|rest_area|'
    'path|service"]["access"!~"customers|no|private"]["public_transport"!~"platform"]'
    '["fee"!~"yes"]["foot"!~"no"]["service"!~"drive-through|driveway|parking_aisle"]["toll"!~"yes"]'
)


def generateRoute(location, village_id):

    try:
        org_graph = ox.graph_from_place(location, network_type='walk', custom_filter=CUSTOM_FILTER)
    
    except ValueError as msg:
        print(msg)
        return False, 'OpenStreetMap裡面沒有資料QQ'
    except TypeError as msg:
        print(msg)
        return False, 'OpenStreetMap裡面的資料只有一個點，不足以規劃路線QQ'
    # Simplifying the original directed multi-graph to undirected, so we can go both ways in one way streets
    graph = ox.convert.to_undirected(org_graph)

    # Finds the odd degree nodes and minimal matching
    odd_degree_nodes = get_odd_degree_nodes(graph)
    pair_weights = get_shortest_distance_for_odd_degrees(graph, odd_degree_nodes)
    matched_edges_with_weights = min_matching(pair_weights)

    # List all edges of the extended graph including original edges and edges from minimal matching
    single_edges = [(u, v) for u, v, k in graph.edges]
    added_edges = get_shortest_paths(graph, matched_edges_with_weights)
    edges = map_osmnx_edges2integers(graph, single_edges + added_edges)

    # Finds the Eulerian path
    network = Network(len(graph.nodes), edges, weighted=True)
    eulerian_path = hierholzer(network)
    converted_eulerian_path = convert_integer_path2osmnx_nodes(eulerian_path, graph.nodes())
    double_edge_heap = get_double_edge_heap(org_graph)

    # Finds the final path with edge IDs
    final_path = convert_path(graph, converted_eulerian_path, double_edge_heap)

    coordinates_path = convert_final_path_to_coordinates(org_graph, final_path)

    # Route statistics from OSMnx 
    eccentricity = nx.eccentricity(graph)
    center = nx.center(graph)
    center_node = graph.nodes[center[0]]

    trace_points = "\n\t\t\t".join([TRACE_POINT.format(
        lat=lat, lon=lon, id=i, timestamp=datetime.now().isoformat()
    ) for i, (lat, lon) in enumerate(coordinates_path)])

    gpx_payload = TEMPLATE.format(
        name=location,
        trace_points=trace_points,
        center_lat=center_node["y"],
        center_lon=center_node["x"]
    )

    if not os.path.exists(f'routes/data/{village_id}/'):
        os.mkdir(f'routes/data/{village_id}/')
    
    gpx_path = f"routes/data/{village_id}/{location}.gpx"
    with open(gpx_path, "w") as f:
        f.write(gpx_payload)
    
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(org_graph)
    m = gdf_edges.explore()
    m = gdf_nodes.explore(m=m, color="red")
    folium.LayerControl().add_to(m)
    outfp = f"routes/data/{village_id}/route_map.html"
    m.save(outfp)

    return True, outfp
    # save list of route pngs
    # fig, ax = plot_graph_route(org_graph, final_path, route_linewidth=6, node_size=0, bgcolor="w", route_alpha=0.2, route_color="w")

    # for i, e in enumerate(final_path, start=1):
    #     fig, ax = plot_graph_route(org_graph, final_path[:i], route_linewidth=6, node_size=0, bgcolor="w", route_alpha=0.2)
    #     ax.set_title(location)
    #     fig.savefig(f"catalog/data/route_imgs/img_{i}.png", dpi=120, bbox_inches="tight")