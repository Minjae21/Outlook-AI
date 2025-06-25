# parser.py
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()

openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-03-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

docintel_client = DocumentAnalysisClient(
    endpoint=os.getenv("AZURE_DOC_INTEL_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_DOC_INTEL_KEY"))
)

def classify_email(content: str) -> str:
    prompt = f"""
Classify the following email into one of the following folders:
HR, Finance, Spam, Personal, Meetings.

Email:
\"\"\"
{content}
\"\"\"
Respond with only the folder name.
"""
    try:
        completion = openai_client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant working for Country Financial. "
                        "You specialize in understanding internal Outlook emails and classifying them into predefined folders. "
                        "Always choose the most appropriate folder based on the email content."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=50
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("[ERROR] Azure OpenAI classification failed:", e)
        return "Uncategorized"
