from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Dict, Any
from fastapi.responses import PlainTextResponse
import os, requests

import asyncio

from app.Chatbot_NLTK.chat import get_response

router = APIRouter(prefix="/chat", tags=["Chatbot", "Chat"])

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


#@router.get("/{msg}", status_code=status.HTTP_200_OK)
#async def resposta_chat(msg: str, request: Request) -> Dict[str, Any]:
    #reposta = await asyncio.to_thread(get_response, msg)
    #return {
        #"id": request.state.request_id,
        #"reposta": reposta
        #}

@router.get("/")
def verify(mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    print("hub_challenge: " + hub_challenge)
    print(f"hub_verify_token {hub_verify_token}")
    if mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "", status_code=200)
    else:
        return PlainTextResponse("", status_code=403)

@router.post("/")
async def incoming(req: Request):
    body = await req.json()
    try:
        entry = body["entry"][0]
        change = entry["changes"][0]
        msg = change["value"].get("messages", [None])[0]

        if msg and "from" in msg:
            from_id = msg["from"]
            text = msg.get("text", {}).get("body", "")

            resposta = await asyncio.to_thread(get_response, text)

            requests.post(
                f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages",
                headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}",
                         "Content-Type": "application/json"},
                json={
                    "messaging_product": "whatsapp",
                    "to": from_id,
                    "type": "text",
                    "text": {"body": f"{resposta}"},
                },
                timeout=10,
            )
    except Exception:
        pass
    return PlainTextResponse("", status_code=200)