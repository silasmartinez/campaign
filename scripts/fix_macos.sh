#!/bin/bash

# Campaign Assistant - macOS Auto-Fix Script
# Attempts to automatically resolve common macOS issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    local status=$1
    local message=$2
    
    case $status in
        "ok")
            echo -e "${GREEN}✅${NC} $message"
            ;;
        "info")
            echo -e "${BLUE}ℹ️${NC}  $message"
            ;;
        "warn")
            echo -e "${YELLOW}⚠️${NC}  $message"
            ;;
        "error")
            echo -e "${RED}❌${NC} $message"
            ;;
    esac
}

fix_homebrew() {
    print_status "info" "Checking Homebrew installation..."
    
    if ! command -v brew >/dev/null 2>&1; then
        print_status "info" "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add to PATH for Apple Silicon Macs
        if [[ $(uname -m) == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        
        print_status "ok" "Homebrew installed successfully"
    else
        print_status "ok" "Homebrew already installed"
        
        # Update Homebrew
        print_status "info" "Updating Homebrew..."
        brew update
        print_status "ok" "Homebrew updated"
    fi
}

fix_python() {
    print_status "info" "Checking Python installation..."
    
    if ! command -v python3 >/dev/null 2>&1; then
        print_status "info" "Installing Python..."
        brew install python@3.11
        brew link python@3.11
        print_status "ok" "Python installed"
    else
        local version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -lt 9 ]; then
            print_status "info" "Upgrading Python from $version to 3.11..."
            brew install python@3.11
            brew unlink python@3.9 python@3.8 2>/dev/null || true
            brew link python@3.11
            print_status "ok" "Python upgraded"
        else
            print_status "ok" "Python $version is suitable"
        fi
    fi
    
    # Ensure pip is available
    if ! python3 -m pip --version >/dev/null 2>&1; then
        print_status "info" "Installing pip..."
        python3 -m ensurepip --upgrade
        print_status "ok" "pip installed"
    fi
}

fix_git() {
    print_status "info" "Checking Git installation..."
    
    if ! command -v git >/dev/null 2>&1; then
        print_status "info" "Installing Git..."
        brew install git
        print_status "ok" "Git installed"
    else
        print_status "ok" "Git already installed"
    fi
}

fix_permissions() {
    print_status "info" "Fixing file permissions..."
    
    # Fix ownership of current directory
    if [ ! -w "." ]; then
        print_status "info" "Fixing directory ownership..."
        sudo chown -R $(whoami) .
    fi
    
    # Ensure scripts are executable
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x install.sh 2>/dev/null || true
    
    print_status "ok" "Permissions fixed"
}

fix_xcode_tools() {
    print_status "info" "Checking Xcode Command Line Tools..."
    
    if ! xcode-select -p >/dev/null 2>&1; then
        print_status "info" "Installing Xcode Command Line Tools..."
        xcode-select --install
        print_status "warn" "Xcode tools installation started - please complete in the popup dialog"
    else
        print_status "ok" "Xcode Command Line Tools already installed"
    fi
}

optimize_system() {
    print_status "info" "Applying system optimizations..."
    
    # Increase file descriptor limits for better performance
    if [ ! -f /etc/launchd.conf ] || ! grep -q "limit maxfiles" /etc/launchd.conf; then
        print_status "info" "Increasing file descriptor limits..."
        echo "limit maxfiles 65536 200000" | sudo tee -a /etc/launchd.conf >/dev/null
        print_status "warn" "File descriptor limits increased - restart required for full effect"
    fi
    
    # Clear system caches if disk space is low
    local available=$(df -h . | awk 'NR==2 {print $4}' | sed 's/[^0-9.]//g')
    if [ "${available%.*}" -lt 5 ]; then
        print_status "info" "Clearing system caches to free disk space..."
        sudo purge
        brew cleanup --prune=all
        pip cache purge 2>/dev/null || true
        print_status "ok" "System caches cleared"
    fi
}

install_optional_tools() {
    print_status "info" "Installing optional but recommended tools..."
    
    # Install Ollama for local LLM support
    if ! command -v ollama >/dev/null 2>&1; then
        print_status "info" "Installing Ollama (for local LLMs)..."
        brew install ollama
        print_status "ok" "Ollama installed"
    fi
    
    # Install jq for JSON processing (useful for debugging)
    if ! command -v jq >/dev/null 2>&1; then
        print_status "info" "Installing jq (JSON processor)..."
        brew install jq
        print_status "ok" "jq installed"
    fi
}

verify_fixes() {
    print_status "info" "Verifying fixes..."
    
    local issues=0
    
    # Check Python
    if ! python3 -c "import sys; assert sys.version_info >= (3, 9)" 2>/dev/null; then
        print_status "error" "Python version still inadequate"
        ((issues++))
    fi
    
    # Check pip
    if ! python3 -m pip --version >/dev/null 2>&1; then
        print_status "error" "pip still not working"
        ((issues++))
    fi
    
    # Check git
    if ! command -v git >/dev/null 2>&1; then
        print_status "error" "Git still not found"
        ((issues++))
    fi
    
    # Check brew
    if ! command -v brew >/dev/null 2>&1; then
        print_status "error" "Homebrew still not found"
        ((issues++))
    fi
    
    if [ $issues -eq 0 ]; then
        print_status "ok" "All critical tools are now available"
        return 0
    else
        print_status "error" "$issues issue(s) remain - manual intervention may be required"
        return 1
    fi
}

main() {
    echo "🔧 Campaign Assistant - macOS Auto-Fix"
    echo "======================================"
    echo ""
    
    # Check if we're on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_status "error" "This script is only for macOS systems"
        exit 1
    fi
    
    print_status "info" "Starting automated fixes for macOS..."
    echo ""
    
    # Run fixes in order of dependency
    fix_xcode_tools
    echo ""
    
    fix_homebrew
    echo ""
    
    fix_python
    echo ""
    
    fix_git
    echo ""
    
    fix_permissions
    echo ""
    
    optimize_system
    echo ""
    
    # Optional tools (don't fail if these don't work)
    set +e
    install_optional_tools
    set -e
    echo ""
    
    # Verify everything worked
    if verify_fixes; then
        echo ""
        print_status "ok" "🎉 Auto-fix completed successfully!"
        echo ""
        echo "Next steps:"
        echo "  1. Run 'make install' to install Campaign Assistant"
        echo "  2. Run 'make run-test' to verify everything works"
    else
        echo ""
        print_status "warn" "Some issues remain - run 'make doctor' for detailed diagnosis"
        exit 1
    fi
}

main "$@"