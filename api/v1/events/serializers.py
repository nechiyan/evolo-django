
from rest_framework import serializers
from events.models import Event,GalleryImage

class EventListSerializer(serializers.ModelSerializer):
    event_date = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = '__all__'

    def get_event_date(self, obj):
        if obj.event_date:
            return obj.event_date.strftime("%d/%m/%y")
        else:
            return None