import asyncio
from datetime import datetime
import json
import os
import uvicorn
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv

from src.transcript_manager import TranscriptManager
from src.types import TranscriptWord

import logging

logging.basicConfig(
    filename="system_debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    
    # Check if this is a transcription payload by looking for expected keys

    logger.info(f"Received message: {data}")
    if data:
        if not data["end_of_turn"]:
            return {"status": "ignored", "reason": "Not end of turn"}
        if "words" not in data or not isinstance(data["words"], list):
            logger.warning("Received data does not contain 'words' key or it's not a list.")
            return {"status": "ignored", "reason": "Invalid payload structure"}
        print(f"Processing {data['transcript']}")
        speakerName = data.get("speakerName", "Unknown")
        timestamp = datetime.fromtimestamp(data.get("start", 0)) 
        words_to_add = []
        had_final = False
        for word_data in data["words"]:
            # Map the dictionary keys to your TranscriptWord type
            # Note: Adjust these keys if your TranscriptWord class uses different names
            word = word_data.get("word", "")
            if len(word.strip()) == 0:
                continue # Skip empty words
            
            word_obj = TranscriptWord(
                speakerName = speakerName,
                timestamp = timestamp,
                word = word,
                speakerConfidence = word_data.get("confidence", 0.0),
                startTime = word_data.get("start", 0.0),
                endTime = word_data.get("end", 0.0),
                is_final = word_data.get("word_is_final")
            )

            
            transcript_manager.add_word(word_obj)
        
            

        # Log the update
        speaker = data.get("speakerName", "Unknown")
        transcript_text = data.get("transcript", "")
        #print(f"✅ Processed {len(data['words'])} words from {speaker}: '{transcript_text}'")

    

    # FastAPI handles the 200 OK status code automatically by default.
    return {"status": "success"}

@app.websocket("/ws/transcript")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    last_index = 0 
    
    try:
        while True:
            # 1. Fetch any new words that arrived since our last tick
            new_words = transcript_manager.get_words(last_index, 999999)
            
            # 2. If we have new words, broadcast them!
            if new_words:
                last_index += len(new_words)
                
                # Convert objects to dictionaries for JSON serialization
                payload = [w.to_dict() for w in new_words]
                message = json.dumps(payload)
                print(f"Sending message: {message}")
                await websocket.send_text(message)
            
            # 3. Sleep for a bit before checking again (e.g., 2 seconds)
            # You can tweak this number to be faster (0.5) or slower (5)
            
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8999)