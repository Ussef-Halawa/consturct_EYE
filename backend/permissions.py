from rest_framework.permissions import BasePermission
from .models import ProjectMember


class IsAdmin(BasePermission):
    """
    Allows access only to users with role = 'admin'.
    Used for:
    - Creating projects
    - Managing cameras
    - Removing project members
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsProjectMember(BasePermission):
    """
    Allows access if the user is a member of the project
    OR if the user is an admin (implicit access to all projects).

    Admin does NOT join projects via ProjectMember record —
    they have implicit access to everything.

    Used for:
    - Viewing project data
    - Viewing camera streams
    - Viewing reports
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has implicit access to all projects
        if request.user.role == 'admin':
            return True

        # For engineers and owners — check ProjectMember record
        project_id = (
            view.kwargs.get('project_id') or
            request.data.get('project') or
            request.query_params.get('project_id')
        )

        if not project_id:
            return False

        return ProjectMember.objects.filter(
            project__project_id=project_id,
            user=request.user
        ).exists()


class IsAdminOrProjectMember(BasePermission):
    """
    Allows access if:
    - User is admin (implicit access to all) OR
    - User is a verified project member

    This is the MOST COMMON permission in the system.
    Used for most read/write operations on project data.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin always passes
        if request.user.role == 'admin':
            return True

        # Check if user is a project member
        project_id = (
            view.kwargs.get('project_id') or
            request.data.get('project') or
            request.query_params.get('project_id')
        )

        if not project_id:
            return False

        return ProjectMember.objects.filter(
            project__project_id=project_id,
            user=request.user
        ).exists()


class IsEngineerOrAdmin(BasePermission):
    """
    Allows access only to engineers or admins.
    Owners are excluded from this permission.

    Used for:
    - Operations that require technical knowledge
    - Viewing detailed AI analysis data
    - Receiving alert notifications from AI system
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'engineer']
        )


class IsDeviceUser(BasePermission):
    """
    Permission class for Raspberry Pi endpoints.
    The Pi authenticates using an API key passed in the request header.

    Used for:
    - Creating safety violation records
    - Creating injury alert records
    - Creating inactivity alert records
    - Sending progress updates

    The Pi sends: X-Device-API-Key: <key> in the request header.
    The key is stored in Django settings as DEVICE_API_KEY.
    """
    def has_permission(self, request, view):
        from django.conf import settings

        api_key = request.headers.get('X-Device-API-Key')

        if not api_key:
            return False

        return api_key == getattr(settings, 'DEVICE_API_KEY', None)


class IsProjectOwner(BasePermission):
    """
    Allows access only to users with role = 'owner'
    who are members of the project.

    Used for:
    - Owner-specific dashboard access
    - Viewing project reports (read-only)
    - Monitoring live camera feeds
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role != 'owner':
            return False

        project_id = (
            view.kwargs.get('project_id') or
            request.data.get('project') or
            request.query_params.get('project_id')
        )

        if not project_id:
            return False

        return ProjectMember.objects.filter(
            project__project_id=project_id,
            user=request.user
        ).exists()


class IsProjectEngineer(BasePermission):
    """
    Allows access only to users with role = 'engineer'
    who are members of the project.

    Used for:
    - Engineer-specific dashboard access
    - Viewing detailed progress data
    - Managing tasks and assignments
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role != 'engineer':
            return False

        project_id = (
            view.kwargs.get('project_id') or
            request.data.get('project') or
            request.query_params.get('project_id')
        )

        if not project_id:
            return False

        return ProjectMember.objects.filter(
            project__project_id=project_id,
            user=request.user
        ).exists()