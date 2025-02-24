import re
import asyncio
import httpx
import requests
import aiohttp
import time
from asgiref.sync import async_to_sync
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.conf import settings

from .models import Itinerary
from .serializers import ItinerarySerializer

# Simple in-memory cache for translations.
translation_cache = {}

class ItineraryViewSet(viewsets.ModelViewSet):
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='weather')
    def get_weather(self, request):
        """
        Example endpoint: /api/itineraries/weather/?city=LosAngeles
        Uses Nominatim to get coordinates for the given city and then fetches
        hourly and daily forecast data from the free Open-Meteo API.
        """
        city = request.query_params.get('city')
        if not city:
            return Response({"error": "City parameter is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            # Get latitude and longitude via Nominatim
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            geo_params = {
                "q": city,
                "format": "json",
                "limit": 1
            }
            headers = {"User-Agent": "YourAppName/1.0"}
            geo_resp = requests.get(nominatim_url, params=geo_params, headers=headers)
            geo_data = geo_resp.json()
            if not geo_data:
                return Response({"error": f"No location found for '{city}'."},
                                status=status.HTTP_404_NOT_FOUND)
            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]
        except Exception as e:
            return Response({"error": f"Geocoding error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Build the Open-Meteo API request URL and parameters.
            meteo_url = "https://api.open-meteo.com/v1/forecast"
            meteo_params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "temperature_2m,precipitation,relativehumidity_2m,windspeed_10m,winddirection_10m,weathercode",
                "daily": "temperature_2m_max,temperature_2m_min,uv_index_max,sunrise,sunset,weathercode",
                "timezone": "auto",
                "temperature_unit": "fahrenheit",
                "forecast_days": 10
            }
            meteo_resp = requests.get(meteo_url, params=meteo_params)
            meteo_data = meteo_resp.json()
            if meteo_resp.status_code == 200:
                # Optionally limit the daily forecast to 7 days if more are returned
                if "daily" in meteo_data and "time" in meteo_data["daily"]:
                    num_days = len(meteo_data["daily"]["time"])
                    if num_days > 10:
                        for key in meteo_data["daily"]:
                            meteo_data["daily"][key] = meteo_data["daily"][key][:10]
                return Response(meteo_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": meteo_data.get("error", "Error fetching forecast")},
                                status=meteo_resp.status_code)
        except Exception as e:
            return Response({"error": f"Forecast error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['get'], url_path='attractions')
    def get_attractions(self, request):
        # Synchronously call the async implementation.
        return async_to_sync(self._async_get_attractions)(request)

    async def _async_get_attractions(self, request):
        """
        Asynchronous attractions endpoint.
        Uses aiohttp for all external calls with high concurrency and HTTP/2 enabled.
        Skips translation for names that are already English (using isascii()).
        """
        # Set up a connector with high concurrency and HTTP/2 (experimental).
        connector = aiohttp.TCPConnector(limit=300, force_close=False)
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15)) as session:
            # Helper: split text into chunks if too long.
            def split_text(text, max_len=4900):
                return [text[i:i+max_len] for i in range(0, len(text), max_len)]
            
            # --- Geocoding using aiohttp ---
            city = request.query_params.get("city", "").strip()
            state = request.query_params.get("state", "").strip()
            country = request.query_params.get("country", "").strip()
            if not city:
                return Response({"error": "City parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            search_query = city
            if state:
                search_query += f", {state}"
            if country:
                search_query += f", {country}"
            search_params = {
                "q": search_query,
                "format": "json",
                "addressdetails": 1,
                "limit": 1
            }
            try:
                async with session.get(nominatim_url, params=search_params, headers={"User-Agent": "YourAppName/1.0 (https://example.com)"}) as resp:
                    if resp.status != 200:
                        return Response({"error": "Error fetching location from Nominatim"}, status=resp.status)
                    results = await resp.json()
                    if not results:
                        return Response({"error": f"No results found for '{search_query}'."}, status=404)
                    address = results[0].get("address", {})
                    state = state or address.get("state", "")
                    country = country or address.get("country", "")
                    bounding_box = results[0].get("boundingbox", [])
                    if len(bounding_box) < 4:
                        return Response({"error": "Could not retrieve bounding box for the specified location."}, status=404)
                    south, north, west, east = bounding_box
            except Exception as e:
                return Response({"error": f"Nominatim request error: {str(e)}"}, status=500)
            
            # --- Overpass Query using aiohttp ---
            overpass_bbox = f"{south},{west},{north},{east}"
            tourism_tags = (
                "museum|gallery|zoo|theme_park|viewpoint|attraction|aquarium|information|"
                "artwork|camp_site|caravan_site|guest_house|hostel|motel|picnic_site|hotel|"
            )
            overpass_url = "https://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["tourism"~"{tourism_tags}"]({overpass_bbox});
              way["tourism"~"{tourism_tags}"]({overpass_bbox});
              relation["tourism"~"{tourism_tags}"]({overpass_bbox});
              node["amenity"="restaurant"]({overpass_bbox});
              way["amenity"="restaurant"]({overpass_bbox});
              relation["amenity"="restaurant"]({overpass_bbox});
            );
            out center;
            """
            try:
                async with session.post(overpass_url, data=overpass_query.encode('utf-8')) as resp:
                    if resp.status != 200:
                        return Response({"error": "Error fetching attractions from Overpass"}, status=resp.status)
                    overpass_data = await resp.json()
            except Exception as e:
                return Response({"error": f"Overpass request error: {str(e)}"}, status=500)
            
            # --- Prepare attractions for translation ---
            processed_attractions = []
            SAFE_LEN = 5000
            names_to_translate = []  # each item: a string or list of chunks
            indices_to_translate = []  # indices in processed_attractions needing translation
            
            for element in overpass_data.get("elements", []):
                tags = element.get("tags", {})
                name = tags.get("name:en", tags.get("name", "")).strip()
                if not name or name.lower() == "unnamed":
                    continue
                # Only mark for translation if no explicit English name and not clearly English.
                if "name:en" not in tags and not name.isascii():
                    if len(name) > SAFE_LEN:
                        chunks = split_text(name, max_len=SAFE_LEN)
                        names_to_translate.append(chunks)
                    else:
                        names_to_translate.append(name)
                    indices_to_translate.append(len(processed_attractions))
                processed_attractions.append({
                    "element": element,
                    "name": name  # might be updated
                })
            
            # --- Asynchronous translation using aiohttp with caching and retries ---
            async def async_translate_text(text, dest='en', retries=5, delay=0.3, session=None):
                if text in translation_cache:
                    return translation_cache[text]
                url = "https://translate.google.com/translate_a/single"
                params = {
                    "client": "gtx",
                    "sl": "auto",
                    "tl": dest,
                    "dt": "t",
                    "q": text,
                }
                for attempt in range(retries):
                    try:
                        async with session.get(url, params=params) as response:
                            data = await response.json()
                            if data and isinstance(data, list) and data[0]:
                                translated_text = data[0][0][0]
                                if translated_text:
                                    translation_cache[text] = translated_text
                                    return translated_text
                    except Exception as e:
                        print(f"Error translating '{text}': {e}, attempt {attempt+1}")
                        await asyncio.sleep(delay * (2 ** attempt))
                translation_cache[text] = text
                return text

            async def process_translation(item, session):
                if isinstance(item, list):
                    tasks = [async_translate_text(chunk, session=session) for chunk in item]
                    translated_chunks = await asyncio.gather(*tasks)
                    return " ".join(translated_chunks)
                else:
                    return await async_translate_text(item, session=session)
            
            if names_to_translate:
                tasks = [process_translation(item, session) for item in names_to_translate]
                translated_texts = await asyncio.gather(*tasks)
                for idx, translated in zip(indices_to_translate, translated_texts):
                    processed_attractions[idx]["name"] = translated
            
            # --- Build final attractions list ---
            attractions = []
            for item in processed_attractions:
                element = item["element"]
                tags = element.get("tags", {})
                if element["type"] == "node":
                    lat = element.get("lat")
                    lon = element.get("lon")
                else:
                    center = element.get("center", {})
                    lat = center.get("lat")
                    lon = center.get("lon")
                attractions.append({
                    "osm_id": element.get("id"),
                    "type": element["type"],
                    "name": item["name"],
                    "tourism": tags.get("tourism") or tags.get("amenity"),
                    "city": city,
                    "state": state,
                    "country": country,
                    "lat": lat,
                    "lon": lon,
                    "tags": tags,
                })
            
            return Response(attractions, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='nearby-cities')
    def nearby_cities(self, request):
        """
        GET /api/itineraries/nearby-cities/?city=LosAngeles&radius=20

        This method:
          1) Uses Nominatim to get the latitude and longitude of the given city.
          2) Uses the Overpass API to find nearby cities (nodes with place=city)
             within the given radius (converted from miles to meters).
        """
        city = request.query_params.get("city", "").strip()
        radius = request.query_params.get("radius", "").strip()

        if not city or not radius:
            return Response({"error": "Both 'city' and 'radius' parameters are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            radius = float(radius)
        except ValueError:
            return Response({"error": "'radius' must be a valid number."},
                            status=status.HTTP_400_BAD_REQUEST)

        nominatim_url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "YourAppName/1.0 (https://example.com)"}
        search_params = {
            "q": city,
            "format": "json",
            "limit": 1
        }

        try:
            search_response = requests.get(nominatim_url, params=search_params, headers=headers)
            if search_response.status_code != 200:
                return Response({"error": "Error fetching city coordinates from Nominatim"},
                                status=search_response.status_code)
            results = search_response.json()
            if not results:
                return Response({"error": f"No results found for '{city}'."},
                                status=status.HTTP_404_NOT_FOUND)
            lat = results[0].get("lat")
            lon = results[0].get("lon")
        except requests.RequestException as e:
            return Response({"error": f"Nominatim request error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        radius_m = radius * 1609.34  # Convert miles to meters.
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node[place=city](around:{radius_m},{lat},{lon});
        );
        out;
        """
        try:
            overpass_response = requests.post(overpass_url, data=overpass_query.encode('utf-8'))
            if overpass_response.status_code != 200:
                return Response({"error": "Error fetching nearby cities from Overpass"},
                                status=overpass_response.status_code)
            overpass_data = overpass_response.json()
        except requests.RequestException as e:
            return Response({"error": f"Overpass request error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        nearby = []
        for element in overpass_data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name:en", tags.get("name", "")).strip()
            if not name or name.lower() == "unnamed":
                continue
            nearby.append({
                "osm_id": element.get("id"),
                "name": name,
                "lat": element.get("lat"),
                "lon": element.get("lon"),
                "distance": round(radius_m / 1609.34, 2)  # Echo the search radius in miles.
            })

        return Response(nearby, status=status.HTTP_200_OK)