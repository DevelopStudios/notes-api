"""
URL configurations
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView, #For getting JWT tokens
    TokenRefreshView    #For refreshing JWT tokens
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('notes.urls')),
    #JWT Authentication Endpoints
    path('api/token/',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
