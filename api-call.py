import requests
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import import_requests

# ANSI escape codes for blue bold text and reset
BLUE_BOLD = "\033[1;34m"
RESET = "\033[0m"

def print_highlight(message):
    print(f"\n{BLUE_BOLD}{message}{RESET}")

# Authenticate and get the token
auth_url = "https://sc.mapplyia.com/api/v1/auths/signin"
auth_payload = {
    "email": "admin@mapply.com",
    "password": "11235813"
}

try:
    auth_response = requests.post(auth_url, json=auth_payload)
    auth_response.raise_for_status()  # Check if authentication fails
    token = auth_response.json().get("token")
    
    if not token:
        raise ValueError("Token not found in response")
    
    print_highlight(f"Authentication successful, Token: {token}")

    # Use this token in headers for subsequent requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

except requests.RequestException as e:
    print_highlight(f"Authentication request failed: {e}")
    sys.exit(1)
except ValueError as e:
    print_highlight(f"Authentication failed: {e}")
    sys.exit(1)

app = FastAPI()

class AuthRequest(BaseModel):
    email: str
    password: str

@app.post("/get-chats")
async def get_chats(auth_request: AuthRequest):
    try:
        # Update credentials dynamically
        import_requests.auth_payload["email"] = auth_request.email
        import_requests.auth_payload["password"] = auth_request.password

        # Execute the main logic from import_requests.py
        chats_data = import_requests.main()

        return chats_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))