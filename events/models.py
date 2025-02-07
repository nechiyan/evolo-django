from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _


class TicketCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  
    description = models.TextField(blank=True, null=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ticket_categories'
        verbose_name = _('Ticket Category')
        verbose_name_plural = _('Ticket Categories')

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    capacity = models.IntegerField()
    ticket_categories = models.ManyToManyField(TicketCategory, through='EventTicket', related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return self.title

    def remaining_capacity(self):
        """
        Calculates the remaining capacity across all ticket categories.
        """
        total_sold = sum(event_ticket.sold_count for event_ticket in self.eventticket_set.all())
        return self.capacity - total_sold


class EventTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_quantity = models.IntegerField()  # Maximum tickets available for this category in this event
    sold_count = models.IntegerField(default=0)  # Track tickets sold for this category in this event
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event_tickets'
        verbose_name = _('Event Ticket')
        verbose_name_plural = _('Event Tickets')

    def __str__(self):
        return f"{self.ticket_category.name} for {self.event.title}"

    def remaining_tickets(self):
        """
        Calculates the remaining tickets for this category in this event.
        """
        return self.max_quantity - self.sold_count


class GalleryImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gallery_images'
        verbose_name = _('Gallery Image')
        verbose_name_plural = _('Gallery Images')

    def __str__(self):
        return f"Image for {self.event.title}"


class TicketPurchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE, related_name='purchases')
    user_email = models.EmailField()  # Collect user email for notifications
    quantity = models.IntegerField()  # Number of tickets purchased
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed')],
        default='PENDING',
    )
    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_purchases'
        verbose_name = _('Ticket Purchase')
        verbose_name_plural = _('Ticket Purchases')

    def __str__(self):
        return f"Purchase by {self.user_email} for {self.event_ticket.event.title}"
