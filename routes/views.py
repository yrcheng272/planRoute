from django.shortcuts import render

# Create your views here.
from django.http import FileResponse, JsonResponse
from routes.utils import algos

import xml.etree.ElementTree as ET

# Create your views here.
def index(request):

    cities = loadXmlData('routes/static/xmls/cities.xml')

    context = {
        'cities': cities,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


def route(request):

    if request.GET.get('town') == '' or request.GET.get('village') == '':
        return render(request, 'index.html')

    location = f"{request.GET.get('city')}{request.GET.get('town')}{request.GET.get('village')}"
    vid = request.GET.get('vid')
    result, msg = algos.generateRoute(location, vid)

    if result:
        with open(msg, 'r') as f:
            content = f.read()
        response_data = {
            'content' : content,
            'location' : location
        }
    else:
        response_data = {
            'content' : msg,
            'location' : location
        }
    return JsonResponse(response_data)


def downloadGPX(request):
    file_path = f"routes/data/{request.POST.get('vid')}/{request.POST.get('loc')}.gpx"
    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
    return response


def getTowns(request):
    city = request.GET.get('city')
    towns = loadXmlData(f'routes/static/xmls/towns/{city}.xml')
    response_data = {
        "towns" : towns
    }
    return JsonResponse(response_data)


def getVillages(request):
    town = request.GET.get('town')
    villages = loadXmlData(f'routes/static/xmls/villages/{town}.xml')

    response_data = {
        "villages" : villages
    }
    return JsonResponse(response_data)


def loadXmlData(file_path):
    tree = ET.parse(file_path) # From XML String
    root = tree.getroot()
    lst = []
    for ele in root:
        dct = {}
        for e in ele:
            dct[e.tag] = e.text
        lst.append(dct)
    
    return lst
