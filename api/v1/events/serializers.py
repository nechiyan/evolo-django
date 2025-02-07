
from rest_framework import serializers
from events.models import Event,GalleryImage,EventTicket,TicketCategory

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
    
class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_date', 'venue', 'capacity', 'price']


class EventTicketSerializer(serializers.ModelSerializer):
    # Define custom fields
    ticket_category_name = serializers.CharField(source='ticket_category.name', read_only=True)
    remaining_tickets = serializers.SerializerMethodField()

    class Meta:
        model = EventTicket
        fields = ['id', 'event', 'ticket_category', 'ticket_category_name', 'price', 'max_quantity', 'sold_count', 'remaining_tickets']

    def get_remaining_tickets(self, obj):
        return obj.remaining_tickets() 

class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = ['id', 'name', 'description','price'] 