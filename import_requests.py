import requests
import sys
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the host URL from the environment variables
HOST_URL = os.getenv("HOST_URL")

# ANSI escape codes for blue bold text and reset
BLUE_BOLD = "\033[1;34m"
RESET = "\033[0m"

def print_highlight(message):
    print(f"\n{BLUE_BOLD}{message}{RESET}")

# Authenticate and get the token
auth_url = f"{HOST_URL}/api/v1/auths/signin"
auth_payload = {
    "email": "mail",
    "password": "password"
}

def main():
    try:
        # Validate the email and password before making the request
        if not auth_payload.get("email") or not auth_payload.get("password"):
            raise ValueError("Email or password is missing in the authentication payload")

        # Step 1: Authenticate and get the token
        try:
            auth_response = requests.post(auth_url, json=auth_payload)
            if auth_response.status_code != 200:
                print_highlight(f"Authentication failed with status {auth_response.status_code}: {auth_response.text}")
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
            print_highlight(f"Response content: {auth_response.text if 'auth_response' in locals() else 'No response'}")
            sys.exit(1)
        except ValueError as e:
            print_highlight(f"Authentication failed: {e}")
            sys.exit(1)

        # Step 2: Make the request to get chats
        chats_url = f"{HOST_URL}/api/v1/chats/all/db"
        chats_response = requests.get(chats_url, headers=headers)
        chats_response.raise_for_status()  # Check if the request fails
        chats_data = chats_response.json()
        print(chats_data)

        # Step 3: Make the request to get user ID
        user_id_url = f"{HOST_URL}/api/v1/users/?skip=0&limit=50"
        user_id_response = requests.get(user_id_url, headers=headers)
        user_id_response.raise_for_status()  # Check if the request fails
        user_data = user_id_response.json()

        # Extract user IDs and other relevant information from the list
        users_info = []
        for user in user_data:
            users_info.append({
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email"),
                "role": user.get("role")
            })

        if not users_info:
            raise ValueError("No users found in response")

        # Ensure chats_data is a dictionary before adding users
        if isinstance(chats_data, list):
            chats_data = {"chats": chats_data}  # Convert list to dictionary with a key "chats"

        # Filtrar chats para incluir solo el nombre de usuario y history (solo mensajes)
        filtered_chats = []
        # Crear un diccionario para mapear user_id a nombre
        user_id_to_name = {user["id"]: user["name"] for user in users_info}
        for chat in chats_data.get("chats", []):
            filtered_history = {
                "messages": {}
            }
            for message_id, message in chat.get("chat", {}).get("history", {}).get("messages", {}).items():
                if message.get("role") in ["user", "assistant"]:
                    filtered_history["messages"][message_id] = {
                        "role": message.get("role"),
                        "content": message.get("content"),
                        "date": message.get("timestamp") if message.get("timestamp") else None
                    }

            if filtered_history["messages"]:
                user_name = user_id_to_name.get(chat.get("user_id"), "Desconocido")
                filtered_chats.append({
                    "user_name": user_name,
                    "history": filtered_history
                })

        # Actualizar chats_data solo con los campos requeridos
        chats_data["chats"] = filtered_chats

        return chats_data

    except requests.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except ValueError as e:
        raise Exception(f"Error: {e}")

if __name__ == "__main__":
    try:
        chats_data = main()
        print_highlight("Final filtered chats data with content:")
        for chat in chats_data["chats"]:
            print(f"User Name: {chat['user_name']}")
            for message_id, message in chat["history"]["messages"].items():
                print(f"  Message ID: {message_id}, Role: {message['role']}, Content: {message['content']}")
    except Exception as e:
        print_highlight(str(e))
        sys.exit(1)