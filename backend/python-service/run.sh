#!/bin/bash

# Government News Monitor - Python Service Runner
# This script helps manage the Python AI/ML service

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
    
    # Run setup script
    python3 setup.py
    print_success "Environment setup completed"
}

# Start the service
start_service() {
    print_status "Starting News Monitor Service..."
    
    case "$1" in
        "api")
            print_status "Starting API server..."
            python3 api_server.py
            ;;
        "scheduler")
            print_status "Starting with scheduler..."
            python3 main.py
            ;;
        "collect")
            print_status "Running news collection..."
            python3 main.py collect
            ;;
        "process")
            print_status "Running article processing..."
            python3 main.py process
            ;;
        "cycle")
            print_status "Running complete cycle..."
            python3 main.py cycle
            ;;
        *)
            print_error "Invalid mode. Use: api, scheduler, collect, process, or cycle"
            exit 1
            ;;
    esac
}

# Show help
show_help() {
    echo "Government News Monitor - Python Service"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install Python dependencies"
    echo "  setup       Setup environment and initialize database"
    echo "  start-api   Start the FastAPI server"
    echo "  start       Start the service with scheduler"
    echo "  collect     Run news collection once"
    echo "  process     Run article processing once"
    echo "  cycle       Run complete collection and processing cycle"
    echo "  status      Check service status"
    echo "  logs        Show recent logs"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install && $0 setup    # First time setup"
    echo "  $0 start-api              # Start API server"
    echo "  $0 start                  # Start with scheduler"
    echo "  $0 cycle                  # Run one complete cycle"
}

# Check service status
check_status() {
    print_status "Checking service status..."
    
    # Check if API server is running
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        print_success "API server is running at http://localhost:8000"
    else
        print_warning "API server is not running"
    fi
    
    # Check database
    if [ -f "../.wrangler/state/v3/d1/miniflare-D1DatabaseObject/db.sqlite" ]; then
        print_success "Database file exists"
    else
        print_warning "Database file not found"
    fi
    
    # Check recent logs
    if [ -f "logs/news_monitor.log" ]; then
        print_status "Recent log entries:"
        tail -5 logs/news_monitor.log
    else
        print_warning "No log file found"
    fi
}

# Show recent logs
show_logs() {
    if [ -f "logs/news_monitor.log" ]; then
        print_status "Showing recent logs..."
        tail -50 logs/news_monitor.log
    else
        print_warning "No log file found"
    fi
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
        "start-api")
            check_python
            start_service "api"
            ;;
        "start")
            check_python
            start_service "scheduler"
            ;;
        "collect")
            check_python
            start_service "collect"
            ;;
        "process")
            check_python
            start_service "process"
            ;;
        "cycle")
            check_python
            start_service "cycle"
            ;;
        "status")
            check_status
            ;;
        "logs")
            show_logs
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
