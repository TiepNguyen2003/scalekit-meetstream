import os
import uvicorn
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv

# Remove the Flask imports:
# from flask import Flask, request

app = FastAPI(title="Agent Backend")

@app.post("/webhook")
async def webhook(request: Request):
    # In FastAPI, we await the JSON body directly from the request object
    try:
        data = await request.json()
    except Exception:
        data = {} # Failsafe in case of empty or invalid JSON, similar to silent=True
        
    print(data)    
    
    # Check if this is a transcription payload by looking for expected keys
    if data and "speakerName" in data and "transcript" in data:
        bot_id = data.get("bot_id", "unknown")
        speaker = data.get("speakerName", "Unknown")
        
        # 'new_text' usually contains the latest spoken words
        new_text = data.get("new_text", "")
        
        # 'end_of_turn' is useful to know if the person has stopped speaking
        is_final = data.get("end_of_turn", False)
        
        # Print the live transcription update to the console
        if new_text.strip():
            status_marker = "[FINAL]" if is_final else "[...]"
            print(f"🎙️ {speaker} {status_marker}: {new_text}")

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