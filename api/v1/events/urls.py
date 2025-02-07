from django.urls import re_path
from api.v1.events import views

app_name = 'api_v1_events'

urlpatterns = [
    re_path(r'^list/$', views.get_events),
    re_path(r'^list/(?P<pk>.*)/$', views.get_event),
    re_path(r'^ticket-categories/$', views.get_tickets_categories),

    re_path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    re_path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    # re_path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    # re_path('', views.checkout_view, name='checkout'),
]