from django.contrib import admin
from .models import Event, TicketCategory, EventTicket, GalleryImage,TicketPurchase


class EventTicketInline(admin.TabularInline):
    model = EventTicket
    list_display = ('id')
    extra = 1  # Number of empty forms to display for new ticket categories

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue', 'capacity', 'created_at', 'updated_at')
    search_fields = ('title', 'venue')
    inlines = [EventTicketInline]
    # filter_horizontal = ('ticket_categories',)  # Allows selection of multiple ticket categories

class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

class EventTicketAdmin(admin.ModelAdmin):
    list_display = ("id",'event', 'ticket_category', 'price', 'max_quantity', 'sold_count', 'remaining_tickets')
    list_filter = ('event', 'ticket_category')
    search_fields = ('event__title', 'ticket_category__name')

class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'image', 'caption', 'created_at')
    search_fields = ('event__title',)
    list_filter = ('created_at',)

class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_category', 'user_email', 'quantity','total_price','payment_status')
    search_fields = ('ticket_category',)
    list_filter = ('payment_status',)

admin.site.register(Event, EventAdmin)
admin.site.register(TicketCategory, TicketCategoryAdmin)
admin.site.register(EventTicket, EventTicketAdmin)
admin.site.register(GalleryImage, GalleryImageAdmin)
admin.site.register(TicketPurchase, TicketPurchaseAdmin)
