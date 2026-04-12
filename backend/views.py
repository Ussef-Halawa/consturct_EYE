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


class CameraCreateView(APIView):
    """
    POST /api/cameras/
    Creates a new camera record linked to a project
    """
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SafetyViolationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
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
    permission_classes = [IsAuthenticated]

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
