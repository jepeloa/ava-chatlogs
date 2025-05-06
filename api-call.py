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