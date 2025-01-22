# events/views.py
from rest_framework import viewsets
from .models import Event,GalleryImage
from .serializer import EventSerializer,GalleryImageSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer