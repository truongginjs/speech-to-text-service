#!/usr/bin/env python3
"""
Test script for VOSK STT service
"""

import requests
import time
import json
from pathlib import Path

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_languages():
    """Test languages endpoint"""
    print("🌐 Testing languages endpoint...")
    try:
        response = requests.get("http://localhost:8000/languages")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Languages: {data}")
            return True
        else:
            print(f"❌ Languages test failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Languages test error: {e}")
        return False

def test_transcription(audio_file: str, language: str = "en"):
    """Test file transcription"""
    print(f"🎤 Testing transcription with {audio_file} (language: {language})...")
    
    if not Path(audio_file).exists():
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': f}
            data = {'language': language}
            response = requests.post("http://localhost:8000/transcribe", 
                                   files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Transcription successful:")
                print(f"   Text: {result.get('text', 'N/A')}")
                print(f"   Language: {result.get('language', 'N/A')}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
                return True
            else:
                print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Transcription request failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Transcription test error: {e}")
        return False

def generate_test_audio():
    """Generate a simple test audio file using text-to-speech (if available)"""
    print("🎵 Generating test audio file...")
    try:
        import pyttsx3
        import wave
        import io
        
        # Create TTS engine
        engine = pyttsx3.init()
        
        # Set properties
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Test phrases
        test_phrases = {
            'en': "Hello, this is a test of the speech to text system.",
            'vi': "Xin chào, đây là bài kiểm tra hệ thống chuyển đổi giọng nói thành văn bản."
        }
        
        for lang, phrase in test_phrases.items():
            filename = f"test_audio_{lang}.wav"
            print(f"   Generating {filename}...")
            engine.save_to_file(phrase, filename)
            engine.runAndWait()
            print(f"   ✅ Generated {filename}")
        
        return True
        
    except ImportError:
        print("   ⚠️  pyttsx3 not available, skipping audio generation")
        print("   💡 You can manually place test audio files in the current directory")
        return False
    except Exception as e:
        print(f"   ❌ Error generating test audio: {e}")
        return False

def wait_for_service(max_retries=30, delay=2):
    """Wait for the service to be ready"""
    print("⏳ Waiting for service to be ready...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Service is ready!")
                return True
        except:
            pass
        
        print(f"   Attempt {attempt + 1}/{max_retries}, retrying in {delay}s...")
        time.sleep(delay)
    
    print("❌ Service failed to start within timeout period")
    return False

def main():
    """Main test function"""
    print("🚀 VOSK STT Service Test Suite")
    print("=" * 50)
    
    # Wait for service
    if not wait_for_service():
        return
    
    # Test health
    if not test_health():
        return
    
    print()
    
    # Test languages
    if not test_languages():
        return
    
    print()
    
    # Generate test audio if possible
    generate_test_audio()
    
    print()
    
    # Test transcription with available files
    test_files = [
        ("test_audio_en.wav", "en"),
        ("test_audio_vi.wav", "vi"),
        # Add any other test files you have
    ]
    
    for audio_file, language in test_files:
        if Path(audio_file).exists():
            test_transcription(audio_file, language)
            print()
    
    print("🎯 Test suite completed!")
    print("\n💡 Tips:")
    print("   - Place your own audio files in this directory to test them")
    print("   - Supported formats: WAV, MP3, FLAC, M4A, OGG")
    print("   - Use 16kHz, 16-bit, mono WAV for best results")
    print("   - Web interface available at: http://localhost:8000")

if __name__ == "__main__":
    main()
