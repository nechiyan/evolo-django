# import request

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import stripe

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from events.models import Event,EventTicket,TicketPurchase,TicketCategory
from api.v1.events.serializers import EventListSerializer,TicketCategorySerializer
from evolve.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .functions import add_to_google_sheet 

import json


stripe.api_key = settings.STRIPE_SECRET_KEY

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
            items_per_page = events.count()
            page_number = 1 
        else:
            items_per_page = 6

        print('events')
        paginated = Paginator(
            instances=events,
            count=events.count(),
            items_per_page=items_per_page,
            default_page_number=1,
            page_number=page_number
        )

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

"""
function for getting a single event
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def get_event(request, pk):
    try:
        event = get_object_or_404(Event, id=pk)
        serialized_data = EventListSerializer(event, context={'request': request}).data
        response_data = {
            "StatusCode": 6000,
            "data": {
                "title": "Success",
                "message": "Event details retrieved successfully",
                "data": serialized_data,
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        response_data = {
            "StatusCode": 6001,
            "data": {
                "title": "Error",
                "message": "Not a valid event id"
            }
        }
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_checkout_session(request):
    try:
        data = request.data
        # Fetch the TicketCategory based on ticket_id
        ticket_category = TicketCategory.objects.get(id=data['ticket_id'])
        quantity = int(data['quantity'])
        user_email = data['user_email']

        # Calculate total price (assuming each ticket in the category has a price)
        unit_price = ticket_category.price
        total_price = unit_price * quantity

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f"{ticket_category.name}",
                        'description': f"Quantity: {quantity}",
                    },
                    'unit_amount': int(unit_price * 100),  # Convert to cents
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url='http://localhost:3000/success',  # Replace with your React success URL
            cancel_url='http://localhost:3000/cancel',   # Replace with your React cancel URL
            metadata={
                'ticket_category_id': str(ticket_category.id),
                'quantity': quantity,
                'unit_price': str(unit_price),
                'total_price': str(total_price),
                'user_email': user_email
            }
        )

        # Create a TicketPurchase linked directly to TicketCategory
        TicketPurchase.objects.create(
            ticket_category=ticket_category,  # Link directly to TicketCategory, not EventTicket
            user_email=user_email,
            quantity=quantity,
            total_price=total_price,
            stripe_payment_id=session.id,
            payment_status='PENDING'
        )

        return Response({'session_id': session.id}, status=status.HTTP_200_OK)

    except TicketCategory.DoesNotExist:
        return Response(
            {'error': 'Invalid Ticket Category'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Retrieve the purchase and verify the payment
            with transaction.atomic():
                purchase = TicketPurchase.objects.select_for_update().get(
                    stripe_payment_id=session.id,
                    payment_status='PENDING'
                )
                
                # Verify the payment amount matches
                expected_amount = purchase.total_price
                paid_amount = Decimal(session.amount_total) / 100  # Convert cents to dollars
                
                if paid_amount != expected_amount:
                    purchase.payment_status = 'FAILED'
                    purchase.save()
                    return JsonResponse(
                        {'error': 'Payment amount mismatch'}, 
                        status=400
                    )

                # Verify ticket availability again
                event_ticket = purchase.event_ticket
                if event_ticket.remaining_tickets() < purchase.quantity:
                    purchase.payment_status = 'FAILED'
                    purchase.save()
                    return JsonResponse(
                        {'error': 'Tickets no longer available'}, 
                        status=400
                    )

                # Update ticket count and purchase status
                event_ticket.sold_count += purchase.quantity
                event_ticket.save()
                
                purchase.payment_status = 'SUCCESS'
                purchase.save()

                # Send confirmation email
                # send_ticket_confirmation(purchase)

        return JsonResponse({'status': 'success'})

    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except TicketPurchase.DoesNotExist:
        return JsonResponse({'error': 'Purchase not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tickets_categories(request):
    tickets = TicketCategory.objects.all()  # Get all EventTickets
    
    if tickets.exists():
        print(tickets,'ticket names')
        # Serialize the tickets
        serializer = TicketCategorySerializer(tickets, many=True)
        return Response(serializer.data)  # Return the tickets as JSON
    else:
        return Response({"message": "No tickets available."}, status=404)

# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import stripe
# from django.conf import settings

# stripe.api_key = settings.STRIPE_SECRET_KEY
# # Disable CSRF for simplicity (use proper auth in production)


from django.shortcuts import render

def checkout_view(request):
    return render(request, 'events/checkout.html')  # Update template path
