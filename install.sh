#!/bin/bash

# Campaign Assistant - Installation Script
# Creates virtual environment and installs dependencies

set -e  # Exit on any error

echo "🎲 Campaign Assistant - Installation"
echo "===================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Using Python $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install \
    chromadb==0.4.18 \
    langchain==0.1.4 \
    pypdf2==3.0.1 \
    python-multipart==0.0.6 \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    pydantic==2.5.2 \
    python-dotenv==1.0.0 \
    markdown==3.5.2 \
    beautifulsoup4==4.12.2 \
    requests==2.31.0 \
    sentence-transformers==2.7.0 \
    openai==1.6.1 \
    anthropic==0.8.1 \
    pytest==7.4.3 \
    black==23.12.1 \
    pyyaml==6.0.1

echo "✅ Dependencies installed successfully"

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Test installation
echo "🧪 Testing installation..."
python -c "
import chromadb
import sentence_transformers
import langchain
print('✅ All core dependencies imported successfully')
"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To use the Campaign Assistant:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the test suite:"
echo "     python test_campaign.py"
echo ""
echo "  3. Start using the tool:"
echo "     python main.py --help"
echo ""
echo "Happy campaigning! 🎲"