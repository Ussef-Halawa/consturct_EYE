from django.urls import path
from . import views

urlpatterns = [
    path('cameras/', views.CameraCreateView.as_view(), name='camera-create'),
    path('cameras/retrieve/', views.CameraRetrieveView.as_view(), name='camera-retrieve-by-project'),
    path('cameras/<uuid:camera_id>/', views.CameraRetrieveView.as_view(), name='camera-retrieve-by-id'),
    path('cameras/<uuid:camera_id>/update/', views.CameraUpdateView.as_view(), name='camera-update'),
    path('cameras/<uuid:camera_id>/delete/', views.CameraDeleteView.as_view(), name='camera-delete'),
    path('safety-violations/', views.SafetyViolationCreateView.as_view(), name='safety-violation-create'),
    path('safety-violations/retrieve/', views.SafetyViolationRetrieveView.as_view(), name='safety-violation-retrieve'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.UserLoginView.as_view(), name='user-login'),
    path('projects/', views.ProjectList.as_view()),
    path('projects/<uuid:project_id>/', views.ProjectDetails.as_view()),
    path('progress/<uuid:project_id>/', views.ProgressUpdate.as_view())
]