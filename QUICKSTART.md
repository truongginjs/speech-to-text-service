# 🚀 Quick Start Guide

## 🐳 Option 1: Use Pre-built Docker Image (Fastest)

The quickest way to get started is using the pre-built image from Docker Hub:

```bash
# Pull and run the image directly
docker run -p 8000:8000 truongginjs/stt:latest
```

**Or create a simple docker-compose.yml**:
```yaml
version: '3.8'
services:
  vosk-stt:
    image: truongginjs/stt:latest
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Then run: `docker-compose up`

## 🔧 Option 2: Build from Source

### Prerequisites
- Docker
- Docker Compose

### Setup and Run

### 1. Build and Start the Service
```bash
# Method 1: Using the convenience script
./run.sh build
./run.sh start

# Method 2: Using Docker Compose directly
docker-compose up --build
```

### 2. Access the Service
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Test the Service
```bash
# Using the test script
python3 test_service.py

# Using the client script
./client.py health
./client.py languages

# Manual test with curl
curl http://localhost:8000/health
```

## Usage Examples

### Web Interface
1. Open http://localhost:8000 in your browser
2. Upload an audio file or use microphone
3. Select language (English/Vietnamese)
4. Get transcription results

### API Usage

#### Upload File for Transcription
```bash
# English
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@your_audio.wav" \
     -F "language=en"

# Vietnamese
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@your_audio.mp3" \
     -F "language=vi"
```

#### Python Client
```python
import requests

# Transcribe file
with open('audio.wav', 'rb') as f:
    files = {'file': f}
    data = {'language': 'vi'}
    response = requests.post('http://localhost:8000/transcribe', 
                           files=files, data=data)
    result = response.json()
    print(result['text'])
```

#### Using the provided client
```bash
./client.py transcribe audio.wav en
./client.py transcribe vietnamese_audio.mp3 vi
```

## Supported Audio Formats
- WAV (recommended)
- MP3
- FLAC
- M4A
- OGG

## Language Support
- `en` - English (US)
- `vi` - Vietnamese

## Management Commands

```bash
# Start service
./run.sh start

# Stop service
./run.sh stop

# View logs
./run.sh logs

# Check status
./run.sh status

# Run tests
./run.sh test

# Clean up
./run.sh cleanup
```

## Troubleshooting

### Service won't start
```bash
# Check Docker is running
docker --version
docker-compose --version

# View detailed logs
./run.sh logs

# Rebuild service
./run.sh stop
./run.sh build
./run.sh start
```

### Audio not processing
- Ensure audio file exists and is readable
- Try converting to WAV format
- Check file size (max 100MB by default)
- Verify language code (en/vi)

### Performance issues
- Use WAV format for best performance
- Prefer 16kHz, 16-bit, mono audio
- Consider using larger models for better accuracy

## Development Tips

### Local development (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Download models manually
mkdir -p models
# Extract VOSK models to models/vi and models/en

# Run locally
python app.py
```

### Custom models
Edit Dockerfile to download different VOSK models or add new languages.

## Support
- Check logs: `./run.sh logs`
- Health check: `curl http://localhost:8000/health`
- Test suite: `python3 test_service.py`
