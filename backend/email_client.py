# email_client.py
import requests
from datetime import datetime, timedelta, timezone

def get_inbox_messages(token: str, only_today=False):
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"

    if only_today:
        now = datetime.now(timezone.utc)
        start_of_today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        iso_start = start_of_today.strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"{base_url}?$filter=receivedDateTime ge {iso_start}"
    else:
        url = base_url

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["value"]


def move_message(token: str, message_id: str, destination_folder_id: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/move"
    response = requests.post(url, headers=headers, json={"destinationId": destination_folder_id})
    response.raise_for_status()
    return response.json()
