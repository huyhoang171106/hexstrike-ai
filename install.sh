#!/bin/bash

# =============================================================================
# HexStrike AI MCP v6.0 - Complete Auto Install Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_NAME="hexstrike_env"

print_banner() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║     ██████╗ ███████╗████████╗██████╗  ██████╗                 ║"
    echo "║     ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔═══██╗                ║"
    echo "║     ██████╔╝█████╗     ██║   ██████╔╝██║   ██║                ║"
    echo "║     ██╔══██╗██╔══╝     ██║   ██╔══██╗██║   ██║                ║"
    echo "║     ██║  ██║███████╗   ██║   ██║  ██║╚██████╔╝                ║"
    echo "║     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝                 ║"
    echo "║                                                               ║"
    echo "║           AI MCP Cybersecurity Automation Platform            ║"
    echo "║                      Version 6.0.0                           ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
}

print_step() {
    echo "[$1/$2] $3"
}

print_success() {
    echo "[OK] $1"
}

print_warning() {
    echo "[WARNING] $1"
}

print_error() {
    echo "[ERROR] $1"
}

print_info() {
    echo "[INFO] $1"
}

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS="$ID"
        OS_VERSION="$VERSION_ID"
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS="$DISTRIB_ID"
        OS_VERSION="$DISTRIB_RELEASE"
    elif [ "$(uname)" = "Darwin" ]; then
        OS="macos"
    else
        OS="unknown"
    fi

    case "$OS" in
        ubuntu|debian|kali|linuxmint|parrot)
            OS_FAMILY="debian"
            ;;
        fedora|rhel|centos|rocky|alma)
            OS_FAMILY="redhat"
            ;;
        arch|manjaro|endeavouros)
            OS_FAMILY="arch"
            ;;
        macos|darwin)
            OS_FAMILY="macos"
            ;;
        *)
            OS_FAMILY="unknown"
            ;;
    esac

    echo "Detected: $OS ($OS_FAMILY)"
}

check_root() {
    if [ "$EUID" -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

main() {
    print_banner

    print_info "Project directory: $PROJECT_DIR"
    print_info "Starting installation..."
    echo ""

    detect_os
    echo ""

    if ! check_root; then
        print_warning "Some system packages require root privileges."
        echo ""
    fi

    # Check Python
    print_step 1 7 "Checking Python installation..."
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is not installed!"
        echo "  Please install Python 3.8+ from: https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"

    if ! command -v pip3 >/dev/null 2>&1 && ! python3 -m pip --version >/dev/null 2>&1; then
        print_error "pip is not installed!"
        exit 1
    fi
    print_success "pip is available"
    echo ""

    # Create virtual environment
    print_step 2 7 "Creating Python virtual environment..."
    cd "$PROJECT_DIR"

    if [ -d "$VENV_NAME" ]; then
        print_warning "Removing existing $VENV_NAME..."
        rm -rf "$VENV_NAME"
    fi

    python3 -m venv "$VENV_NAME"
    print_success "Virtual environment created: $VENV_NAME"
    echo ""

    # Activate virtual environment
    print_step 3 7 "Activating virtual environment and upgrading pip..."
    source "$VENV_NAME/bin/activate"
    python3 -m pip install --upgrade pip
    print_success "pip upgraded"
    echo ""

    # Install Python dependencies
    print_step 4 7 "Installing Python dependencies..."
    echo ""

    echo "  Installing core dependencies..."
    pip install "flask>=2.3.0,<4.0.0" "requests>=2.31.0,<3.0.0" "psutil>=5.9.0,<6.0.0" "fastmcp>=0.2.0,<1.0.0"
    print_success "Core dependencies installed"

    echo "  Installing web scraping & automation..."
    pip install "beautifulsoup4>=4.12.0,<5.0.0" "selenium>=4.15.0,<5.0.0" "webdriver-manager>=4.0.0,<5.0.0"
    print_success "Web automation installed"

    echo "  Installing async & networking..."
    pip install "aiohttp>=3.8.0,<4.0.0"
    print_success "Async networking installed"

    echo "  Installing proxy & testing tools..."
    pip install "mitmproxy>=9.0.0,<11.0.0"
    print_success "Proxy tools installed"

    echo "  Installing binary analysis tools (optional)..."
    pip install "bcrypt==4.0.1" 2>/dev/null || true
    pip install "pwntools>=4.10.0,<5.0.0" 2>/dev/null || print_warning "pwntools may need system dependencies"
    pip install "angr>=9.2.0,<10.0.0" 2>/dev/null || print_warning "angr may need system dependencies"
    print_success "Binary analysis tools installed"
    echo ""

    # Verify imports
    print_step 5 7 "Verifying Python dependencies..."
    python3 -c "import flask, requests, psutil" 2>/dev/null && print_success "Core modules OK" || print_error "Core modules failed"
    python3 -c "import bs4, selenium" 2>/dev/null && print_success "Web modules OK" || print_error "Web modules failed"
    python3 -c "import aiohttp" 2>/dev/null && print_success "Async modules OK" || print_error "Async modules failed"
    python3 -c "import mitmproxy" 2>/dev/null && print_success "Proxy modules OK" || print_error "Proxy modules failed"
    echo ""

    # Install external security tools
    print_step 6 7 "Installing external security tools..."
    echo ""
    install_security_tools
    echo ""

    # Browser Agent setup
    print_step 7 7 "Setting up Browser Agent..."
    setup_browser_agent
    echo ""

    echo "═══════════════════════════════════════════════════════════════"
    echo "  Installation Complete!"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  1. Activate the virtual environment:"
    echo "     source $VENV_NAME/bin/activate"
    echo ""
    echo "  2. Start the HexStrike server:"
    echo "     python3 hexstrike_server.py"
    echo ""
    echo "  3. Verify server is running:"
    echo "     curl http://localhost:8888/health"
    echo ""
}

install_security_tools() {
    echo "Installing external security tools..."
    echo ""

    case "$OS_FAMILY" in
        debian)
            install_debian_tools
            ;;
        redhat)
            install_redhat_tools
            ;;
        arch)
            install_arch_tools
            ;;
        macos)
            install_macos_tools
            ;;
        *)
            print_warning "Unknown OS. Please install security tools manually."
            ;;
    esac

    print_success "Security tools installation complete"
}

install_debian_tools() {
    print_info "Updating package list..."
    sudo apt update -qq 2>/dev/null || print_warning "Could not update package list"

    print_info "Installing network & reconnaissance tools..."
    sudo apt install -y -qq nmap masscan curl wget git dnsutils 2>/dev/null || true

    print_info "Installing web application tools..."
    sudo apt install -y -qq gobuster dirb nikto 2>/dev/null || true

    if ! command -v go >/dev/null 2>&1; then
        print_info "Installing Go..."
        sudo apt install -y -qq golang-go 2>/dev/null || true
    fi

    if command -v go >/dev/null 2>&1; then
        print_info "Installing Go-based security tools..."
        export PATH="$PATH:$(go env GOPATH)/bin" 2>/dev/null || true
        go install github.com/projectdiscovery/nuclei/v3/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/httpx/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/subfinder/v2/...@latest 2>/dev/null || true
        go install github.com/OJ/gobuster/v3/...@latest 2>/dev/null || true
    fi

    print_info "Installing Python-based security tools..."
    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true

    print_info "Installing binary analysis tools..."
    sudo apt install -y -qq gdb radare2 binutils 2>/dev/null || true

    print_info "Installing forensics tools..."
    sudo apt install -y -qq steghide exiftool foremost 2>/dev/null || true

    print_info "Installing password tools..."
    sudo apt install -y -qq john hashcat hydra 2>/dev/null || true

    echo ""
    print_success "Installed security tools:"
    for tool in nmap masscan gobuster dirb nikto nuclei httpx subfinder; do
        if command -v $tool >/dev/null 2>&1; then
            echo "    ✓ $tool"
        fi
    done
}

install_redhat_tools() {
    print_info "Installing tools for RHEL/Fedora/CentOS..."
    sudo dnf install -y nmap masscan curl wget git golang 2>/dev/null || true

    if command -v go >/dev/null 2>&1; then
        go install github.com/projectdiscovery/nuclei/v3/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/httpx/...@latest 2>/dev/null || true
    fi

    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true
}

install_arch_tools() {
    print_info "Installing tools for Arch Linux..."
    sudo pacman -Sy --noconfirm nmap masscan gobuster nikto curl wget git go 2>/dev/null || true
    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true
}

install_macos_tools() {
    print_info "Installing tools for macOS..."

    if ! command -v brew >/dev/null 2>&1; then
        print_warning "Homebrew not found."
        return
    fi

    brew install nmap masscan gobuster nikto curl wget git go 2>/dev/null || true
    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true
}

setup_browser_agent() {
    echo "Setting up Browser Agent..."
    echo ""

    case "$OS_FAMILY" in
        debian)
            if command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1; then
                print_success "Chromium already installed"
            elif command -v google-chrome >/dev/null 2>&1; then
                print_success "Google Chrome already installed"
            else
                print_info "Installing Chromium for Browser Agent..."
                sudo apt install -y -qq chromium chromium-driver 2>/dev/null || {
                    print_warning "Consider installing Google Chrome manually"
                }
            fi
            ;;
        redhat)
            sudo dnf install -y chromium 2>/dev/null || print_warning "Consider installing Google Chrome manually"
            ;;
        macos)
            print_info "Please install Google Chrome from https://www.google.com/chrome/"
            ;;
        *)
            print_warning "Please ensure Chrome/Chromium is installed for Browser Agent"
            ;;
    esac

    print_success "Browser Agent setup complete"
}

main "$@"
