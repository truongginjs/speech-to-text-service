import os
import json
import asyncio
import wave
import logging
from typing import Optional
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import vosk
import uvicorn
from pydub import AudioSegment
import tempfile
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VOSK Speech-to-Text API", version="1.0.0")

# Model paths
MODELS_DIR = "/app/models"
VIETNAMESE_MODEL_PATH = os.path.join(MODELS_DIR, "vi")
ENGLISH_MODEL_PATH = os.path.join(MODELS_DIR, "en")

# Global models
models = {}

def load_models():
    """Load VOSK models for supported languages"""
    global models
    
    try:
        if os.path.exists(VIETNAMESE_MODEL_PATH):
            logger.info("Loading Vietnamese model...")
            models["vi"] = vosk.Model(VIETNAMESE_MODEL_PATH)
            logger.info("Vietnamese model loaded successfully")
        else:
            logger.warning(f"Vietnamese model not found at {VIETNAMESE_MODEL_PATH}")
            
        if os.path.exists(ENGLISH_MODEL_PATH):
            logger.info("Loading English model...")
            models["en"] = vosk.Model(ENGLISH_MODEL_PATH)
            logger.info("English model loaded successfully")
        else:
            logger.warning(f"English model not found at {ENGLISH_MODEL_PATH}")
            
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise

def convert_to_wav(audio_file_path: str, output_path: str) -> str:
    """Convert audio file to WAV format with correct parameters for VOSK"""
    try:
        audio = AudioSegment.from_file(audio_file_path)
        # Convert to mono, 16kHz, 16-bit
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        raise

def transcribe_audio(audio_file_path: str, language: str = "en") -> dict:
    """Transcribe audio file using VOSK"""
    if language not in models:
        raise ValueError(f"Language {language} not supported. Available: {list(models.keys())}")
    
    try:
        # Convert to WAV if necessary
        if not audio_file_path.endswith('.wav'):
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
            convert_to_wav(audio_file_path, wav_path)
        else:
            wav_path = audio_file_path
        
        # Open WAV file
        wf = wave.open(wav_path, 'rb')
        
        # Check audio format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            wf.close()
            # Convert to correct format
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                correct_wav_path = temp_wav.name
            convert_to_wav(wav_path, correct_wav_path)
            wf = wave.open(correct_wav_path, 'rb')
        
        # Create recognizer
        rec = vosk.KaldiRecognizer(models[language], wf.getframerate())
        rec.SetWords(True)
        
        results = []
        final_result = ""
        
        # Process audio in chunks
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result.get("text"):
                    results.append(result)
                    final_result += result["text"] + " "
        
        # Get final result
        final_result_json = json.loads(rec.FinalResult())
        if final_result_json.get("text"):
            final_result += final_result_json["text"]
        
        wf.close()
        
        # Clean up temporary files
        if wav_path != audio_file_path:
            os.unlink(wav_path)
        
        return {
            "success": True,
            "language": language,
            "text": final_result.strip(),
            "detailed_results": results,
            "confidence": final_result_json.get("confidence", 0)
        }
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    load_models()
    logger.info(f"Available languages: {list(models.keys())}")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the simple recorder interface"""
    try:
        async with aiofiles.open("recorder.html", mode='r') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Recorder interface not found</h1><p>Please make sure recorder.html exists.</p>")

@app.get("/simple", response_class=HTMLResponse)
async def get_simple_interface():
    """Serve the original simple HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VOSK Speech-to-Text - Simple Interface</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
            select, input, button { padding: 10px; margin: 5px; border-radius: 5px; border: 1px solid #ddd; }
            button { background: #007bff; color: white; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { background: white; padding: 15px; border-radius: 5px; margin-top: 10px; min-height: 100px; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>🎤 VOSK Speech-to-Text - Simple Interface</h1>
        <p>Upload an audio file for transcription</p>
        
        <div class="container">
            <h3>📁 File Upload</h3>
            <form id="uploadForm">
                <div>
                    <label>Language:</label>
                    <select id="language">
                        <option value="en">English</option>
                        <option value="vi">Vietnamese</option>
                    </select>
                </div>
                <div>
                    <label>Audio File:</label>
                    <input type="file" id="audioFile" accept="audio/*" required>
                </div>
                <button type="submit">🚀 Transcribe</button>
            </form>
            <div id="result" class="result"></div>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <a href="/" style="padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">
                🎤 Go to Voice Recorder
            </a>
        </div>

        <script>
            // File upload handling
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                const fileInput = document.getElementById('audioFile');
                const language = document.getElementById('language').value;
                
                if (!fileInput.files[0]) {
                    alert('Please select an audio file');
                    return;
                }
                
                formData.append('file', fileInput.files[0]);
                formData.append('language', language);
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '⏳ Processing...';
                
                try {
                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        resultDiv.innerHTML = `
                            <div class="success">✅ Transcription completed</div>
                            <p><strong>Text:</strong> ${result.text}</p>
                            <p><strong>Language:</strong> ${result.language}</p>
                            <p><strong>Confidence:</strong> ${result.confidence}</p>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="error">❌ Error: ${result.error}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/transcribe")
async def transcribe_file(
    file: UploadFile = File(...),
    language: str = Form(default="en")
):
    """Transcribe uploaded audio file"""
    
    if language not in models:
        raise HTTPException(
            status_code=400,
            detail=f"Language {language} not supported. Available: {list(models.keys())}"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Transcribe the audio
        result = transcribe_audio(temp_file_path, language)
        return JSONResponse(content=result)
    
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

@app.websocket("/ws/{language}")
async def websocket_endpoint(websocket: WebSocket, language: str):
    """WebSocket endpoint for real-time speech recognition"""
    
    if language not in models:
        await websocket.close(code=4000, reason=f"Language {language} not supported")
        return
    
    await websocket.accept()
    
    try:
        # Create recognizer for real-time processing
        rec = vosk.KaldiRecognizer(models[language], 16000)
        rec.SetWords(True)
        
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                await websocket.send_text(json.dumps(result))
            else:
                partial = json.loads(rec.PartialResult())
                await websocket.send_text(json.dumps(partial))
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=4000, reason=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "available_languages": list(models.keys()),
        "models_loaded": len(models)
    }

@app.get("/languages")
async def get_languages():
    """Get available languages"""
    return {
        "languages": list(models.keys()),
        "details": {
            "en": "English (US)",
            "vi": "Vietnamese"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
