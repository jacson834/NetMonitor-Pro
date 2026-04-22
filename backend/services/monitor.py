import psutil
import time
import json
import logging
import asyncio
import os
from datetime import datetime
from database.connection import SessionLocal
from models.models import NetworkLog

# Resolve o caminho raiz do projeto de forma dinâmica (volta 3 pastas)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configuração do logger
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NetworkMonitorService:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(BASE_DIR, "config", "config.json")
            
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.interval = self.config.get("update_interval", 1)
        self.limit_mbps = self.config.get("alert_limit_mbps", 5.0)
        self.interface = self.config.get("interface", "all")
        self.old_data = self._get_net_data()
        self.active_connections = []
        self.current_stats = {"upload": 0.0, "download": 0.0}

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

    def _bytes_to_mb(self, bytes_val):
        return bytes_val / (1024 * 1024)

    def _get_net_data(self):
        if self.interface == "all" or not self.interface:
            return psutil.net_io_counters()
            
        pernic_data = psutil.net_io_counters(pernic=True)
        if self.interface in pernic_data:
            return pernic_data[self.interface]
        else:
            return psutil.net_io_counters() # Fallback seguro se a interface não existir

    async def start_monitoring(self):
        db_counter = 0
        while True:
            new_data = self._get_net_data()
            
            # Calcula diferença por segundo
            up_bytes = new_data.bytes_sent - self.old_data.bytes_sent
            down_bytes = new_data.bytes_recv - self.old_data.bytes_recv
            
            self.current_stats["upload"] = self._bytes_to_mb(up_bytes) / self.interval
            self.current_stats["download"] = self._bytes_to_mb(down_bytes) / self.interval
            
            self.old_data = new_data

            # Alertas
            if self.current_stats["upload"] > self.limit_mbps or self.current_stats["download"] > self.limit_mbps:
                logging.warning(f"Limite excedido! UP: {self.current_stats['upload']:.2f} MB/s | DOWN: {self.current_stats['download']:.2f} MB/s")

            # Broadcast WS
            await self.broadcast({
                "timestamp": datetime.now().isoformat(), 
                "stats": self.current_stats,
                "interface": self.interface
            })

            # Salva no DB a cada 10 interações (ex: 10 seg) para evitar sobrecarga no histórico
            db_counter += 1
            if db_counter >= 10:
                db_counter = 0
                db = SessionLocal()
                log_entry = NetworkLog(
                    upload_mbps=self.current_stats["upload"],
                    download_mbps=self.current_stats["download"]
                )
                db.add(log_entry)
                db.commit()
                db.close()

            await asyncio.sleep(self.interval)

monitor_service = NetworkMonitorService()