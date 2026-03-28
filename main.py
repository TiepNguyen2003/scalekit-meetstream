from datetime import datetime
import json
import os
import uvicorn
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv

from src.transcript_manager import TranscriptManager
from src.types import TranscriptWord

app = FastAPI(title="Agent Backend")
transcript_manager = TranscriptManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass # Client disconnected unexpectedly

manager = ConnectionManager()

@app.post("/webhook")
async def webhook(request: Request):
    # In FastAPI, we await the JSON body directly from the request object
    try:
        data = await request.json()
    except Exception:
        data = {} # Failsafe in case of empty or invalid JSON, similar to silent=True
        
    print(data)    
    
    # Check if this is a transcription payload by looking for expected keys
    if data and "words" in data and isinstance(data["words"], list):
        speakerName = data.get("speakerName", "Unknown")
        timestamp = datetime.fromtimestamp(data.get("start", 0)) 
        new_words_for_broadcast = []
        for word_data in data["words"]:
            # Map the dictionary keys to your TranscriptWord type
            # Note: Adjust these keys if your TranscriptWord class uses different names
            
            
            word_obj = TranscriptWord(
                speakerName = speakerName,
                timestamp = timestamp,
                word = word_data.get("word", ""),
                speakerConfidence = word_data.get("confidence", 0.0),
                startTime = word_data.get("start", 0.0),
                endTime = word_data.get("end", 0.0),
                is_final = word_data.get("is_final", False)
            )
            
            # Store in the singleton manager
            new_index = transcript_manager.add_word(word_obj)
            new_words_for_broadcast.append(word_obj.to_dict()) # Convert to dict for JSON serialization
            print(word_obj)
        
        # Broadcast the new words to all connected WebSocket clients
        if len(new_words_for_broadcast) > 0:
            await manager.broadcast(json.dumps(new_words_for_broadcast))

        # Log the update
        speaker = data.get("speakerName", "Unknown")
        transcript_text = data.get("transcript", "")
        print(f"✅ Processed {len(data['words'])} words from {speaker}: '{transcript_text}'")

    

    # FastAPI handles the 200 OK status code automatically by default.
    return {"status": "success"}

@app.websocket("/ws/transcript")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Keep the connection open and listen for client disconnects
        while True:
            await websocket.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(websocket)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8999)