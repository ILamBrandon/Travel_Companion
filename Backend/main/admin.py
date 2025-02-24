# main/admin.py

from django.contrib import admin
from .models import Itinerary

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'state', 'country', 'start_date', 'end_date')
    list_filter = ('city', 'state', 'country', 'start_date')
