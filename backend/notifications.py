from firebase_admin import messaging
from .firebase import initialize_firebase

initialize_firebase()


def send_alert_to_engineers(project, alert_type: str, message: str, data: dict = None):
    """
    Sends FCM push notification ONLY to Engineers
    who are members of the given project.

    Owners do NOT receive notifications (per sequence diagrams).
    Admins do NOT receive notifications (they monitor from dashboard).

    Args:
        project: The Project model instance
        alert_type: Type of alert e.g. 'Safety Violation', 'Injury Alert'
        message: The notification message body
        data: Optional extra data to send with notification

    Returns:
        dict with success and failure counts
    """
    from .models import ProjectMember

    # ── Find all Engineers in this project ──
    engineer_members = ProjectMember.objects.filter(
        project=project,
        user__role='engineer'
    ).select_related('user')

    # ── Get their FCM tokens ─────────────────
    fcm_tokens = [
        member.user.fcm_token
        for member in engineer_members
        if member.user.fcm_token  # only if token exists
    ]

    if not fcm_tokens:
        # No engineers with FCM tokens found
        return {"success": 0, "failure": 0, "message": "No engineer tokens found"}

    # ── Build the notification ───────────────
    notification = messaging.Notification(
        title=f"🚨 ConstructEYE - {alert_type}",
        body=message,
    )

    # ── Extra data payload ───────────────────
    notification_data = {
        "alert_type": alert_type,
        "project_id": str(project.project_id),
        "project_name": project.project_name,
    }

    if data:
        notification_data.update({str(k): str(v) for k, v in data.items()})

    # ── Send to multiple devices ─────────────
    multicast_message = messaging.MulticastMessage(
        tokens=fcm_tokens,
        notification=notification,
        data=notification_data,
        android=messaging.AndroidConfig(
            priority='high',  # ensures immediate delivery
            notification=messaging.AndroidNotification(
                sound='default',
                priority='high',
            )
        ),
        apns=messaging.APNSConfig(  # iOS config
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    sound='default',
                    badge=1,
                )
            )
        )
    )

    response = messaging.send_each_for_multicast(multicast_message)

    return {
        "success": response.success_count,
        "failure": response.failure_count,
        "total_engineers": len(fcm_tokens)
    }


def send_safety_violation_notification(project, camera, violation_type: str):
    """
    Sends notification when a safety violation is detected.
    Called from SafetyViolationCreateView after saving.
    """
    return send_alert_to_engineers(
        project=project,
        alert_type="Safety Violation",
        message=f"Safety violation detected: {violation_type} at {camera.location_description}",
        data={
            "camera_id": str(camera.camera_id),
            "violation_type": violation_type,
        }
    )


def send_injury_alert_notification(project, camera, alert_type: str):
    """
    Sends notification when an injury is detected.
    Called from InjuryAlertCreateView after saving.
    """
    return send_alert_to_engineers(
        project=project,
        alert_type="Injury Alert",
        message=f"Injury detected: {alert_type} at {camera.location_description}",
        data={
            "camera_id": str(camera.camera_id),
            "alert_type": alert_type,
        }
    )


def send_inactivity_alert_notification(project, camera):
    """
    Sends notification when worker inactivity is detected.
    Called from InactivityAlertCreateView after saving.
    """
    return send_alert_to_engineers(
        project=project,
        alert_type="Inactivity Alert",
        message=f"Worker inactivity detected at {camera.location_description}",
        data={
            "camera_id": str(camera.camera_id),
        }
    )