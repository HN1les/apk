from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import uvicorn
from database import Database
from datetime import datetime
import json

app = FastAPI()
db = Database()

# Хранение активных подключений
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}  # user_id: websocket

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def broadcast(self, message: dict):
        # Отправляем сообщение всем подключенным пользователям
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# API endpoints
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Сохраняем сообщение в БД
            db.save_message(
                user_id=data['user_id'],
                username=data['username'],
                text=data['text']
            )
            # Отправляем сообщение всем
            await manager.broadcast({
                'user_id': data['user_id'],
                'username': data['username'],
                'text': data['text'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@app.post("/register")
async def register(username: str, email: str, password: str):
    success, error = db.register_user(username, email, password)
    if success:
        return {"status": "success"}
    return {"status": "error", "message": error}

@app.post("/login")
async def login(email: str, password: str):
    user = db.login_user(email, password)
    if user:
        return {"status": "success", "user": user}
    return {"status": "error", "message": "Invalid credentials"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)