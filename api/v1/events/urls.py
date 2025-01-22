from django.urls import re_path
from api.v1.events import views

app_name = 'api_v1_events'

urlpatterns = [
    re_path(r'^list/$', views.get_events),
]