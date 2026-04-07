from rest_framework import serializers
from .models import Project
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['project_id', 'project_name', 'project_code', 'location_address', 'start_date', 'structural_design_storage_key', 'architectural_design_storage_key']