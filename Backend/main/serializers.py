from rest_framework import serializers
from .models import Itinerary

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = [
            'id',
            'user',
            'title',
            'city',
            'state',
            'country',
            'start_date',
            'end_date',
            'reason',
            'planning_details'
        ]
        read_only_fields = ['user']
