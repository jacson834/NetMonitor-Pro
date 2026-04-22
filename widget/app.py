import sys
import requests
import webbrowser
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor

class NetworkWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Configurações de Janela
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout
        layout = QVBoxLayout()
        self.label = QLabel("Conectando...")
        self.label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #00FF00; background-color: rgba(0, 0, 0, 150); padding: 10px; border-radius: 8px;")
        layout.addWidget(self.label)
        
        # Botão para abrir o Dashboard Web
        self.btn_dash = QPushButton("🌐 Abrir Dashboard")
        self.btn_dash.setStyleSheet("color: #FFFFFF; background-color: rgba(50, 50, 50, 150); padding: 5px; border-radius: 5px; border: 1px solid #555; font-weight: bold;")
        self.btn_dash.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dash.clicked.connect(self.open_dashboard)
        layout.addWidget(self.btn_dash)
        
        self.setLayout(layout)
        
        # Update Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000) # Atualiza a cada 1 segundo
        
        # Variáveis de arraste
        self.oldPos = self.pos()
        self.locked = False

    def update_stats(self):
        try:
            # Consome a API local do Backend
            resp = requests.get("http://localhost:8000/api/stats", timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                lock_symbol = "🔒" if self.locked else "🔓"
                text = f"{lock_symbol} ⬆ UP: {data['upload']:.2f} MB/s\n⬇ DL: {data['download']:.2f} MB/s"
                self.label.setText(text)
        except Exception as e:
            self.label.setText("API Offline")

    def open_dashboard(self):
        # Abre o endereço padrão do Vite no navegador
        webbrowser.open("http://localhost:5173")

    # Métodos para arrastar a janela sem borda
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.locked:
            self.oldPos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            # Botão direito trava/destrava o widget
            self.locked = not self.locked
            self.update_stats() # Força a atualização visual imediatamente

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.locked:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = NetworkWidget()
    # Posição inicial no canto da tela (aprox)
    screen = app.primaryScreen().geometry()
    widget.move(screen.width() - 250, screen.height() - 150)
    widget.show()
    sys.exit(app.exec())