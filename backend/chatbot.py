from fastapi import APIRouter
from pydantic import BaseModel
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import traceback
from datetime import datetime, timedelta

from auth import get_access_token
from email_client import get_inbox_messages

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-03-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

chatbot_router = APIRouter()

class Message(BaseModel):
    message: str

def summarize_todays_emails(token: str) -> str:
    try:
        messages = get_inbox_messages(token, only_today=True)
        today = datetime.utcnow().date()
        todays_emails = []

        for msg in messages:
            received = msg.get("receivedDateTime", "")
            if received:
                msg_date = datetime.fromisoformat(received.rstrip("Z")).date()
                if msg_date == today:
                    subject = msg.get("subject", "No Subject")
                    preview = msg.get("bodyPreview", "")
                    sender = msg.get("from", {}).get("emailAddress", {}).get("name", "Unknown Sender")
                    todays_emails.append(f"From: {sender}\nSubject: {subject}\nPreview: {preview}\n")

        if not todays_emails:
            return "You have no emails today."

        combined = "\n---\n".join(todays_emails[:5])  # limit to 5 emails
        return f"Here are your emails from today:\n{combined}"
    except Exception as e:
        return f"Error summarizing today's emails: {e}"

@chatbot_router.post("")
async def chat(data: Message):
    try:
        user_message = data.message.lower()
        deployment_name = os.getenv("DEPLOYMENT_NAME")
        token = get_access_token()

        if "summarize" in user_message and "email" in user_message:
            summary = summarize_todays_emails(token)
            return {"response": summary}

        completion = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": data.message}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return {"response": completion.choices[0].message.content}

    except Exception as e:
        print("Azure OpenAI error:", e)
        traceback.print_exc()
        return {"response": f"Sorry, something went wrong: {str(e)}"}
