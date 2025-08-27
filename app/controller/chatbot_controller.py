from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Dict, Any

import asyncio

from app.Chatbot_NLTK.chat import get_response

router = APIRouter(prefix="/chat", tags=["Chatbot", "Chat"])

@router.get("/{msg}", status_code=status.HTTP_200_OK)
async def resposta_chat(msg: str, request: Request) -> Dict[str, Any]:
    reposta = await asyncio.to_thread(get_response, msg)
    return {
        "id": request.state.request_id,
        "reposta": reposta
        }