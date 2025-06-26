#!/bin/bash

# Multi-platform Docker build script for VOSK STT
# This script builds images for both AMD64 and ARM64 architectures

set -e

IMAGE_NAME="truongginjs/stt"
VERSION="${1:-latest}"

echo "🐳 Building multi-platform Docker image: ${IMAGE_NAME}:${VERSION}"
echo "📋 Target platforms: linux/amd64, linux/arm64"

# Check if buildx is available
if ! docker buildx version &> /dev/null; then
    echo "❌ Error: Docker buildx is not available."
    echo "Please update Docker to a newer version that supports buildx."
    exit 1
fi

# Check if user is logged in
if ! docker info | grep -q "Username:"; then
    echo "⚠️  Warning: You may need to login to Docker Hub first:"
    echo "   docker login"
    echo ""
fi

# Create and use buildx builder
echo "🔧 Setting up buildx builder..."
docker buildx create --name multiarch --driver docker-container --use 2>/dev/null || true
docker buildx inspect --bootstrap

# Build and push for multiple platforms
echo "🚀 Building and pushing ${IMAGE_NAME}:${VERSION}..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag "${IMAGE_NAME}:${VERSION}" \
    --push \
    .

if [ $? -eq 0 ]; then
    echo "✅ Multi-platform build completed successfully!"
    echo "📦 Image available at: https://hub.docker.com/r/${IMAGE_NAME}"
    echo "🔍 Supported platforms: linux/amd64, linux/arm64"
    echo ""
    echo "Usage:"
    echo "  docker pull ${IMAGE_NAME}:${VERSION}"
    echo "  docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
else
    echo "❌ Multi-platform build failed"
    exit 1
fi
