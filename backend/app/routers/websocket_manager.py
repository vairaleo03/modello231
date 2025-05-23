from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []  # ✅ Lista di connessioni attive

    async def connect(self, websocket: WebSocket):
        """Accetta una nuova connessione WebSocket."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Rimuove una connessione WebSocket quando si disconnette."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_notification(self, message: str):
        """Invia una notifica generica."""
        print(f"----------------------->📨 Notifica inviata: {message}")
        await self._send_message({"type": "notification", "message": message})

    async def send_progress(self, message: str):
        """Invia un aggiornamento di progresso."""
        await self._send_message({"type": "progress", "message": message})

    async def _send_message(self, data: dict):
        """Metodo interno per inviare un messaggio JSON a tutti i client connessi."""
        message_json = json.dumps(data)
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"❌ Errore nell'invio del messaggio: {e}")
                self.disconnect(connection)

# 🔹 Istanza globale per la gestione WebSocket
websocket_manager = WebSocketManager()

# ✅ Endpoint WebSocket per ricevere messaggi dal frontend
@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📩 Messaggio ricevuto dal frontend: {data}")

            try:
                # 🔹 Convertiamo il messaggio JSON in un dizionario
                message_data = json.loads(data)

                # 🔹 Controlliamo il tipo di messaggio
                message_type = message_data.get("type")
                message = message_data.get("message")

                if message_type == "notification":
                    await websocket_manager.send_notification(message)
                elif message_type == "progress":
                    await websocket_manager.send_progress(message)
                else:
                    print(f"⚠️ Tipo di messaggio sconosciuto: {message_type}")

            except json.JSONDecodeError:
                print("❌ Errore: Il messaggio ricevuto non è un JSON valido.")

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        print("❌ Connessione WebSocket chiusa.")
