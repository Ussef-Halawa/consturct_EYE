"""
URL configuration for constructEYE project.
...
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT auth endpoints
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App endpoints
    path('api/', include('backend.urls')),

    # Debug toolbar
    path('__debug__/', include(debug_toolbar.urls)),
]