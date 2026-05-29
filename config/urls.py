"""
URL configuration for constructEYE project.
...
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT auth endpoints
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App endpoints
    path('api/', include('backend.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Debug toolbar
    path('__debug__/', include(debug_toolbar.urls)),
]