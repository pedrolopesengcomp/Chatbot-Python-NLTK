# main.py
import os, requests
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from chat import ChatBot
app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


@app.get("/")
def verify(mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    print("hub_challenge: " + hub_challenge)
    print(f"hub_verify_token {hub_verify_token}")
    if mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "", status_code=200)
    else:
        return PlainTextResponse("", status_code=403)

@app.post("/")
async def incoming(req: Request):
    body = await req.json()
    try:
        entry = body["entry"][0]
        change = entry["changes"][0]
        msg = change["value"].get("messages", [None])[0]

        if msg and "from" in msg:
            from_id = msg["from"]
            text = msg.get("text", {}).get("body", "")

            chatbot = ChatBot()

            response_text = await chatbot.get_response(text)

            requests.post(
                f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages",
                headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}",
                         "Content-Type": "application/json"},
                json={
                    "messaging_product": "whatsapp",
                    "to": from_id,
                    "type": "text",
                    "text": {"body": f"{response_text}"},
                },
                timeout=10,
            )
    except Exception:
        pass
    return PlainTextResponse("", status_code=200)


