from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from database.connection import engine, Base
from routes.api import router
from services.monitor import monitor_service

# Cria a tabela se não existir
Base.metadata.create_all(bind=engine)

# Garante que a pasta de logs existe
os.makedirs("../logs", exist_ok=True)

app = FastAPI(title="Network Monitor Pro API")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_service.start_monitoring())