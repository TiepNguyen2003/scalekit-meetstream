from datetime import datetime
import os
import uvicorn
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv

from src.transcript_manager import TranscriptManager
from src.types import TranscriptWord

# Remove the Flask imports:
# from flask import Flask, request

app = FastAPI(title="Agent Backend")
transcript_manager = TranscriptManager()


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

            print(word_obj)
        
        # Log the update
        speaker = data.get("speakerName", "Unknown")
        transcript_text = data.get("transcript", "")
        print(f"✅ Processed {len(data['words'])} words from {speaker}: '{transcript_text}'")

        # ---------------------------------------------------------
        # TODO: Here is where you would write this text to a database, 
        # a JSON file, or broadcast it via WebSockets so your frontend 
        # can display it live.
        # ---------------------------------------------------------

    # FastAPI handles the 200 OK status code automatically by default.
    # You can just return a dictionary, or a simple success message.
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8999)