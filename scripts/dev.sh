#!/bin/bash
# Campaign Assistant - Development Script
# Quick development environment setup and common tasks

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[DEV]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Set development environment
export CAMPAIGN_ENV=development

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    print_status "Virtual environment activated"
else
    print_status "No venv found - run ./scripts/setup.sh first"
    exit 1
fi

# Function to show available commands
show_help() {
    echo "Campaign Assistant - Development Helper"
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  install    - Install/update dependencies"
    echo "  test       - Run tests"
    echo "  lint       - Check code formatting"
    echo "  format     - Format code with black"
    echo "  clean      - Clean up data and caches"
    echo "  models     - Show model status"
    echo "  demo       - Run demo with sample data"
    echo "  shell      - Start interactive Python shell"
    echo
}

# Install dependencies
install_deps() {
    print_status "Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.deps_installed
    print_status "Dependencies updated ✓"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    if [ -f "test_campaign.py" ]; then
        python -m pytest test_campaign.py -v
    else
        print_info "No tests found"
    fi
}

# Code formatting
lint_code() {
    print_status "Checking code formatting..."
    python -m black --check src/ main.py
    print_status "Code formatting check complete"
}

format_code() {
    print_status "Formatting code..."
    python -m black src/ main.py
    print_status "Code formatted ✓"
}

# Clean up
clean_data() {
    print_status "Cleaning up development data..."
    rm -rf data/dev_*
    rm -rf data/local_*
    rm -rf __pycache__ src/__pycache__ src/*/__pycache__
    print_status "Development data cleaned ✓"
}

# Show model status
show_models() {
    print_status "Checking model status..."
    python main.py models
}

# Demo with sample data
run_demo() {
    print_status "Running demo..."
    
    # Check if we have sample data
    if [ ! -d "test_data" ]; then
        print_info "Creating sample data..."
        mkdir -p test_data
        echo "# Sample Campaign Document" > test_data/sample.md
        echo "This is a test document for the campaign assistant." >> test_data/sample.md
        echo "It contains information about NPCs, locations, and plot hooks." >> test_data/sample.md
    fi
    
    # Ingest sample data
    print_status "Ingesting sample data..."
    python main.py ingest test_data/
    
    # Show stats
    print_status "Showing collection stats..."
    python main.py stats
    
    # Example search
    print_status "Example search..."
    python main.py search "campaign"
}

# Interactive shell
start_shell() {
    print_status "Starting interactive Python shell..."
    print_info "Campaign Assistant modules available:"
    print_info "  from src.config.settings import get_settings"
    print_info "  from src.storage.vector_store import VectorStore"
    print_info "  from src.llm.service_factory import LLMServiceFactory"
    echo
    python -i -c "
import sys
sys.path.append('.')
from src.config.settings import get_settings
print('Campaign Assistant development shell')
print('Settings loaded:', get_settings().app.name)
"
}

# Main execution
case "${1:-help}" in
    "install")
        install_deps
        ;;
    "test")
        run_tests
        ;;
    "lint")
        lint_code
        ;;
    "format")
        format_code
        ;;
    "clean")
        clean_data
        ;;
    "models")
        show_models
        ;;
    "demo")
        run_demo
        ;;
    "shell")
        start_shell
        ;;
    "help"|*)
        show_help
        ;;
esac