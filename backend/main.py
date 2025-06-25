import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from msal import ConfidentialClientApplication
from routers.email_router import email_router, get_latest_email_id, process_emails
from dotenv import load_dotenv
from auth import token_cache, get_access_token
from chatbot import chatbot_router

load_dotenv()

app = FastAPI()
app.include_router(email_router, prefix="/api/email")
app.include_router(chatbot_router, prefix="/api/chat")

# CORS Config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:8000/redirect"

SCOPE = ["Mail.ReadWrite", "User.Read"]

msal_app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=AUTHORITY,
)

last_processed_email_id = None

@app.get("/")
def root():
    return {"message": "Welcome to Outlook Chatbot API. Go to /login to authenticate."}

@app.get("/login")
def login():
    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI,
    )
    return RedirectResponse(auth_url)

@app.get("/redirect")
def oauth_redirect(request: Request):
    code = request.query_params.get("code")
    if not code:
        error = request.query_params.get("error")
        error_desc = request.query_params.get("error_description")
        return HTMLResponse(f"Error: {error}<br>Description: {error_desc}")

    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI,
    )

    if "access_token" in result:
        token_cache["access_token"] = result["access_token"]
        return HTMLResponse("Authentication completed. You can close this window now.")
    else:
        return HTMLResponse(f"Failed to get token: {result.get('error_description')}")

async def periodic_email_processing():
    global last_processed_email_id
    while True:
        print("Checking for new emails before processing...")
        try:
            token = get_access_token()
            latest_id = get_latest_email_id(token)
            if latest_id != last_processed_email_id:
                print("New email detected. Running processing...")
                await process_emails(token)
                last_processed_email_id = latest_id
            else:
                print("No new emails. Skipping processing.")
        except Exception as e:
            print(f"Error in periodic processing: {e}")
        await asyncio.sleep(10)  # 5 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_email_processing())
