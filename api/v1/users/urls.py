from django.urls import re_path
from api.v1.users import views

urlpatterns = [
    # re_path(r'^users/$', views.UserList.as_view()),
    # re_path(r'^users/(?P<pk>\d+)/$', views.UserDetail.as_view()),
]
app_name = 'api_v1_users'