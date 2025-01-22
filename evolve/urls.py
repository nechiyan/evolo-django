
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from events.view import EventViewSet,GalleryImageViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'gallery', GalleryImageViewSet)

urlpatterns = [
    path('admin-d1abc891-c973-4a98-86ab/', admin.site.urls),
    # path('api/v1/', include(router.urls)),
    path('api/v1/users/', include('api.v1.users.urls', namespace='api_v1_users')),  

]
