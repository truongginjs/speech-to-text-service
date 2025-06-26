# Platform Compatibility Fix

## Problem: "exec /usr/local/bin/python: exec format error"

This error occurs when the Docker image was built for a different CPU architecture than your server.

## Solution Options

### Option 1: Use Pre-built Multi-Platform Image (Recommended)

Use the pre-built image that supports both AMD64 and ARM64:

```bash
docker pull truongginjs/stt:latest
docker run -p 8000:8000 truongginjs/stt:latest
```

### Option 2: Build Multi-Platform Image

Build an image that works on both AMD64 and ARM64 servers:

```bash
# Using the helper script
./build-multiplatform.sh

# Or using the management script
./run.sh build-multi

# Or manually
docker buildx create --name multiarch --driver docker-container --use
docker buildx build --platform linux/amd64,linux/arm64 -t truongginjs/stt:latest --push .
```

### Option 3: Build for Specific Platform

If you know your server's architecture, build specifically for it:

```bash
# For AMD64 (x86_64) servers
docker buildx build --platform linux/amd64 -t truongginjs/stt:latest .

# For ARM64 servers  
docker buildx build --platform linux/arm64 -t truongginjs/stt:latest .
```

### Option 4: Check Your Server Architecture

To determine your server's architecture:

```bash
# On your server
uname -m
# x86_64 = AMD64
# aarch64 = ARM64

# Or using Docker
docker version --format '{{.Server.Arch}}'
```

## Updated Docker Compose

The `docker-compose.yml` now includes platform specification:

```yaml
version: '3.8'
services:
  vosk-stt:
    image: truongginjs/stt:latest
    platform: linux/amd64  # Specify platform if needed
    ports:
      - "8000:8000"
```

## Building on Different Platforms

- **Building on Mac M1/M2**: Creates ARM64 images by default
- **Building on Intel Mac/Linux**: Creates AMD64 images by default
- **Multi-platform build**: Creates both ARM64 and AMD64 images

Use multi-platform builds for maximum compatibility across different server types.
