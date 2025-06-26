# Example Usage Scripts

This directory contains example scripts and usage patterns for the VOSK STT service.

## Files

- `websocket_client.html` - WebSocket real-time transcription example
- `batch_process.py` - Batch processing multiple audio files
- `streaming_example.py` - Streaming audio processing example

## Usage

### WebSocket Example
Open `websocket_client.html` in a browser to test real-time speech recognition.

### Batch Processing
```bash
python3 batch_process.py /path/to/audio/files/ vi
```

### Streaming Example
```bash
python3 streaming_example.py audio_stream.wav en
```

## Custom Integration

These examples show how to integrate the VOSK STT service into your own applications:

1. **Web Applications**: Use the WebSocket API for real-time transcription
2. **Batch Processing**: Process multiple files efficiently
3. **Streaming**: Handle continuous audio streams
4. **Custom Clients**: Build your own client applications

## Notes

- All examples assume the service is running on `localhost:8000`
- Modify the base URL in scripts if running on a different host/port
- Check the main README.md for detailed API documentation
