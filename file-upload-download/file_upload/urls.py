from django.urls import re_path, path
from . import views

app_name = "file_upload"

urlpatterns = [


    re_path(r'^upload/$', views.file_upload, name='file_upload'),
    path('', views.file_list, name='file_list'),

]