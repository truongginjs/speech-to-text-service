# VOSK Speech-to-Text Docker Project

A Docker-based speech-to-text service using VOSK with support for Vietnamese and English languages.

## 🐳 Docker Hub

**Image**: [`truongginjs/stt`](https://hub.docker.com/r/truongginjs/stt)

```bash
# Pull and run the pre-built image (supports AMD64 + ARM64)
docker run -p 8000:8000 truongginjs/stt:latest

# Or use Docker Compose
docker-compose up
```

### Platform Compatibility

The Docker image supports multiple platforms:
- ✅ **linux/amd64** (Intel/AMD x86_64)
- ✅ **linux/arm64** (ARM64/Apple Silicon)

If you get "exec format error", see [`PLATFORM_FIX.md`](PLATFORM_FIX.md) for solutions.

## Features

- 🎤 **Multi-language Support**: Vietnamese and English
- 🌐 **REST API**: Upload audio files for transcription
- 🔄 **Real-time Processing**: WebSocket support for live speech recognition
- 🐳 **Docker Ready**: Complete containerized solution
- 📱 **Web Interface**: Simple HTML interface for testing
- 🎯 **High Accuracy**: Uses VOSK's pre-trained models

## Quick Start

### Prerequisites

- Docker
- Docker Compose

### Installation & Running

1. **Clone the repository**:
   ```bash
   git clone https://github.com/truongginjs/speech-to-text-service.git
   cd speech-to-text-service
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the service**:
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### File Upload Transcription
```bash
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@your_audio.wav" \
     -F "language=vi"
```

### WebSocket Real-time Recognition
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/en');
// Send audio data as binary
ws.send(audioBuffer);
```

### Available Languages
```bash
curl http://localhost:8000/languages
```

## Supported Audio Formats

- WAV (recommended)
- MP3
- FLAC
- M4A
- OGG
- And more (automatically converted)

## Language Codes

- `en` - English (US)
- `vi` - Vietnamese

## Usage Examples

### 1. Using the Web Interface

Navigate to http://localhost:8000 and use the built-in interface to:
- Upload audio files
- Start real-time recording
- View transcription results

### 2. Using cURL

**Vietnamese transcription**:
```bash
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@vietnamese_audio.mp3" \
     -F "language=vi"
```

**English transcription**:
```bash
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@english_audio.wav" \
     -F "language=en"
```

### 3. Using Python

```python
import requests

# Upload file for transcription
with open('audio.wav', 'rb') as f:
    files = {'file': f}
    data = {'language': 'vi'}
    response = requests.post('http://localhost:8000/transcribe', 
                           files=files, data=data)
    result = response.json()
    print(result['text'])
```

### 4. Using JavaScript (WebSocket)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/en');

ws.onopen = () => {
    console.log('Connected to STT service');
};

ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Transcription:', result.text);
};

// Send audio data
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
            ws.send(event.data);
        };
        mediaRecorder.start(1000); // Send data every second
    });
```

## API Response Format

### Successful Response
```json
{
    "success": true,
    "language": "vi",
    "text": "Xin chào, tôi là trợ lý ảo",
    "detailed_results": [...],
    "confidence": 0.95
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message"
}
```

## Configuration

### Environment Variables

- `MODELS_DIR`: Directory containing VOSK models (default: `/app/models`)
- `PYTHONUNBUFFERED`: Set to 1 for immediate log output

### Custom Models

To use different VOSK models, modify the Dockerfile to download your preferred models:

```dockerfile
# Add custom model download
RUN wget -O /tmp/your-custom-model.zip https://your-model-url.zip && \
    unzip /tmp/your-custom-model.zip -d /app/models/ && \
    mv /app/models/your-model-folder /app/models/custom && \
    rm /tmp/your-custom-model.zip
```

## Docker Hub & Publishing

### Using the Management Script

The project includes a comprehensive management script `run.sh` for easy operations:

```bash
# Build the Docker image
./run.sh build

# Start the service
./run.sh start

# View logs
./run.sh logs

# Test the service
./run.sh test

# Build and publish to Docker Hub
./run.sh publish

# Publish with a specific version
./run.sh publish v1.0

# Stop the service
./run.sh stop
```

### Publishing to Docker Hub

1. **Login to Docker Hub**:
   ```bash
   docker login
   ```

2. **Build and push**:
   ```bash
   ./run.sh publish        # Pushes as latest
   ./run.sh publish v1.0   # Pushes as v1.0
   ```

3. **Or manually**:
   ```bash
   docker build -t truongginjs/stt:latest .
   docker push truongginjs/stt:latest
   ```

### Alternative Image Names

If you want to use a different Docker Hub username, you can:

1. **Update docker-compose.yml**:
   ```yaml
   image: yourusername/stt:latest
   ```

2. **Update the IMAGE_NAME in run.sh**:
   ```bash
   IMAGE_NAME="yourusername/stt"
   ```

## Development

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download models manually**:
   ```bash
   mkdir -p models
   # Download and extract VOSK models to models/vi and models/en
   ```

3. **Run locally**:
   ```bash
   python app.py
   ```

### Adding New Languages

1. Add model download in Dockerfile
2. Update the `models` dictionary in `app.py`
3. Add language details in the `/languages` endpoint

## Performance Tips

- Use WAV format for best performance
- 16kHz, 16-bit, mono audio works best
- Smaller models trade accuracy for speed
- Use larger models for better accuracy

## Troubleshooting

### Common Issues

1. **Model not found**: Ensure models are properly downloaded in the Docker build
2. **Audio format issues**: Try converting to WAV format first
3. **Memory issues**: Use smaller models or increase Docker memory limits

### Logs

View container logs:
```bash
docker-compose logs -f vosk-stt
```

### Health Check

```bash
curl http://localhost:8000/health
```

## License

This project uses VOSK (Apache 2.0 License) and is intended for educational and commercial use.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both languages
5. Submit a pull request

## Model Information

- **Vietnamese Model**: vosk-model-small-vi-0.4 (~39MB)
- **English Model**: vosk-model-small-en-us-0.15 (~39MB)
- **Accuracy**: Good for general speech recognition
- **Speed**: Optimized for real-time processing

For better accuracy, consider using larger models (vosk-model-vi or vosk-model-en-us).
