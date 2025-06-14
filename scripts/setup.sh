#!/bin/bash
# Campaign Assistant - Setup Script
# One-time setup for the campaign assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Campaign Assistant Setup${NC}"
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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

print_header

# Check system requirements
print_status "Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    print_error "Install Python 3.11+ from: https://python.org"
    exit 1
fi

python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    print_error "Python 3.11+ is required. You have Python $python_version"
    exit 1
fi
print_status "Python $python_version ✓"

# Setup virtual environment
print_status "Setting up virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Recreating..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
touch venv/.deps_installed

# Create data directories
print_status "Creating data directories..."
mkdir -p data/{uploads,processed,chroma_db,models,logs}

# Check optional dependencies
print_status "Checking optional dependencies..."

# Check Ollama
if command -v ollama &> /dev/null; then
    print_status "Ollama found ✓"
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_status "Ollama is running ✓"
    else
        print_warning "Ollama found but not running"
        print_status "To start Ollama: ollama serve"
    fi
    
    # Suggest models to install
    echo
    print_status "Recommended models to install:"
    echo "  ollama pull llama3.1:8b      # Best overall model"
    echo "  ollama pull mistral:7b       # Creative content"
    echo "  ollama pull llama3.2:3b      # Fast development"
    echo
else
    print_warning "Ollama not found"
    print_status "Install Ollama from: https://ollama.ai"
    print_status "LLM features will be disabled without Ollama"
fi

# Test basic functionality
print_status "Testing basic functionality..."
if python3 main.py stats >/dev/null 2>&1; then
    print_status "Basic functionality test ✓"
else
    print_warning "Basic functionality test failed - check dependencies"
fi

# Create executable symlink or script
print_status "Setting up command-line access..."
if [ -w "/usr/local/bin" ]; then
    ln -sf "$PROJECT_DIR/campaign" "/usr/local/bin/campaign"
    print_status "Command 'campaign' available globally ✓"
else
    print_warning "Cannot create global command. Add to PATH manually:"
    echo "  export PATH=\"$PROJECT_DIR:\$PATH\""
fi

# Final instructions
echo
print_status "🎉 Setup complete!"
echo
echo "Quick start:"
echo "  ./campaign --help                    # Show help"
echo "  ./campaign stats                     # Check status"
echo "  ./campaign ingest path/to/docs       # Add documents"
echo "  ./campaign ask 'Tell me about...'    # Ask questions (requires Ollama)"
echo
echo "Environment:"
echo "  CAMPAIGN_ENV=development   # Use development settings"
echo "  CAMPAIGN_ENV=production    # Use production settings"
echo
if ! command -v ollama &> /dev/null; then
    print_warning "Install Ollama for AI features: https://ollama.ai"
fi