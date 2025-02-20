from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('get-towns', views.getTowns, name='GetTowns'),
    path('get-villages', views.getVillages, name='GetVillages'),
    path('route', views.route, name='route'),
    path('download-gpx', views.downloadGPX, name='DownloadGpx'),

]
