#!/bin/bash

# Campaign Assistant - System Requirements Checker
# Checks for required tools and dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Tracking variables
ISSUES_FOUND=0
WARNINGS_FOUND=0

print_status() {
    local status=$1
    local message=$2
    local detail=$3
    
    case $status in
        "ok")
            echo -e "${GREEN}✅${NC} $message"
            ;;
        "warn")
            echo -e "${YELLOW}⚠️${NC}  $message"
            if [ -n "$detail" ]; then
                echo -e "   ${YELLOW}→${NC} $detail"
            fi
            ((WARNINGS_FOUND++))
            ;;
        "error")
            echo -e "${RED}❌${NC} $message"
            if [ -n "$detail" ]; then
                echo -e "   ${RED}→${NC} $detail"
            fi
            ((ISSUES_FOUND++))
            ;;
        "info")
            echo -e "${BLUE}ℹ️${NC}  $message"
            ;;
    esac
}

check_command() {
    local cmd=$1
    local name=$2
    local install_hint=$3
    local required=${4:-true}
    
    if command -v "$cmd" >/dev/null 2>&1; then
        local version=$($cmd --version 2>/dev/null | head -n1 || echo "unknown")
        print_status "ok" "$name found: $version"
        return 0
    else
        if [ "$required" = "true" ]; then
            print_status "error" "$name not found" "$install_hint"
            return 1
        else
            print_status "warn" "$name not found (optional)" "$install_hint"
            return 0
        fi
    fi
}

check_python_version() {
    if command -v python3 >/dev/null 2>&1; then
        local version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 9 ]; then
            print_status "ok" "Python $version (meets requirement ≥3.9)"
        else
            print_status "error" "Python $version found, but ≥3.9 required" "brew install python@3.11"
        fi
    else
        print_status "error" "Python 3 not found" "brew install python@3.11"
    fi
}

check_memory() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local memory_gb=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
        if [ "$memory_gb" -ge 8 ]; then
            print_status "ok" "Memory: ${memory_gb}GB (recommended ≥8GB)"
        elif [ "$memory_gb" -ge 4 ]; then
            print_status "warn" "Memory: ${memory_gb}GB (minimum 4GB, recommended ≥8GB)" "Consider closing other applications"
        else
            print_status "error" "Memory: ${memory_gb}GB (minimum 4GB required)" "Upgrade RAM or use cloud deployment"
        fi
    else
        print_status "info" "Memory check not available on this platform"
    fi
}

check_disk_space() {
    local available=$(df -h . | awk 'NR==2 {print $4}' | sed 's/[^0-9.]//g')
    local available_num=$(echo $available | cut -d. -f1)
    
    if [ "$available_num" -ge 5 ]; then
        print_status "ok" "Disk space: ${available}GB available"
    elif [ "$available_num" -ge 2 ]; then
        print_status "warn" "Disk space: ${available}GB available (minimum 2GB, recommended ≥5GB)" "Consider cleaning up disk space"
    else
        print_status "error" "Disk space: ${available}GB available (minimum 2GB required)" "Free up disk space"
    fi
}

check_brew() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            print_status "ok" "Homebrew found: $(brew --version | head -n1)"
        else
            print_status "warn" "Homebrew not found (recommended for macOS)" "Install from https://brew.sh/"
        fi
    fi
}

check_git() {
    check_command "git" "Git" "brew install git" true
}

check_optional_tools() {
    print_status "info" "Checking optional tools..."
    check_command "ollama" "Ollama (for local LLMs)" "brew install ollama" false
    check_command "docker" "Docker (for containerized deployment)" "brew install docker" false
    check_command "node" "Node.js (for web interface)" "brew install node" false
}

check_network() {
    print_status "info" "Checking network connectivity..."
    
    # Check basic internet
    if curl -s --max-time 5 https://www.google.com >/dev/null 2>&1; then
        print_status "ok" "Internet connectivity"
    else
        print_status "warn" "Internet connectivity issues" "Check network connection"
    fi
    
    # Check PyPI access
    if curl -s --max-time 5 https://pypi.org >/dev/null 2>&1; then
        print_status "ok" "PyPI accessible"
    else
        print_status "warn" "PyPI not accessible" "Check firewall/proxy settings"
    fi
}

main() {
    echo "🔍 Campaign Assistant - System Requirements Check"
    echo "================================================="
    echo ""
    
    # Platform detection
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "info" "Platform: macOS ($(sw_vers -productVersion))"
    elif [[ "$OSTYPE" == "linux"* ]]; then
        print_status "info" "Platform: Linux"
    else
        print_status "warn" "Platform: $OSTYPE (may not be fully supported)"
    fi
    
    echo ""
    print_status "info" "Checking core requirements..."
    
    # Core requirements
    check_python_version
    check_git
    check_brew
    
    echo ""
    print_status "info" "Checking system resources..."
    
    # System resources
    check_memory
    check_disk_space
    
    echo ""
    check_network
    
    echo ""
    check_optional_tools
    
    echo ""
    echo "📊 Summary"
    echo "=========="
    
    if [ $ISSUES_FOUND -eq 0 ] && [ $WARNINGS_FOUND -eq 0 ]; then
        print_status "ok" "All checks passed! System ready for Campaign Assistant."
    elif [ $ISSUES_FOUND -eq 0 ]; then
        print_status "warn" "$WARNINGS_FOUND warning(s) found, but system should work."
    else
        print_status "error" "$ISSUES_FOUND critical issue(s) found, $WARNINGS_FOUND warning(s)."
        echo ""
        echo "💡 Next steps:"
        echo "   • Run 'make doctor' for detailed fix suggestions"
        echo "   • Run 'make fix-macos' to auto-fix common macOS issues"
        exit 1
    fi
}

main "$@"