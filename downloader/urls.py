from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='downloader-home'),
    path('channels', views.get_channels, name='downloader-channels'),
    path('epg', views.get_epg, name='downloader-epg'),
    path('download', views.download, name='downloader-download'),
]