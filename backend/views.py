from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Camera, Project
from .serializers import CameraSerializer, CameraUpdateSerializer
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.permissions import AllowAny
from .models import SafetyViolation
from .serializers import SafetyViolationSerializer
from .models import InjuryAlert
from .serializers import InjuryAlertSerializer
from .models import InactivityAlert
from .serializers import InactivityAlertSerializer
from .permissions import (
    IsAdmin,
    IsProjectMember,
    IsAdminOrProjectMember,
    IsEngineerOrAdmin,
    IsDeviceUser,
    IsProjectOwner,
    IsProjectEngineer,
)
from .notifications import (
    send_safety_violation_notification,
    send_injury_alert_notification,
    send_inactivity_alert_notification,
)

class CameraCreateView(APIView):
    """
    POST /api/cameras/
    Creates a new camera record linked to a project
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Authentication'],
        summary='Register a new user',
        description='Creates a new user account with username, email, password and role.',
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
    )

    def post(self, request):
        serializer = CameraSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Camera created successfully.",
                    "camera": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "message": "Invalid data.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class CameraRetrieveView(APIView):
    """
    GET /api/cameras/<camera_id>/        --> retrieve single camera by its ID
    GET /api/cameras/?project_id=<uuid>  --> retrieve all cameras for a project
    
    Both formats are handled in one view because they both 
    represent "reading camera data"
    """
    permission_classes = [IsAdminOrProjectMember]

    @extend_schema(
        tags=['Cameras'],
        summary='Retrieve camera(s)',
        description='Get a single camera by ID, or all cameras for a project using ?project_id=',
        parameters=[
            OpenApiParameter(name='project_id', description='Filter by project UUID', required=False, type=str),
        ],
        responses={200: CameraSerializer},
    )

    def get(self, request, camera_id=None):

        # Retrieve by camera_id (URL parameter)
        if camera_id:
            camera = get_object_or_404(Camera, camera_id=camera_id)
            serializer = CameraSerializer(camera)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Retrieve by project_id (query parameter)
        project_id = request.query_params.get('project_id')

        if project_id:
            # Verify the project actually exists first
            get_object_or_404(Project, project_id=project_id)
            cameras = Camera.objects.filter(project__project_id=project_id)
            serializer = CameraSerializer(cameras, many=True)
            return Response(
                {
                    "project_id": project_id,
                    "count": cameras.count(),
                    "cameras": serializer.data
                },
                status=status.HTTP_200_OK
            )

        # Neither provided
        return Response(
            {"message": "Provide either a camera_id in the URL or a project_id query parameter."},
            status=status.HTTP_400_BAD_REQUEST
        )


class CameraUpdateView(APIView):
    """
    PATCH /api/cameras/<camera_id>/update/
    Updates a single field on a camera
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Cameras'],
        summary='Update a camera field',
        description='Admin only. Updates a single field on a camera.',
        request=CameraUpdateSerializer,
    )

    def patch(self, request, camera_id):
        camera = get_object_or_404(Camera, camera_id=camera_id)
        serializer = CameraUpdateSerializer(data=request.data)

        if serializer.is_valid():
            field = serializer.validated_data['field']
            value = serializer.validated_data['value']

            # Dynamically set the field and save
            setattr(camera, field, value)
            camera.save(update_fields=[field])  # only hit DB for this one field

            return Response(
                {
                    "message": f"Camera '{field}' updated successfully.",
                    "camera_id": str(camera.camera_id),
                    "updated_field": field,
                    "new_value": value
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Invalid update data.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class CameraDeleteView(APIView):
    """
    DELETE /api/cameras/<camera_id>/delete/
    Permanently deletes a camera record by its ID
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Cameras'],
        summary='Delete a camera',
        description='Admin only. Permanently deletes a camera record.',
    )

    def delete(self, request, camera_id):
        camera = get_object_or_404(Camera, camera_id=camera_id)
        camera_info = str(camera)  # capture before deletion for the response log
        camera.delete()

        return Response(
            {"message": f"Camera '{camera_info}' deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )


class UserRegistrationView(APIView):
    """
    POST /api/auth/register/
    Registers a new user
    No authentication required — anyone can register
    """
    permission_classes = [AllowAny]  # No token needed to register

    @extend_schema(
        tags=['Authentication'],
        summary='Register a new user',
        description='Creates a new user account with username, email, password and role.',
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
    )

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "user_id": str(user.user_id),
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "message": "Registration failed.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLoginView(APIView):
    """
    POST /api/auth/login/email/
    Authenticates user by email + password
    Returns JWT access and refresh tokens
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Authentication'],
        summary='Login with email and password',
        description='Authenticates user and returns JWT access and refresh tokens.',
        request=UserLoginSerializer,
        responses={200: UserLoginSerializer},
    )

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                {
                    "message": "Login successful.",
                    "data": serializer.validated_data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Login failed.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    


class SafetyViolationCreateView(APIView):
    """
    POST /api/safety-violations/
    Creates a new safety violation record
    This will be called by the Raspberry Pi / AI model when it detects a violation on site
    """
    permission_classes = [IsDeviceUser]

    @extend_schema(
        tags=['Safety Violations'],
        summary='Record a safety violation',
        description='Raspberry Pi only (API key auth). Records a detected safety violation.',
        request=SafetyViolationSerializer,
        responses={201: SafetyViolationSerializer},
    )

    def post(self, request):
        serializer = SafetyViolationSerializer(data=request.data)

        if serializer.is_valid():
            violation = serializer.save()  # ← change from serializer.save() to violation = serializer.save()

        # ── Send FCM notification to Engineers ──
            try:
                send_safety_violation_notification(
                    project=violation.project,
                    camera=violation.camera,
                    violation_type=violation.violation_type
                )
            except Exception as e:
                print(f"FCM notification error: {e}")

            return Response(
            {
                "message": "Safety violation recorded successfully.",
                "violation": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        return Response(
        {
            "message": "Invalid data.",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


class SafetyViolationRetrieveView(APIView):
    """
    GET /api/safety-violations/?project_id=<uuid>
    Retrieves all safety violations for a specific project
    Supports optional filtering by violation_type
    """
    permission_classes = [IsAdminOrProjectMember]

    @extend_schema(
        tags=['Safety Violations'],
        summary='Get safety violations by project',
        description='Returns all safety violations for a project. Filter by violation_type optionally.',
        parameters=[
            OpenApiParameter(name='project_id', description='Project UUID', required=True, type=str),
            OpenApiParameter(name='violation_type', description='Filter by type', required=False, type=str),
        ],
        responses={200: SafetyViolationSerializer(many=True)},
    )

    def get(self, request):
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {"message": "project_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify project exists
        get_object_or_404(Project, project_id=project_id)

        violations = SafetyViolation.objects.filter(
            project__project_id=project_id
        ).order_by('-created_at')  # newest first

        # Optional filter by violation type
        violation_type = request.query_params.get('violation_type')
        if violation_type:
            violations = violations.filter(violation_type=violation_type)

        serializer = SafetyViolationSerializer(violations, many=True)

        return Response(
            {
                "project_id": project_id,
                "count": violations.count(),
                "violations": serializer.data
            },
            status=status.HTTP_200_OK
        )
    



class InjuryAlertCreateView(APIView):
    """
    POST /api/injury-alerts/
    Creates a new injury alert record.
    Called by the Raspberry Pi / AI model when it detects a potential injury on site.
    """
    permission_classes = [IsDeviceUser]

    @extend_schema(
        tags=['Injury Alerts'],
        summary='Record an injury alert',
        description='Raspberry Pi only (API key auth). Records a detected injury.',
        request=InjuryAlertSerializer,
        responses={201: InjuryAlertSerializer},
    )

    def post(self, request):
        serializer = InjuryAlertSerializer(data=request.data)

        if serializer.is_valid():
            alert = serializer.save()  # ← change to alert = serializer.save()

        # ── Send FCM notification to Engineers ──
            try:
                send_injury_alert_notification(
                    project=alert.project,
                    camera=alert.camera,
                    alert_type=alert.alert_type or "Unknown"
            )
            except Exception as e:
                print(f"FCM notification error: {e}")

            return Response(
            {
                    "message": "Injury alert recorded successfully.",
                    "alert": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        return Response(
        {
            "message": "Invalid data.",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


class InjuryAlertRetrieveView(APIView):
    """
    GET /api/injury-alerts/?project_id=<uuid>
    Retrieves all injury alerts for a specific project.
    Supports optional filtering by alert_type.
    Examples:
    GET /api/injury-alerts/?project_id=<uuid>
    GET /api/injury-alerts/?project_id=<uuid>&alert_type=Fall detected
    """
    permission_classes = [IsAdminOrProjectMember]

    @extend_schema(
        tags=['Injury Alerts'],
        summary='Get injury alerts by project',
        description='Returns all injury alerts for a project.',
        parameters=[
            OpenApiParameter(name='project_id', description='Project UUID', required=True, type=str),
        ],
        responses={200: InjuryAlertSerializer(many=True)},
    )

    def get(self, request):
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {"message": "project_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify project exists
        get_object_or_404(Project, project_id=project_id)

        alerts = InjuryAlert.objects.filter(
            project__project_id=project_id
        ).order_by('-created_at')  # newest first

        # Optional filter by alert type
        alert_type = request.query_params.get('alert_type')
        if alert_type:
            alerts = alerts.filter(alert_type=alert_type)

        serializer = InjuryAlertSerializer(alerts, many=True)

        return Response(
            {
                "project_id": project_id,
                "count": alerts.count(),
                "alerts": serializer.data
            },
            status=status.HTTP_200_OK
        )
    




class InactivityAlertCreateView(APIView):
    """
    POST /api/inactivity-alerts/
    Creates a new inactivity alert record.
    Called by the Raspberry Pi / AI model when it detects no movement or work activity on site.
    """
    permission_classes = [IsDeviceUser]

    @extend_schema(
        tags=['Inactivity Alerts'],
        summary='Record an inactivity alert',
        description='Raspberry Pi only (API key auth). Records detected worker inactivity.',
        request=InactivityAlertSerializer,
        responses={201: InactivityAlertSerializer},
    )

    

    def post(self, request):
        serializer = InactivityAlertSerializer(data=request.data)

        if serializer.is_valid():
            alert = serializer.save()

            try:
                send_inactivity_alert_notification(
                    project=alert.project,
                    camera=alert.camera,
            )
            except Exception as e:
                print(f"FCM notification error: {e}")

            return Response(
            {
                    "message": "Inactivity alert recorded successfully.",
                    "alert": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        return Response(
        {
            "message": "Invalid data.",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )





class InactivityAlertRetrieveView(APIView):
    """
    GET /api/inactivity-alerts/?project_id=<uuid>
    Retrieves all inactivity alerts for a specific project.
    Supports optional date filtering.
    Examples:
    GET /api/inactivity-alerts/?project_id=<uuid>
    GET /api/inactivity-alerts/?project_id=<uuid>&date=2026-04-11
    """
    permission_classes = [IsAdminOrProjectMember]

    @extend_schema(
        tags=['Inactivity Alerts'],
        summary='Get inactivity alerts by project',
        description='Returns all inactivity alerts for a project.',
        parameters=[
            OpenApiParameter(name='project_id', description='Project UUID', required=True, type=str),
        ],
        responses={200: InactivityAlertSerializer(many=True)},
    )

    def get(self, request):
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {"message": "project_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify project exists
        get_object_or_404(Project, project_id=project_id)

        alerts = InactivityAlert.objects.filter(
            project__project_id=project_id
        ).order_by('-created_at')  # newest first

        # Optional filter by date
        date = request.query_params.get('date')
        if date:
            alerts = alerts.filter(created_at__date=date)

        serializer = InactivityAlertSerializer(alerts, many=True)

        return Response(
            {
                "project_id": project_id,
                "count": alerts.count(),
                "alerts": serializer.data
            },
            status=status.HTTP_200_OK
        )
    


from .models import DailyProgressUpdate
from .serializers import DailyProgressUpdateSerializer


class DailyProgressUpdateCreateView(APIView):
    """
    POST /api/progress-updates/
    Creates a new daily progress update record.
    Called by the AI model after analyzing the
    current construction state vs the design plans.

    Request body:
    {
        "project": "<project_uuid>",
        "progress_percentage": 35.50,
        "details": {"completed_floors": 3, "pending_tasks": ["roofing"]},
        "created_at": "2026-04-11"
    }
    """
    permission_classes = [IsDeviceUser]

    @extend_schema(
        tags=['Progress Updates'],
        summary='Record a progress update',
        description='Raspberry Pi only. Records daily construction progress percentage.',
        request=DailyProgressUpdateSerializer,
        responses={201: DailyProgressUpdateSerializer},
    )

    def post(self, request):
        serializer = DailyProgressUpdateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Progress update recorded successfully.",
                    "update": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "message": "Invalid data.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class DailyProgressUpdateRetrieveView(APIView):
    """
    GET /api/progress-updates/latest/?project_id=<uuid>
    Retrieves the LATEST progress update for a project.
    This is what the engineer/owner dashboard will call
    to show the most recent construction progress.

    GET /api/progress-updates/?project_id=<uuid>
    Retrieves ALL progress updates for a project (full history).
    """
    permission_classes = [IsAdminOrProjectMember]

    @extend_schema(
        tags=['Progress Updates'],
        summary='Get progress updates',
        description='Returns latest or full history of progress updates for a project.',
        parameters=[
            OpenApiParameter(name='project_id', description='Project UUID', required=True, type=str),
        ],
        responses={200: DailyProgressUpdateSerializer},
    )

    def get(self, request):
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {"message": "project_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify project exists
        get_object_or_404(Project, project_id=project_id)

        updates = DailyProgressUpdate.objects.filter(
            project__project_id=project_id
        ).order_by('-created_at')  # newest first

        # Return only the latest update
        latest = updates.first()

        if not latest:
            return Response(
                {
                    "project_id": project_id,
                    "message": "No progress updates found for this project."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DailyProgressUpdateSerializer(latest)

        return Response(
            {
                "project_id": project_id,
                "latest_update": serializer.data
            },
            status=status.HTTP_200_OK
        )





from .models import ProjectMember
from .serializers import ProjectJoinSerializer, ProjectMemberSerializer


class ProjectJoinView(APIView):
    """
    POST /api/projects/join/
    Allows an engineer or owner to join a project using its 6-character code.

    Rules:
    - Admin does NOT join projects (they have implicit access to all)
    - Cannot join the same project twice
    - Project code must be valid

    Request body:
    {
        "project_code": "CON001"
    }
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Project Members'],
        summary='Join a project',
        description='Engineer or Admin joins a project using its 6-character code.',
        request=ProjectJoinSerializer,
    )

    def post(self, request):
        # Admin cannot join projects
        if request.user.role == 'admin':
            return Response(
                {"message": "Admins have implicit access to all projects and cannot join."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProjectJoinSerializer(data=request.data)

        if serializer.is_valid():
            project_code = serializer.validated_data['project_code']
            project = serializer.get_project(project_code)

            # Check if user is already a member
            already_member = ProjectMember.objects.filter(
                project=project,
                user=request.user
            ).exists()

            if already_member:
                return Response(
                    {"message": "You are already a member of this project."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the ProjectMember record
            ProjectMember.objects.create(
                project=project,
                user=request.user
            )

            return Response(
                {
                    "message": f"Successfully joined project '{project.project_name}'.",
                    "project": {
                        "project_id": str(project.project_id),
                        "project_name": project.project_name,
                        "project_code": project.project_code,
                        "location_address": project.location_address,
                        "start_date": str(project.start_date),
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "message": "Invalid data.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ProjectMembersListView(APIView):
    """
    GET /api/projects/<project_id>/members/
    Returns a list of all members for a specific project.
    Any authenticated user can view project members.
    """
    permission_classes = [IsAdminOrProjectMember]

    @extend_schema(
        tags=['Project Members'],
        summary='List project members',
        description='Returns all members of a specific project.',
        responses={200: ProjectMemberSerializer(many=True)},
    )

    def get(self, request, project_id):
        # Verify project exists
        project = get_object_or_404(Project, project_id=project_id)

        members = ProjectMember.objects.filter(
            project=project
        ).select_related('user')  # optimizes DB query

        serializer = ProjectMemberSerializer(members, many=True)

        return Response(
            {
                "project_id": str(project_id),
                "project_name": project.project_name,
                "count": members.count(),
                "members": serializer.data
            },
            status=status.HTTP_200_OK
        )


class ProjectMemberDeleteView(APIView):
    """
    DELETE /api/projects/<project_id>/members/<user_id>/
    Removes a member from a project.
    Only admins can remove members.
    """
    permission_classes = [IsAdmin]

    @extend_schema(
        tags=['Project Members'],
        summary='Remove a project member',
        description='Admin only. Removes a user from a project.',
    )

    def delete(self, request, project_id, user_id):
        # Only admin can remove members
        if request.user.role != 'admin':
            return Response(
                {"message": "Only admins can remove project members."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verify project exists
        project = get_object_or_404(Project, project_id=project_id)

        # Verify member exists in this project
        member = ProjectMember.objects.filter(
            project=project,
            user__user_id=user_id
        ).first()

        if not member:
            return Response(
                {"message": "This user is not a member of this project."},
                status=status.HTTP_404_NOT_FOUND
            )

        member.delete()

        return Response(
            {"message": "Member removed from project successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    



class FCMTokenUpdateView(APIView):
    """
    POST /api/users/fcm-token/
    Saves the user's FCM token for push notifications.
    Called by Flutter app after login.

    Request body:
    {
        "fcm_token": "device_token_from_firebase_sdk"
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)

        if serializer.is_valid():
            request.user.fcm_token = serializer.validated_data['fcm_token']
            request.user.save(update_fields=['fcm_token'])

            return Response(
                {"message": "FCM token updated successfully."},
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "message": "Invalid data.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    