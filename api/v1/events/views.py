# import request

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from events.models import Event
from api.v1.events.serializers import EventListSerializer
from evolve.paginator import Paginator

"""
function for getting all events
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def get_events(request):
    page_number = request.GET.get('page')
    events = Event.objects.all()
    if events.exists():

        if page_number and page_number.lower() == "list":
        # Retrieve all data on a single page
            items_per_page = events.count()
            page_number = 1 
        else:
        # Set the number of items per page
            items_per_page = 6

        print('events')
        paginated = Paginator(
            instances=events,
            count=events.count(),
            items_per_page=items_per_page,
            default_page_number=1,
            page_number=page_number
        )

        # data = paginated.pagination_data
        serialized_data = EventListSerializer(paginated.objects, many=True, context={'request': request}).data
        response_data = {
            "StatusCode": 6000,
            "title": "Success",
            "data": serialized_data,
            'pagination_data': paginated.pagination_data,

        }
    else:
        response_data = {
            "StatusCode": 6001,
            "data": {
                "title": "Failed",
                "message": 'No Events found'
            }
        }
    return Response(response_data, status=status.HTTP_200_OK)
