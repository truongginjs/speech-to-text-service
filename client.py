#!/usr/bin/env python3
"""
Simple client example for VOSK STT API
"""

import requests
import json
import sys
from pathlib import Path

class VOSKClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check if the service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200, response.json()
        except Exception as e:
            return False, str(e)
    
    def get_languages(self):
        """Get available languages"""
        try:
            response = requests.get(f"{self.base_url}/languages")
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def transcribe_file(self, file_path, language="en"):
        """Transcribe an audio file"""
        if not Path(file_path).exists():
            return False, f"File not found: {file_path}"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'language': language}
                response = requests.post(f"{self.base_url}/transcribe", 
                                       files=files, data=data)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  {sys.argv[0]} health                    # Check service health")
        print(f"  {sys.argv[0]} languages                 # List available languages")
        print(f"  {sys.argv[0]} transcribe <file> [lang]  # Transcribe audio file")
        print()
        print("Examples:")
        print(f"  {sys.argv[0]} health")
        print(f"  {sys.argv[0]} transcribe audio.wav en")
        print(f"  {sys.argv[0]} transcribe vietnamese.mp3 vi")
        sys.exit(1)
    
    client = VOSKClient()
    command = sys.argv[1]
    
    if command == "health":
        print("🔍 Checking service health...")
        success, result = client.health_check()
        if success:
            print("✅ Service is healthy")
            print(f"Details: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Service is not healthy: {result}")
    
    elif command == "languages":
        print("🌐 Getting available languages...")
        success, result = client.get_languages()
        if success:
            print("✅ Available languages:")
            print(f"{json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed to get languages: {result}")
    
    elif command == "transcribe":
        if len(sys.argv) < 3:
            print("❌ Please provide audio file path")
            sys.exit(1)
        
        file_path = sys.argv[2]
        language = sys.argv[3] if len(sys.argv) > 3 else "en"
        
        print(f"🎤 Transcribing {file_path} (language: {language})...")
        success, result = client.transcribe_file(file_path, language)
        
        if success:
            if result.get('success'):
                print("✅ Transcription completed:")
                print(f"Text: {result.get('text', 'N/A')}")
                print(f"Language: {result.get('language', 'N/A')}")
                print(f"Confidence: {result.get('confidence', 'N/A')}")
            else:
                print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed: {result}")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
