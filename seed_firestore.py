# Copyright 2026 Google LLC
# Seed script for Firestore knowledge_base collection.

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-411423280d35"

SEED_ARTICLES = [
    {
        "id": "KB-101",
        "title": "VPN Connection Error & Network Timeout",
        "category": "Network",
        "error_code": "ERR_VPN_TIMEOUT",
        "symptoms": "User cannot connect to corporate VPN or loses connection after 30 seconds.",
        "resolution_steps": "1. Verify Internet connection. 2. Restart GlobalProtect/Cisco AnyConnect client. 3. Flush DNS cache via ipconfig /flushdns. 4. Reset network adapter.",
        "severity": "Medium",
    },
    {
        "id": "KB-102",
        "title": "Blue Screen BSOD 0x0000007E",
        "category": "OS & Hardware",
        "error_code": "BSOD_0x0000007E",
        "symptoms": "Windows crashes randomly with SYSTEM_THREAD_EXCEPTION_NOT_HANDLED error.",
        "resolution_steps": "1. Boot into Safe Mode. 2. Update display and graphics drivers. 3. Run sfc /scannow in Admin Command Prompt. 4. Check memory health using Windows Memory Diagnostic.",
        "severity": "High",
    },
    {
        "id": "KB-103",
        "title": "Disk Full & Storage Clean Up",
        "category": "Storage",
        "error_code": "STORAGE_DISK_FULL",
        "symptoms": "Low disk space warning on C: drive, system running slow and applications freezing.",
        "resolution_steps": "1. Run Disk Cleanup (cleanmgr.exe). 2. Delete temporary files in %temp%. 3. Empty Recycle Bin. 4. Relocate large downloads or media files to Cloud Storage.",
        "severity": "Low",
    },
    {
        "id": "KB-104",
        "title": "SSO & Password Expiration Reset",
        "category": "Security & Identity",
        "error_code": "AUTH_PASSWORD_EXPIRED",
        "symptoms": "User locked out of corporate portal or email due to expired credentials.",
        "resolution_steps": "1. Visit the self-service password reset portal at sso.company.com/reset. 2. Verify identity via MFA SMS or Authenticator App. 3. Create a new password and update credentials.",
        "severity": "Medium",
    },
]


def seed_firestore():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("knowledge_base")

    print(f"Seeding Firestore collection 'knowledge_base' in project '{PROJECT_ID}'...")
    for article in SEED_ARTICLES:
        doc_ref = collection_ref.document(article["id"])
        doc_ref.set(article)
        print(f"  - Added/Updated document {article['id']}: {article['title']}")

    print("Firestore seeding complete!")


if __name__ == "__main__":
    seed_firestore()
