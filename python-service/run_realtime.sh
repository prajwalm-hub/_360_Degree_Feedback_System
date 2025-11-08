#!/bin/bash

# Real-Time NewsScope India Runner
# This script manages the real-time AI-powered news monitoring system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi

    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Found Python $python_version"
}

# Check if Redis is running
check_redis() {
    if ! command -v redis-cli &> /dev/null; then
        print_warning "Redis CLI not found. Please install Redis."
        return 1
    fi

    if ! redis-cli ping &> /dev/null; then
        print_error "Redis server is not running. Please start Redis:"
        print_error "  redis-server"
        exit 1
    fi

    print_success "Redis is running"
}

# Install dependencies
install_deps() {
    print_status "Installing Python dependencies..."

    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found. Make sure you're in the python-service directory."
        exit 1
    fi

    pip3 install -r requirements.txt
    print_success "Dependencies installed successfully"
}

# Setup environment
setup_env() {
    print_status "Setting up environment..."

    # Create logs directory
    mkdir -p logs

    # Download required NLTK data
    print_status "Downloading NLTK data..."
    python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')" 2>/dev/null || true

    print_success "Environment setup completed"
}

# Start Redis (if available)
start_redis() {
    if command -v redis-server &> /dev/null; then
        print_status "Starting Redis server..."
        redis-server --daemonize yes --port 6379
        sleep 2
        print_success "Redis started"
    else
        print_warning "Redis server not found. Please install Redis separately."
    fi
}

# Start the real-time system
start_system() {
    print_status "Starting Real-Time News Monitoring System..."

    case "$1" in
        "full")
            print_status "Starting complete system (collector + processor + websocket)..."
            python3 realtime_main.py
            ;;
        "collector")
            print_status "Starting news collector only..."
            python3 -c "
import asyncio
from realtime_collector import RealTimeCollector
import redis.asyncio as redis

async def main():
    redis_client = redis.Redis(decode_responses=True)
    async with RealTimeCollector(redis_client) as collector:
        await collector.start_collection()

asyncio.run(main())
"
            ;;
        "processor")
            print_status "Starting AI processor only..."
            python3 -c "
import asyncio
from queue_manager import initialize_queue_system, queue_manager

async def main():
    await initialize_queue_system()
    await queue_manager.start_processing()

asyncio.run(main())
"
            ;;
        "websocket")
            print_status "Starting WebSocket server only..."
            python3 -c "
import asyncio
from websocket_server import start_websocket_server

asyncio.run(start_websocket_server())
"
            ;;
        *)
            print_error "Invalid mode. Use: full, collector, processor, or websocket"
            exit 1
            ;;
    esac
}

# Show help
show_help() {
    echo "Real-Time NewsScope India System"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install       Install Python dependencies"
    echo "  setup         Setup environment and download models"
    echo "  start-redis   Start Redis server"
    echo "  start-full    Start complete real-time system"
    echo "  start-collector Start news collector only"
    echo "  start-processor Start AI processor only"
    echo "  start-websocket Start WebSocket server only"
    echo "  status        Check system status"
    echo "  test          Run basic tests"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install && $0 setup    # First time setup"
    echo "  $0 start-redis            # Start Redis"
    echo "  $0 start-full             # Start everything"
    echo "  $0 start-collector        # Start only collector for testing"
}

# Check system status
check_status() {
    print_status "Checking system status..."

    # Check Python
    check_python

    # Check Redis
    check_redis

    # Check if services are running
    if pgrep -f "realtime_main.py" > /dev/null; then
        print_success "Main system is running"
    else
        print_warning "Main system is not running"
    fi

    if pgrep -f "python.*realtime_collector" > /dev/null; then
        print_success "News collector is running"
    else
        print_warning "News collector is not running"
    fi

    if lsof -i :8765 > /dev/null 2>&1; then
        print_success "WebSocket server is running on port 8765"
    else
        print_warning "WebSocket server is not running"
    fi
}

# Run basic tests
run_tests() {
    print_status "Running basic system tests..."

    # Test imports
    python3 -c "
try:
    from realtime_collector import RealTimeCollector
    from advanced_nlp import AdvancedNLPProcessor
    from queue_manager import QueueManager
    from websocket_server import NewsWebSocketServer
    print('✓ All imports successful')
except ImportError as e:
    print('✗ Import error:', e)
    exit(1)
"

    # Test Redis connection
    python3 -c "
import redis
try:
    r = redis.Redis()
    r.ping()
    print('✓ Redis connection successful')
except Exception as e:
    print('✗ Redis connection failed:', e)
"

    # Test AI models (basic)
    python3 -c "
import asyncio
from advanced_nlp import nlp_processor

async def test():
    try:
        info = await nlp_processor.get_model_info()
        print('✓ AI models loaded:', info['models'])
    except Exception as e:
        print('✗ AI model loading failed:', e)

asyncio.run(test())
"

    print_success "Basic tests completed"
}

# Main script logic
main() {
    # Change to script directory
    cd "$(dirname "$0")"

    case "$1" in
        "install")
            check_python
            install_deps
            ;;
        "setup")
            check_python
            setup_env
            ;;
        "start-redis")
            start_redis
            ;;
        "start-full")
            check_python
            check_redis
            start_system "full"
            ;;
        "start-collector")
            check_python
            check_redis
            start_system "collector"
            ;;
        "start-processor")
            check_python
            check_redis
            start_system "processor"
            ;;
        "start-websocket")
            check_python
            start_system "websocket"
            ;;
        "status")
            check_status
            ;;
        "test")
            check_python
            run_tests
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            print_error "No command specified. Use '$0 help' for usage information."
            exit 1
            ;;
        *)
            print_error "Unknown command: $1. Use '$0 help' for usage information."
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
