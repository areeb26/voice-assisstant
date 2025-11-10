# 🤖 Jarvis Voice Assistant Setup Guide

Transform your AI assistant into a voice-activated Jarvis-like system!

## ✨ Features

- **Wake Word Activation**: Say "Jarvis" or "Hey Jarvis" to activate
- **Continuous Listening**: Always listening for your commands
- **Voice Responses**: Jarvis speaks back to you
- **AI-Powered**: Uses Google Gemini for intelligent responses
- **Bilingual**: Supports English and Urdu
- **Task Management**: Create and manage tasks by voice
- **Natural Conversations**: Ask questions, get information

## 🎯 Quick Start

### 1. Configure Voice Settings

Edit your `.env` file:

```bash
# Voice Features - Jarvis Mode
VOICE_ENABLED=True
VOICE_WAKE_WORD_REQUIRED=True
VOICE_WAKE_WORDS=jarvis,hey jarvis,ok jarvis,assistant
VOICE_CONTINUOUS_MODE=True
VOICE_RESPONSE_ENABLED=True
VOICE_SPEECH_RATE=150
VOICE_VOLUME=0.9
VOICE_AUTO_CALIBRATE=True

# AI Integration
USE_GEMINI_AI=True
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
```

### 2. Install Audio Dependencies (if needed)

**Windows:**
```bash
pip install pyaudio
```

If PyAudio fails:
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

### 3. Start Jarvis

**Option A: Voice-Only Mode (Standalone)**
```bash
python jarvis.py
```

**Option B: Full Server with Voice API**
```bash
python main.py
```

Then use the voice endpoints at http://localhost:8001/api/v1/voice/

## 🎤 Using Voice Commands

### Wake Words
Say any of these to activate Jarvis:
- "Jarvis"
- "Hey Jarvis"
- "Ok Jarvis"
- "Assistant"

### Example Commands

**Task Management:**
- "Jarvis, create a task to buy groceries tomorrow"
- "Jarvis, list my tasks"
- "Jarvis, complete the grocery task"

**Questions & Chat:**
- "Jarvis, what's the weather today?"
- "Jarvis, tell me a joke"
- "Jarvis, what can you do?"

**File Operations:**
- "Jarvis, create a file called notes.txt"
- "Jarvis, read the file report.pdf"

**System Commands:**
- "Jarvis, what time is it?"
- "Jarvis, search for Python tutorials"

## 🌐 Voice API Endpoints

### Start Listening
```bash
POST http://localhost:8001/api/v1/voice/listen/start
```

### Stop Listening
```bash
POST http://localhost:8001/api/v1/voice/listen/stop
```

### Process Voice Command
```bash
POST http://localhost:8001/api/v1/voice/command
Content-Type: application/json

{
  "audio_data": "base64_encoded_audio",
  "language": "en"
}
```

### Text-to-Speech
```bash
POST http://localhost:8001/api/v1/voice/speak
Content-Type: application/json

{
  "text": "Hello, I am Jarvis",
  "language": "en",
  "speed": 150
}
```

### Get Voice Settings
```bash
GET http://localhost:8001/api/v1/voice/status
```

## 🎨 Customization

### Change Wake Words

Edit `.env`:
```bash
VOICE_WAKE_WORDS=jarvis,friday,computer,hey ai
```

### Adjust Voice Speed

```bash
VOICE_SPEECH_RATE=150  # Default
VOICE_SPEECH_RATE=120  # Slower
VOICE_SPEECH_RATE=180  # Faster
```

### Disable Wake Word (Always Listen)

```bash
VOICE_WAKE_WORD_REQUIRED=False
```

### Change Voice Gender/Style

Edit `voice_handler/text_to_speech.py` and configure the TTS engine.

## 🛠️ Troubleshooting

### Microphone Not Working

1. Check microphone permissions
2. Test with: `python -m speech_recognition`
3. Adjust energy threshold:
   ```bash
   VOICE_ENERGY_THRESHOLD=4000  # Increase for noisy environments
   ```

### Voice Not Detected

1. Enable auto-calibration:
   ```bash
   VOICE_AUTO_CALIBRATE=True
   ```

2. Increase timeout:
   ```bash
   VOICE_TIMEOUT=10
   ```

### No Voice Response

Check that TTS is enabled:
```bash
VOICE_RESPONSE_ENABLED=True
```

### Gemini API Errors

Make sure your API key is valid:
```bash
GEMINI_API_KEY=your-valid-key-here
```

Get a free key at: https://aistudio.google.com/app/apikey

## 📱 Web Interface

Access the voice control panel:
```
http://localhost:8001/api/v1/voice/
```

Features:
- Start/stop listening
- View voice status
- Test microphone
- Adjust settings
- View command history

## 🚀 Advanced Features

### Background Service

Run Jarvis as a background service that's always listening:

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "At startup"
4. Action: Start program `python jarvis.py`

**Linux (systemd):**
```bash
sudo nano /etc/systemd/system/jarvis.service
```

```ini
[Unit]
Description=Jarvis AI Assistant
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/voice-assisstant
ExecStart=/path/to/venv/bin/python jarvis.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

### Integration with Home Automation

Use the N8N integration to trigger smart home devices:

```bash
# In .env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/jarvis
```

Then:
- "Jarvis, turn on the lights"
- "Jarvis, set temperature to 72 degrees"
- "Jarvis, play music"

## 📖 Tips for Best Experience

1. **Speak Clearly**: Enunciate wake word and commands
2. **Reduce Background Noise**: Use in quiet environment or with noise-canceling mic
3. **Use Natural Language**: Jarvis understands conversational commands
4. **Be Specific**: "Create task to buy milk" vs just "buy milk"
5. **Check Gemini**: Enable Gemini API for much better responses

## 🎭 Make It More Like Jarvis

### Custom Responses

Edit `services/gemini_service.py` to add personality:

```python
prompt = f"""You are Jarvis, an AI assistant like in Iron Man movies.
You address the user as 'sir' and have a polite, sophisticated British tone.
Be concise but helpful.

User: {message}
Jarvis:"""
```

### Change Voice

Configure different TTS engines in `voice_handler/text_to_speech.py`:
- Google TTS (gTTS)
- pyttsx3 (offline)
- Azure TTS (premium voices)
- Amazon Polly

## 🎬 Demo

Try these commands to test:

1. Say: "Jarvis"
2. Wait for activation sound/response
3. Say: "What can you do?"
4. Say: "Create a task to test voice commands"
5. Say: "List my tasks"

Enjoy your personal Jarvis! 🚀
