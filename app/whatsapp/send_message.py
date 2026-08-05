import requests

# Configuration
WHATSAPP_SEND_MESSAGE_API_URL = "https://pingly.in/api/v1/messages"
WHATSAPP_API_TOKEN = "pgly_live_O5G8CJwsJHT1rWhVJUqanKGMB7shM7xP"  # Replace with your actual token
WHATSAPP_ACCOUNT_ID = "81f4985e-8c20-4a0c-94e9-1c5dfa211bb7"


def send_whatsapp_message(to: str, text: str):
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
        "accountId": WHATSAPP_ACCOUNT_ID,
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