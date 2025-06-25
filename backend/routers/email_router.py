from fastapi import APIRouter,Depends
from email_client import get_inbox_messages, move_message
from parser import classify_email
from auth import get_access_token

email_router = APIRouter()

FOLDER_ID_MAP = {
    "HR": "AAMkAGUyMjVjMWY5LTFlOGMtNGJlNS04YmNjLWNmZDI1NTM3OTNkZQAuAAAAAABn5UtmIWzYQ6q37uBhv6j2AQABRWvI7SUXQI73tZ0jFZ4gAAEIkXEkAAA=",
    "Finance": "AAMkAGUyMjVjMWY5LTFlOGMtNGJlNS04YmNjLWNmZDI1NTM3OTNkZQAuAAAAAABn5UtmIWzYQ6q37uBhv6j2AQABRWvI7SUXQI73tZ0jFZ4gAAEIkXElAAA=",
    "Personal": "AAMkAGUyMjVjMWY5LTFlOGMtNGJlNS04YmNjLWNmZDI1NTM3OTNkZQAuAAAAAABn5UtmIWzYQ6q37uBhv6j2AQABRWvI7SUXQI73tZ0jFZ4gAAEIkXEmAAA=",
}

@email_router.get("/emails/process")
async def process_emails(token: str):
    messages = get_inbox_messages(token)
    moved = []

    for msg in messages:
        content = msg.get("subject", "") + "\n" + msg.get("bodyPreview", "")
        predicted_folder = classify_email(content)
        folder_id = FOLDER_ID_MAP.get(predicted_folder)
        if folder_id:
            try:
                move_message(token, msg["id"], folder_id)
                moved.append({"id": msg["id"], "moved_to": predicted_folder})
            except Exception as e:
                moved.append({"id": msg["id"], "moved_to": "Error", "error": str(e)})
        else:
            moved.append({"id": msg["id"], "moved_to": "Uncategorized"})

    return {"moved_emails": moved}

def get_latest_email_id(token: str) -> str | None:
    from email_client import get_inbox_messages
    messages = get_inbox_messages(token)
    if messages:
        return messages[0]["id"]
    return None

@email_router.get("/email-tags")
def get_email_tags(token: str = Depends(get_access_token)):
    import requests

    folder_map = {
        "HR": FOLDER_ID_MAP["HR"],
        "Finance": FOLDER_ID_MAP["Finance"],
        "Personal": FOLDER_ID_MAP["Personal"],
        "Inbox": "inbox",
    }

    tags = []
    headers = {"Authorization": f"Bearer {token}"}

    for label, folder_id in folder_map.items():
        url = f"https://graph.microsoft.com/v1.0/me/mailFolders/{folder_id}/messages?$top=50"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch from folder {label}: {response.text}")
            continue

        messages = response.json().get("value", [])
        for msg in messages:
            subject = msg.get("subject", "").strip()
            if not subject:
                continue

            tag = label if label != "Inbox" else "Other"

            tags.append({
                "subject": subject.lower().strip(),
                "tag": tag
            })

    return tags
