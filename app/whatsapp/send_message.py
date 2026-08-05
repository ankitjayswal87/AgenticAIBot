import requests
import os
from constants import constant

# Configuration
WHATSAPP_SEND_MESSAGE_API_URL = constant.WHATSAPP_SEND_MESSAGE_API_URL
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")

def send_whatsapp_message(to: str, text: str, account_id: str):
    """
    Send a WhatsApp message via Pingly.

    Args:
        to (str): Recipient phone number in E.164 format (e.g. +919979272423)
        text (str): Message text

    Returns:
        dict: API response if JSON, otherwise raw response text.
    """
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "accountId": account_id,
        "to": to,
        "text": text
    }

    try:
        response = requests.post(WHATSAPP_SEND_MESSAGE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        # print("MESSAGE SEND RESPONSE---")
        # print(response)

        try:
            return response.json()
        except ValueError:
            return {"success": True, "response": response.text}

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": getattr(e.response, "status_code", None),
            "response": getattr(e.response, "text", None)
        }