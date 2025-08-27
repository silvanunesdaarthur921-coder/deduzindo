# server.py
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir conexões do front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estrutura para armazenar jogadores
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.host: Optional[WebSocket] = None
        self.players: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, is_host: bool = False):
        await websocket.accept()
        self.active_connections.append(websocket)
        if is_host:
            self.host = websocket
        else:
            self.players.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.players:
            self.players.remove(websocket)
        if websocket == self.host:
            self.host = None

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# WebSocket para host e jogadores
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, role: str = "player"):
    is_host = role.lower() == "host"
    await manager.connect(websocket, is_host)
    try:
        await manager.send_personal_message(f"✅ Conectado como {'Host' if is_host else 'Jogador'}!", websocket)
        while True:
            data = await websocket.receive_text()
            # Transmitir mensagens do host para todos os jogadores
            if is_host:
                await manager.broadcast(f"HOST: {data}")
            else:
                # Mensagens dos jogadores só vão para o host
                if manager.host:
                    await manager.send_personal_message(f"PLAYER: {data}", manager.host)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if is_host:
            await manager.broadcast("❌ Host desconectou. O jogo acabou.")
        else:
            await manager.broadcast("❌ Um jogador saiu do jogo.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

