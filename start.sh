curl -X POST https://api.meetstream.ai/api/v1/bots/create_bot \
     -H "Authorization: Token ms_Zg9tcT1dzX5ugGIAO0bajEuLoOu8EhoJ" \
     -H "Content-Type: application/json" \
     -d '{
  "meeting_link": "https://meet.google.com/mrc-ptni-utp",
  "bot_name": "Meetstream Agent",
  "video_required": true,
  "live_transcription_required": {
    "webhook_url": "https://sirena-unimitable-glowingly.ngrok-free.dev/webhook"
  },
  "recording_config": {
    "transcript": {
      "provider": {
        "assemblyai_streaming": {
          "transcription_mode": "raw",
          "sample_rate": 48000,
          "speech_model": "universal-streaming-english",
          "format_turns": false,
          "encoding": "pcm_s16le",
          "vad_threshold": "0.4",
          "end_of_turn_confidence_threshold": "0.4",
          "inactivity_timeout": 300,
          "min_end_of_turn_silence_when_confident": "400",
          "max_turn_silence": "1280"
        }
      }
    }
  }
}'