from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ProjectSerializer
from .models import Project
# Create your views here.
# Views are request handlers.
@api_view()
def project_list(request):

        querySet = Project.objects.all()
        serializer = ProjectSerializer(querySet, many = True)
        return Response(serializer.data)