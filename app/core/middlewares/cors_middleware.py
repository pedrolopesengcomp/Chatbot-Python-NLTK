import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

def add(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    @app.middleware("http")
    async def add_request_id_and_timing(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.time()

        # adicionar request id ao scope para handlers/handlers de exceção usarem
        request.state.request_id = request_id

        logging.info(f"[{request_id}] IN  {request.method} {request.url.path} query={dict(request.query_params)}")

        response = await call_next(request)

        process_time = time.time() - start
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Request-Id"] = request_id

        logging.info(f"[{request_id}] OUT {request.method} {request.url.path} status={response.status_code} time={process_time:.4f}s")
        return response

