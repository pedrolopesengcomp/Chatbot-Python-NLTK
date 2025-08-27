from fastapi import FastAPI, Request
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Dict, Any
from fastapi.responses import PlainTextResponse
import os, requests, json
from dotenv import load_dotenv

from app.core.middlewares import cors_middleware
import asyncio

from app.Chatbot_NLTK.chat import get_response

app = FastAPI()

# add middlewares
cors_middleware.add(app)

load_dotenv()

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

@app.get("/")
def verify(mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    print(f'mode == subscribe : {mode == "subscribe"} - mode: {mode}')
    print(f'hub_verify_token == VERIFY_TOKEN : {hub_verify_token == VERIFY_TOKEN} - hub: {hub_verify_token}')
    print(VERIFY_TOKEN)
    if(mode == "subscribe"):
        print("OK")
    if mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge or "", status_code=200)
    else:
        return PlainTextResponse("", status_code=403)

@app.post("/")
async def incoming(req: Request):
    if(req == None):
        return PlainTextResponse("", status_code=403)
    else:
        body = await req.json()
        try:
            entry = body["entry"][0]
            change = entry["changes"][0]
            msg = change["value"].get("messages", [None])[0]
            print(f'entry: {entry}')
            print(f'change: {change}')
            print(f'msg: {msg}')

            if msg and "from" in msg:
                from_id = msg["from"]
                text = msg.get("text", {}).get("body", "")

                resposta = await asyncio.to_thread(get_response, text)

                print(f'Resposta: {resposta}')

                requests.post(
                    f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages",
                    headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}",
                            "Content-Type": "application/json"},
                    json={
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": from_id,
                        "type": "text",
                        "text": {"body": f"{resposta}"},
                    },
                    timeout=10,
                )
        except Exception:
            pass
        return PlainTextResponse("", status_code=200)
    return PlainTextResponse(status_code=200)