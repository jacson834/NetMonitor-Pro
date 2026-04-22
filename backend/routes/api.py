from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import SessionLocal
from models.models import NetworkLog
from services.monitor import monitor_service
from datetime import datetime, timedelta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_current_stats():
    return monitor_service.current_stats

@router.get("/history")
def get_history(limit: int = 100, db: Session = Depends(get_db)):
    logs = db.query(NetworkLog).order_by(NetworkLog.timestamp.desc()).limit(limit).all()
    return logs[::-1]

@router.get("/usage/daily")
def get_daily_usage(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    # Simplificação: média do dia em MB/s
    result = db.query(
        func.avg(NetworkLog.upload_mbps).label("avg_up"),
        func.avg(NetworkLog.download_mbps).label("avg_down")
    ).filter(func.date(NetworkLog.timestamp) == today).first()
    
    return {
        "date": today.isoformat(),
        "avg_upload_mbps": result.avg_up or 0,
        "avg_download_mbps": result.avg_down or 0
    }

@router.get("/usage/monthly")
def get_monthly_usage(db: Session = Depends(get_db)):
    return {"message": "Monthly usage aggregation endpoint"}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await monitor_service.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        monitor_service.disconnect(websocket)