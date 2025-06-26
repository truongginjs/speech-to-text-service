FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    ffmpeg \
    portaudio19-dev \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create models directory
RUN mkdir -p /app/models

# Download VOSK models for Vietnamese and English
# English model (small)
RUN wget -O /tmp/vosk-model-small-en-us-0.15.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
    unzip /tmp/vosk-model-small-en-us-0.15.zip -d /app/models/ && \
    mv /app/models/vosk-model-small-en-us-0.15 /app/models/en && \
    rm /tmp/vosk-model-small-en-us-0.15.zip

# Vietnamese model (small) - using correct URL and model name
RUN wget -O /tmp/vosk-model-small-vn-0.4.zip https://alphacephei.com/vosk/models/vosk-model-small-vn-0.4.zip && \
    unzip /tmp/vosk-model-small-vn-0.4.zip -d /app/models/ && \
    mv /app/models/vosk-model-small-vn-0.4 /app/models/vi && \
    rm /tmp/vosk-model-small-vn-0.4.zip

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
