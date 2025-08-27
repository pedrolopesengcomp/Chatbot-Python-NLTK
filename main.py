from fastapi import FastAPI, Request
from app.Chatbot_NLTK import chat

from app.controller import chatbot_controller

from app.core.middlewares import cors_middleware

app = FastAPI()

# add middlewares
cors_middleware.add(app)
 
app.include_router(chatbot_controller.router)