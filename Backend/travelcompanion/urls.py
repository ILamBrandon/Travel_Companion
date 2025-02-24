from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),          # User routes
    path('api/', include('main.urls')),                # Main app routes
]
