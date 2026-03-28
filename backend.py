import asyncio
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws/transcript")
async def transcript_ws(websocket: WebSocket):
    await websocket.accept()
    
    words = ["Hello", "this", "is", "a", "test."]
    
    for word in words:
        await websocket.send_json([{"word": word}])
        await asyncio.sleep(1)
