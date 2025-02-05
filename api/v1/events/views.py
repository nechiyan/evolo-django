# import request

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import stripe

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from events.models import Event,EventTicket,TicketPurchase
from api.v1.events.serializers import EventListSerializer
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
        event_ticket = EventTicket.objects.get(id=data['event_ticket_id'])
        quantity = int(data['quantity'])
        user_email = data['user_email']

        # Validate ticket availability
        if event_ticket.remaining_tickets() < quantity:
            return Response(
                {'error': 'Not enough tickets available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total price
        unit_price = event_ticket.price
        total_price = unit_price * quantity

        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"{event_ticket.ticket_category.name} - {event_ticket.event.title}",
                        'description': f"Quantity: {quantity}",
                    },
                    'unit_amount': int(unit_price * 100),  # Convert to cents
                },
                'quantity': quantity,
            }],
            mode='payment',
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3000/cancel', 
            # success_url=settings.STRIPE_SUCCESS_URL,
            # cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={
                'event_ticket_id': str(event_ticket.id),
                'quantity': quantity,
                'unit_price': str(unit_price),
                'total_price': str(total_price),
                'user_email': user_email
            }
        )

        # Create pending purchase record
        TicketPurchase.objects.create(
            event_ticket=event_ticket,
            user_email=user_email,
            quantity=quantity,
            total_price=total_price,
            stripe_payment_id=session.id,
            payment_status='PENDING'
        )

        return Response({'session_id': session.id}, status=status.HTTP_200_OK)

    except EventTicket.DoesNotExist:
        return Response(
            {'error': 'Invalid ticket'}, 
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


# @csrf_exempt  # Add this if you're testing without CSRF token
# def create_payment_intent(request):
#     if request.method == 'POST':
#         try:
#             # Debug: Print the raw request body
#             print("Request body:", request.body)
            
#             # Check if request body is empty
#             if not request.body:
#                 return JsonResponse({'error': 'Empty request body'}, status=400)
            
#             data = json.loads(request.body)
            
#             # Debug: Print parsed data
#             print("Parsed data:", data)
            
#             # Validate required fields
#             if 'amount' not in data:
#                 return JsonResponse({'error': 'Amount is required'}, status=400)
                
#             amount = int(data.get('amount'))
#             currency = data.get('currency', 'usd')
            
#             # Create a Stripe PaymentIntent
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=amount,
#                 currency=currency,
#                 payment_method_types=['card','paypal'],
#             )
            
#             return JsonResponse({
#                 'clientSecret': payment_intent.client_secret
#             })
        
#         except json.JSONDecodeError as e:
#             return JsonResponse({
#                 'error': 'Invalid JSON format',
#                 'details': str(e)
#             }, status=400)
#         except stripe.error.StripeError as e:
#             return JsonResponse({
#                 'error': 'Stripe error',
#                 'details': str(e)
#             }, status=400)
#         except Exception as e:
#             return JsonResponse({
#                 'error': 'Server error',
#                 'details': str(e)
#             }, status=500)
    
#     return JsonResponse({'error': 'Method not allowed'}, status=405)
