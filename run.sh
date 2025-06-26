#!/bin/bash

# VOSK STT Service Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service configuration
SERVICE_NAME="vosk-stt"
IMAGE_NAME="truongginjs/stt"
PORT=8000
HEALTH_URL="http://localhost:${PORT}/health"

print_header() {
    echo -e "${BLUE}🎤 VOSK Speech-to-Text Service${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

wait_for_service() {
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for service to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$HEALTH_URL" > /dev/null 2>&1; then
            print_status "Service is ready! 🎉"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "Service failed to start within timeout"
    return 1
}

build_service() {
    print_status "Building VOSK STT service..."
    docker-compose build
    
    if [ $? -eq 0 ]; then
        print_status "Build completed successfully ✅"
    else
        print_error "Build failed ❌"
        exit 1
    fi
}

build_multiplatform() {
    print_status "Building multi-platform VOSK STT service..."
    
    # Check if buildx is available
    if ! docker buildx version &> /dev/null; then
        print_error "Docker buildx is not available. Please update Docker to a newer version."
        exit 1
    fi
    
    # Create builder if it doesn't exist
    docker buildx create --name multiarch --driver docker-container --use 2>/dev/null || true
    docker buildx inspect --bootstrap
    
    # Build for multiple platforms
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag "${IMAGE_NAME}:latest" \
        --push \
        .
    
    if [ $? -eq 0 ]; then
        print_status "Multi-platform build completed successfully ✅"
    else
        print_error "Multi-platform build failed ❌"
        exit 1
    fi
}

start_service() {
    print_status "Starting VOSK STT service..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_status "Service started successfully ✅"
        wait_for_service
        
        if [ $? -eq 0 ]; then
            print_status "Service URLs:"
            echo "  🌐 Web Interface: http://localhost:${PORT}"
            echo "  📚 API Docs:     http://localhost:${PORT}/docs"
            echo "  ❤️  Health Check: http://localhost:${PORT}/health"
            echo "  🔍 Languages:    http://localhost:${PORT}/languages"
        fi
    else
        print_error "Failed to start service ❌"
        exit 1
    fi
}

stop_service() {
    print_status "Stopping VOSK STT service..."
    docker-compose down
    
    if [ $? -eq 0 ]; then
        print_status "Service stopped successfully ✅"
    else
        print_error "Failed to stop service ❌"
        exit 1
    fi
}

restart_service() {
    print_status "Restarting VOSK STT service..."
    stop_service
    start_service
}

show_logs() {
    print_status "Showing service logs (Press Ctrl+C to exit)..."
    docker-compose logs -f
}

show_status() {
    print_status "Service status:"
    docker-compose ps
    
    echo ""
    print_status "Health check:"
    if curl -s -f "$HEALTH_URL" > /dev/null 2>&1; then
        response=$(curl -s "$HEALTH_URL")
        echo "✅ Service is healthy"
        echo "Response: $response"
    else
        echo "❌ Service is not responding"
    fi
}

cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_status "Cleanup completed ✅"
}

test_service() {
    print_status "Running service tests..."
    
    if [ -f "test_service.py" ]; then
        python3 test_service.py
    else
        print_warning "test_service.py not found, running basic health check..."
        
        if curl -s -f "$HEALTH_URL" > /dev/null 2>&1; then
            response=$(curl -s "$HEALTH_URL")
            print_status "Health check passed ✅"
            echo "Response: $response"
        else
            print_error "Health check failed ❌"
        fi
    fi
}

tag_image() {
    local version="${1:-latest}"
    print_status "Tagging image as ${IMAGE_NAME}:${version}..."
    
    # Tag the image
    docker tag "${IMAGE_NAME}:latest" "${IMAGE_NAME}:${version}"
    
    if [ $? -eq 0 ]; then
        print_status "Image tagged successfully ✅"
        print_status "Available tags:"
        docker images "${IMAGE_NAME}"
    else
        print_error "Failed to tag image ❌"
        exit 1
    fi
}

push_image() {
    local version="${1:-latest}"
    print_status "Pushing ${IMAGE_NAME}:${version} to Docker Hub..."
    
    # Check if user is logged in to Docker Hub
    if ! docker info | grep -q "Username:"; then
        print_warning "You may need to login to Docker Hub first:"
        echo "  docker login"
        echo ""
    fi
    
    # Push the image
    docker push "${IMAGE_NAME}:${version}"
    
    if [ $? -eq 0 ]; then
        print_status "Image pushed successfully ✅"
        print_status "Image available at: https://hub.docker.com/r/${IMAGE_NAME}"
    else
        print_error "Failed to push image ❌"
        exit 1
    fi
}

build_and_push() {
    local version="${1:-latest}"
    print_status "Building and pushing ${IMAGE_NAME}:${version}..."
    
    # Build the image
    build_service
    
    # Tag if not latest
    if [ "$version" != "latest" ]; then
        tag_image "$version"
    fi
    
    # Push to Docker Hub
    push_image "$version"
}

show_help() {
    echo "Usage: $0 [COMMAND] [VERSION]"
    echo ""
    echo "Commands:"
    echo "  build           Build the Docker image (current platform)"
    echo "  build-multi     Build multi-platform image (amd64 + arm64) and push"
    echo "  start           Start the service"
    echo "  stop            Stop the service"
    echo "  restart         Restart the service"
    echo "  logs            Show service logs"
    echo "  status          Show service status"
    echo "  test            Test the service"
    echo "  cleanup         Clean up Docker resources"
    echo "  tag [VERSION]   Tag the image (default: latest)"
    echo "  push [VERSION]  Push image to Docker Hub (default: latest)"
    echo "  publish [VERSION] Build, tag and push to Docker Hub (default: latest)"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build           # Build for current platform"
    echo "  $0 build-multi     # Build for amd64 + arm64 and push"
    echo "  $0 start           # Start the service"
    echo "  $0 publish         # Build and push to Docker Hub as latest"
    echo "  $0 publish v1.0    # Build and push to Docker Hub as v1.0"
    echo ""
    echo "Docker Hub: https://hub.docker.com/r/${IMAGE_NAME}"
}

# Main script logic
main() {
    print_header
    
    # Check prerequisites
    check_docker
    
    # Handle commands
    case "${1:-help}" in
        "build")
            build_service
            ;;
        "build-multi")
            build_multiplatform
            ;;
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "test")
            test_service
            ;;
        "cleanup")
            cleanup
            ;;
        "tag")
            tag_image "$2"
            ;;
        "push")
            push_image "$2"
            ;;
        "publish")
            build_and_push "$2"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run the script
main "$@"
