from django.contrib import admin
from .models import Event, GalleryImage

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'venue', 'capacity', 'price')
    search_fields = ('title', 'venue')
    list_filter = ('event_date',)
    ordering = ('-event_date',)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'caption', 'created_at')
    search_fields = ('event__title', 'caption')
    list_filter = ('created_at',)

