from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from database.connection import Base

class NetworkLog(Base):
    __tablename__ = "network_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    upload_mbps = Column(Float, default=0.0)
    download_mbps = Column(Float, default=0.0)