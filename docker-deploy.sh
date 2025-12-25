#!/bin/bash
# Docker Build & Deploy Script for Cinema AI Backend

set -e  # Exit on error

echo "🐳 Cinema AI Backend - Docker Deployment"
echo "========================================"

# Configuration
IMAGE_NAME="cinema-ai-backend"
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-your-dockerhub-username}"
PORT="${PORT:-8000}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# TASK 2: Build Docker Image
build_image() {
    print_step "Building Docker image..."
    docker build -t $IMAGE_NAME .
    print_success "Docker image built successfully!"
}

# TASK 2: Run Docker Container Locally
run_local() {
    print_step "Running container locally on port $PORT..."
    docker run -d \
        --name $IMAGE_NAME \
        -p $PORT:8000 \
        --restart unless-stopped \
        $IMAGE_NAME
    print_success "Container running at http://localhost:$PORT"
    echo "Test health endpoint: curl http://localhost:$PORT/health"
}

# Stop and remove existing container
stop_local() {
    print_step "Stopping existing container..."
    docker stop $IMAGE_NAME 2>/dev/null || true
    docker rm $IMAGE_NAME 2>/dev/null || true
    print_success "Container stopped and removed"
}

# TASK 3: Push to DockerHub
push_dockerhub() {
    if [ "$DOCKERHUB_USERNAME" = "your-dockerhub-username" ]; then
        print_error "Please set DOCKERHUB_USERNAME environment variable"
        echo "Example: export DOCKERHUB_USERNAME=stalinSaga04"
        exit 1
    fi
    
    print_step "Logging into DockerHub..."
    docker login
    
    print_step "Tagging image..."
    docker tag $IMAGE_NAME $DOCKERHUB_USERNAME/$IMAGE_NAME:latest
    
    print_step "Pushing to DockerHub..."
    docker push $DOCKERHUB_USERNAME/$IMAGE_NAME:latest
    
    print_success "Image pushed to DockerHub!"
    echo "Image URL: $DOCKERHUB_USERNAME/$IMAGE_NAME:latest"
}

# Show usage
usage() {
    echo "Usage: ./docker-deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build       - Build Docker image"
    echo "  run         - Run container locally"
    echo "  stop        - Stop local container"
    echo "  restart     - Stop, rebuild, and run"
    echo "  push        - Push to DockerHub"
    echo "  full        - Build, run, and push (complete workflow)"
    echo ""
    echo "Environment Variables:"
    echo "  DOCKERHUB_USERNAME - Your DockerHub username"
    echo "  PORT               - Local port (default: 8000)"
}

# Main script logic
case "${1:-}" in
    build)
        build_image
        ;;
    run)
        run_local
        ;;
    stop)
        stop_local
        ;;
    restart)
        stop_local
        build_image
        run_local
        ;;
    push)
        push_dockerhub
        ;;
    full)
        build_image
        run_local
        echo ""
        read -p "Test the app, then press Enter to push to DockerHub..."
        push_dockerhub
        ;;
    *)
        usage
        exit 1
        ;;
esac
