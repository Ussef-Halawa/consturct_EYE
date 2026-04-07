from django.urls import path
from . import views

# URL configuration
urlpatterns = [
    path('projects/', views.project_list)
]