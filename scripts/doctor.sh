#!/bin/bash

# Campaign Assistant - System Doctor
# Diagnoses common issues and provides detailed fix instructions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}🩺 $1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

print_fix() {
    local title=$1
    local commands=$2
    
    echo -e "${YELLOW}🔧 $title${NC}"
    echo -e "${GREEN}$commands${NC}"
    echo ""
}

check_and_diagnose_python() {
    print_header "Python Diagnosis"
    
    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ Python 3 not found"
        print_fix "Install Python 3.11" "brew install python@3.11"
        return
    fi
    
    local version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    
    if [ "$major" -eq 3 ] && [ "$minor" -lt 9 ]; then
        echo "❌ Python $version found, but ≥3.9 required"
        print_fix "Upgrade Python" "brew install python@3.11
brew unlink python@3.9  # if needed
brew link python@3.11"
        return
    fi
    
    # Check for common Python issues
    if ! python3 -c "import venv" 2>/dev/null; then
        echo "❌ Python venv module missing"
        print_fix "Install Python with venv support" "brew reinstall python@3.11"
    fi
    
    if ! python3 -c "import pip" 2>/dev/null; then
        echo "❌ pip not available"
        print_fix "Install pip" "python3 -m ensurepip --upgrade"
    fi
    
    echo "✅ Python installation looks good"
}

check_and_diagnose_dependencies() {
    print_header "Dependency Diagnosis"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "⚠️ Virtual environment not found"
        print_fix "Create virtual environment" "python3 -m venv venv"
        return
    fi
    
    # Check if virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "⚠️ Virtual environment not activated"
        print_fix "Activate virtual environment" "source venv/bin/activate"
    fi
    
    # Check key dependencies
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || true
        
        local missing_deps=()
        
        if ! python -c "import chromadb" 2>/dev/null; then
            missing_deps+=("chromadb")
        fi
        
        if ! python -c "import sentence_transformers" 2>/dev/null; then
            missing_deps+=("sentence-transformers")
        fi
        
        if ! python -c "import yaml" 2>/dev/null; then
            missing_deps+=("pyyaml")
        fi
        
        if [ ${#missing_deps[@]} -gt 0 ]; then
            echo "❌ Missing dependencies: ${missing_deps[*]}"
            print_fix "Install dependencies" "source venv/bin/activate
pip install ${missing_deps[*]}"
        else
            echo "✅ Core dependencies installed"
        fi
    fi
}

check_and_diagnose_permissions() {
    print_header "Permissions Diagnosis"
    
    # Check write permissions for data directory
    if [ ! -w "." ]; then
        echo "❌ No write permission in current directory"
        print_fix "Fix permissions" "sudo chown -R \$(whoami) ."
    fi
    
    # Check if we can create directories
    if ! mkdir -p "data/test" 2>/dev/null; then
        echo "❌ Cannot create data directories"
        print_fix "Fix directory permissions" "sudo chown -R \$(whoami) .
chmod -R u+w ."
    else
        rmdir "data/test" 2>/dev/null || true
        echo "✅ Directory permissions OK"
    fi
}

check_and_diagnose_memory() {
    print_header "Memory Diagnosis"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local memory_gb=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
        local memory_pressure=$(memory_pressure | grep "System-wide memory free percentage" | awk '{print $5}' | sed 's/%//')
        
        echo "💾 Total RAM: ${memory_gb}GB"
        
        if [ -n "$memory_pressure" ]; then
            echo "💾 Memory free: ${memory_pressure}%"
            
            if [ "$memory_pressure" -lt 20 ]; then
                echo "⚠️ Low memory warning"
                print_fix "Free up memory" "# Close unnecessary applications
# Or restart your system
sudo purge  # Clear disk cache"
            fi
        fi
        
        if [ "$memory_gb" -lt 4 ]; then
            echo "❌ Insufficient RAM for optimal performance"
            print_fix "Memory recommendations" "# Consider:
# • Closing other applications
# • Using cloud deployment
# • Upgrading RAM"
        fi
    fi
}

check_and_diagnose_network() {
    print_header "Network Diagnosis"
    
    # Test basic connectivity
    if ! curl -s --max-time 5 https://www.google.com >/dev/null 2>&1; then
        echo "❌ No internet connectivity"
        print_fix "Network troubleshooting" "# Check:
# • WiFi/ethernet connection
# • VPN settings
# • Firewall settings
ping google.com"
        return
    fi
    
    # Test PyPI connectivity
    if ! curl -s --max-time 5 https://pypi.org >/dev/null 2>&1; then
        echo "❌ Cannot reach PyPI"
        print_fix "PyPI connectivity" "# Check:
# • Corporate firewall
# • Proxy settings
# • DNS settings
curl -v https://pypi.org"
    fi
    
    # Test model download capability
    if ! curl -s --max-time 10 -I https://huggingface.co >/dev/null 2>&1; then
        echo "⚠️ Cannot reach Hugging Face (model downloads may fail)"
        print_fix "Model download fallback" "# If model downloads fail:
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1"
    fi
    
    echo "✅ Network connectivity OK"
}

check_and_diagnose_disk() {
    print_header "Disk Space Diagnosis"
    
    local available=$(df -h . | awk 'NR==2 {print $4}' | sed 's/[^0-9.]//g')
    local used_percent=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    echo "💿 Available space: ${available}GB"
    echo "💿 Disk usage: ${used_percent}%"
    
    if [ "$used_percent" -gt 90 ]; then
        echo "❌ Disk almost full"
        print_fix "Free up disk space" "# Clean up options:
du -sh * | sort -h  # Find large directories
brew cleanup        # Clean Homebrew cache
pip cache purge     # Clean pip cache
rm -rf ~/.Trash/*   # Empty trash"
    fi
    
    # Check for specific large directories
    if [ -d "$HOME/Library/Caches" ]; then
        local cache_size=$(du -sh "$HOME/Library/Caches" 2>/dev/null | cut -f1)
        echo "📁 Cache directory: $cache_size"
    fi
}

run_performance_test() {
    print_header "Performance Test"
    
    echo "🧪 Running quick performance test..."
    
    # Test Python import speed
    local python_time=$(time (python3 -c "import sys, time; print('Python OK')") 2>&1 | grep real | awk '{print $2}')
    echo "⏱️ Python startup: $python_time"
    
    # Test if we can import key libraries quickly
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || true
        local import_time=$(time (python -c "import chromadb, sentence_transformers; print('Imports OK')" 2>/dev/null) 2>&1 | grep real | awk '{print $2}')
        if [ -n "$import_time" ]; then
            echo "⏱️ Library imports: $import_time"
        else
            echo "❌ Library import test failed (dependencies not installed?)"
        fi
    fi
}

suggest_optimizations() {
    print_header "Performance Optimizations"
    
    echo "💡 Suggestions for better performance:"
    echo ""
    
    # macOS specific optimizations
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍎 macOS Optimizations:"
        print_fix "Disable unnecessary visual effects" "# System Preferences → Accessibility → Display → Reduce Motion"
        
        print_fix "Optimize for performance" "# Close unnecessary browser tabs
# Quit unused applications
# Disable Spotlight indexing for project directory:
sudo mdutil -i off ."
    fi
    
    # Project specific optimizations
    echo "🎲 Campaign Assistant Optimizations:"
    print_fix "Use smaller embedding model for testing" "# Edit config/development.yaml:
embeddings:
  model:
    name: \"all-MiniLM-L6-v2\"  # Smaller, faster model"
    
    print_fix "Reduce chunk sizes for testing" "# Edit config/development.yaml:
processing:
  chunking:
    chunk_size: 500
    chunk_overlap: 50"
}

main() {
    echo "🩺 Campaign Assistant - System Doctor"
    echo "====================================="
    echo ""
    
    # Run all diagnostic checks
    check_and_diagnose_python
    echo ""
    
    check_and_diagnose_dependencies
    echo ""
    
    check_and_diagnose_permissions
    echo ""
    
    check_and_diagnose_memory
    echo ""
    
    check_and_diagnose_network
    echo ""
    
    check_and_diagnose_disk
    echo ""
    
    run_performance_test
    echo ""
    
    suggest_optimizations
    
    echo ""
    print_header "Next Steps"
    echo "🚀 If issues persist:"
    echo "   • Run 'make fix-macos' for automated fixes"
    echo "   • Check the troubleshooting guide in README.md"
    echo "   • Open an issue on GitHub with this diagnostic output"
}

main "$@"