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
def verify(req: Request):
    mode = req.query_params.get("hub.mode")
    hub_verify_token = req.query_params.get("hub.verify_token")
    hub_challenge = req.query_params.get("hub.challenge")
    print(f'mode == subscribe : {mode == "subscribe"} - mode: {mode}')
    print(f'hub_verify_token == VERIFY_TOKEN : {hub_verify_token == VERIFY_TOKEN} - hub: {hub_verify_token}')
    print(VERIFY_TOKEN)
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

                from_id = from_id[:4] + '9' + from_id[4:]

                resposta = await asyncio.to_thread(get_response, text)

                print(f'Resposta: {resposta}')
                print(f'From : {from_id}')
                print(f'PHONE_NUMBER_ID {PHONE_NUMBER_ID}')
                print(f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages")
                print(f'headers=("Authorization": Bearer {WHATSAPP_TOKEN}')
                print("Content-Type : application/json")
                print("json={")
                print("messaging_product : whatsapp")
                print("recipient_type : individual")
                print(f"to: {from_id}")
                print("type: text")
                print(f"text: body: {resposta}")

                resp = requests.post(
                    f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages",
                    headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}",
                            "Content-Type": "application/json"},
                    json={
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": from_id,
                        "type": "text",
                        "text": {"body": resposta},
                    },
                    timeout=10,
                )
                print("Status:", resp.status_code)
                print("Response:", resp.text)
        except Exception:
            pass
        return PlainTextResponse("", status_code=200)
    return PlainTextResponse(status_code=200)