import uuid
import random
import string
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


def generate_unique_project_code():
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
    max_attempts = 25

    for _ in range(max_attempts):
        code = ''.join(random.choices(alphabet, k=6))
        if not Project.objects.filter(project_code=code).exists():
            return code

    raise RuntimeError('Could not generate a unique project code after multiple attempts.')

class Project(models.Model):
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_code = models.CharField(max_length=6, unique=True, default=generate_unique_project_code, editable = False)
    project_name = models.CharField(max_length=255)
    location_address = models.TextField(blank=True, null=True)
    structural_design_storage_key = models.URLField(max_length=2048)
    architectural_design_storage_key = models.URLField(max_length=2048)
    start_date = models.DateField()

    def __str__(self):
        return self.project_name


class User(AbstractUser):
    ADMIN_ROLE = 'admin'
    ENGINEER_ROLE = 'engineer'
    OWNER_ROLE = 'owner'

    USER_ROLES = [
        (ADMIN_ROLE, 'Administrator'),
        (ENGINEER_ROLE, 'Supervise engineer'),
        (OWNER_ROLE, 'Property owner')
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=False, blank=False, unique = True)
    role = models.CharField(max_length=50, choices=USER_ROLES)

    def __str__(self):
        return self.username


class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'user'], name='unique_project_member')
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.project_name}"


class Camera(models.Model):
    camera_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    location_description = models.CharField(max_length=255, blank=True, null=True)
    stream_url = models.URLField(max_length=2048)


    def __str__(self):
        return f"{self.project.project_name} - {self.location_description}"


class SafetyViolation(models.Model):
    violation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    violation_type = models.CharField(max_length=100)
    evidence_storage_key = models.URLField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.violation_type} - {self.project.project_name}"


class InjuryAlert(models.Model):
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=100, blank=True, null=True)
    evidence_storage_key = models.URLField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.alert_type} - {self.project.project_name}"


class InactivityAlert(models.Model):
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Inactivity Alert - {self.project.project_name}"


class DailyProgressUpdate(models.Model):
    update_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add = True)


    def __str__(self):
        return f"{self.project.project_name} - {self.progress_percentage}%"


class Report(models.Model):
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50)
    storage_object_key = models.URLField(max_length=2048) 
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.report_type} - {self.project.project_name}"
