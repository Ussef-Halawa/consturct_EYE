import firebase_admin
from firebase_admin import credentials, storage, messaging
from django.conf import settings
import os

# ─────────────────────────────────────────
# Initialize Firebase App (only once)
# ─────────────────────────────────────────

def initialize_firebase():
    """
    Initialize Firebase Admin SDK.
    Called once when Django starts.
    Uses the service account JSON file for authentication.
    """
    if not firebase_admin._apps:
        # Path to your service account JSON file
        cred_path = os.path.join(
            settings.BASE_DIR,
            'firebase-service-account.json'
        )

        cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred, {
            'storageBucket': settings.FIREBASE_STORAGE_BUCKET
        })

# Initialize when this module is imported
initialize_firebase()