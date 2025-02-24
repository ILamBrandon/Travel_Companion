from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItineraryViewSet

router = DefaultRouter()
router.register('itineraries', ItineraryViewSet, basename='itinerary')

urlpatterns = [
    path('', include(router.urls)),
]
