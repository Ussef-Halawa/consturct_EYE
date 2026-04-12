from django.urls import path
from .views import (
    CameraCreateView,
    CameraRetrieveView,
    CameraUpdateView,
    CameraDeleteView,
    UserRegistrationView,
    UserLoginView,
    SafetyViolationCreateView,
    SafetyViolationRetrieveView,
)

urlpatterns = [
    path('projects/', views.project_list)
    path('cameras/', CameraCreateView.as_view(), name='camera-create'),
    path('cameras/retrieve/', CameraRetrieveView.as_view(), name='camera-retrieve-by-project'),
    path('cameras/<uuid:camera_id>/', CameraRetrieveView.as_view(), name='camera-retrieve-by-id'),
    path('cameras/<uuid:camera_id>/update/', CameraUpdateView.as_view(), name='camera-update'),
    path('cameras/<uuid:camera_id>/delete/', CameraDeleteView.as_view(), name='camera-delete'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('safety-violations/', SafetyViolationCreateView.as_view(), name='safety-violation-create'),
    path('safety-violations/retrieve/', SafetyViolationRetrieveView.as_view(), name='safety-violation-retrieve'),
]