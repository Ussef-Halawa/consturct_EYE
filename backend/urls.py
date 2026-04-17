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
    InjuryAlertCreateView,
    InjuryAlertRetrieveView,
    InactivityAlertCreateView,
    InactivityAlertRetrieveView,
)

urlpatterns = [
    path('cameras/', CameraCreateView.as_view(), name='camera-create'),
    path('cameras/retrieve/', CameraRetrieveView.as_view(), name='camera-retrieve-by-project'),
    path('cameras/<uuid:camera_id>/', CameraRetrieveView.as_view(), name='camera-retrieve-by-id'),
    path('cameras/<uuid:camera_id>/update/', CameraUpdateView.as_view(), name='camera-update'),
    path('cameras/<uuid:camera_id>/delete/', CameraDeleteView.as_view(), name='camera-delete'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('safety-violations/', SafetyViolationCreateView.as_view(), name='safety-violation-create'),
    path('safety-violations/retrieve/', SafetyViolationRetrieveView.as_view(), name='safety-violation-retrieve'),
    path('injury-alerts/', InjuryAlertCreateView.as_view(), name='injury-alert-create'),
    path('injury-alerts/retrieve/', InjuryAlertRetrieveView.as_view(), name='injury-alert-retrieve'),
    path('inactivity-alerts/', InactivityAlertCreateView.as_view(), name='inactivity-alert-create'),
    path('inactivity-alerts/retrieve/', InactivityAlertRetrieveView.as_view(), name='inactivity-alert-retrieve'),

]