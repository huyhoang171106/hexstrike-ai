#!/bin/bash

# =============================================================================
# HexStrike AI MCP v6.0 - Complete Auto Install Script
# =============================================================================
# This script sets up the complete HexStrike AI environment including:
# - Python virtual environment and dependencies
# - External security tools (150+ tools)
# - System dependencies for binary analysis
# - Browser Agent requirements (Chrome/Chromium)
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_NAME="hexstrike_env"

# =============================================================================
# Helper Functions
# =============================================================================

print_banner() {
    echo -e "${MAGENTA}"
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
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}[$1/$2]${NC} ${BLUE}$3${NC}"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        OS_VERSION=$DISTRIB_RELEASE
    elif [ "$(uname)" == "Darwin" ]; then
        OS="macos"
    elif [ "$(uname)" == "Windows_NT" ]; then
        OS="windows"
    else
        OS="unknown"
    fi

    # Normalize
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

    echo "Detected: $OS $OS_VERSION ($OS_FAMILY)"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# Main Installation
# =============================================================================

main() {
    print_banner

    echo ""
    print_info "Project directory: $PROJECT_DIR"
    print_info "Starting installation..."
    echo ""

    # Detect OS
    detect_os

    # Check if script is run as root for system installs
    if ! check_root; then
        print_warning "Some system packages require root privileges."
        echo "  You may be prompted for sudo password during installation."
        echo ""
    fi

    # Check Python
    print_step 1 7 "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed!"
        echo "  Please install Python 3.8+ from: https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"

    # Check pip
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
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

    # Core dependencies
    echo -e "  ${CYAN}Installing core dependencies...${NC}"
    pip install "flask>=2.3.0,<4.0.0" "requests>=2.31.0,<3.0.0" "psutil>=5.9.0,<6.0.0" "fastmcp>=0.2.0,<1.0.0"
    print_success "Core dependencies installed"

    # Web scraping & automation
    echo -e "  ${CYAN}Installing web scraping & automation...${NC}"
    pip install "beautifulsoup4>=4.12.0,<5.0.0" "selenium>=4.15.0,<5.0.0" "webdriver-manager>=4.0.0,<5.0.0"
    print_success "Web automation installed"

    # Async & networking
    echo -e "  ${CYAN}Installing async & networking...${NC}"
    pip install "aiohttp>=3.8.0,<4.0.0"
    print_success "Async networking installed"

    # Proxy & testing
    echo -e "  ${CYAN}Installing proxy & testing tools...${NC}"
    pip install "mitmproxy>=9.0.0,<11.0.0"
    print_success "Proxy tools installed"

    # Binary analysis (optional)
    echo -e "  ${CYAN}Installing binary analysis tools (optional)...${NC}"
    pip install "bcrypt==4.0.1" 2>/dev/null || true
    pip install "pwntools>=4.10.0,<5.0.0" 2>/dev/null || print_warning "pwntools may need system dependencies"
    pip install "angr>=9.2.0,<10.0.0" 2>/dev/null || print_warning "angr may need system dependencies"
    print_success "Binary analysis tools installed (some may require system deps)"
    echo ""

    # Verify core imports
    print_step 5 7 "Verifying Python dependencies..."
    python3 -c "import flask, requests, psutil; print_success 'Core modules: OK'" 2>/dev/null || print_error "Core modules failed"
    python3 -c "import bs4, selenium, webdriver_manager; print_success 'Web modules: OK'" 2>/dev/null || print_error "Web modules failed"
    python3 -c "import aiohttp; print_success 'Async modules: OK'" 2>/dev/null || print_error "Async modules failed"
    python3 -c "import mitmproxy; print_success 'Proxy modules: OK'" 2>/dev/null || print_error "Proxy modules failed"
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

    # Final summary
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo ""
    echo "  1. Activate the virtual environment:"
    echo "     source $VENV_NAME/bin/activate"
    echo ""
    echo "  2. Start the HexStrike server:"
    echo "     python3 hexstrike_server.py"
    echo ""
    echo "  3. (Optional) Start with custom port:"
    echo "     python3 hexstrike_server.py --port 8888"
    echo ""
    echo "  4. Verify server is running:"
    echo "     curl http://localhost:8888/health"
    echo ""
    echo "  5. Configure MCP client (Claude Desktop, Cursor, etc.)"
    echo "     See README.md for configuration examples"
    echo ""
}

# =============================================================================
# Security Tools Installation (by OS)
# =============================================================================

install_security_tools() {
    echo -e "${CYAN}Installing external security tools...${NC}"
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
            echo "  See README.md for tool installation instructions."
            ;;
    esac

    print_success "Security tools installation complete"
}

install_debian_tools() {
    # Update package list
    print_info "Updating package list..."
    sudo apt update -qq 2>/dev/null || print_warning "Could not update package list"

    # Core network tools
    print_info "Installing network & reconnaissance tools..."
    sudo apt install -y -qq \
        nmap \
        masscan \
        curl \
        wget \
        git \
        dnsutils \
        enum4linux \
        nbtscan \
        rpcbind \
        2>/dev/null || true

    # Web tools
    print_info "Installing web application tools..."
    sudo apt install -y -qq \
        gobuster \
        dirb \
        nikto \
        2>/dev/null || true

    # Install Go tools (needed for many security tools)
    if ! command -v go &> /dev/null; then
        print_info "Installing Go..."
        sudo apt install -y -qq golang-go 2>/dev/null || true
    fi

    # Install Go-based tools
    if command -v go &> /dev/null; then
        print_info "Installing Go-based security tools..."

        # Install various tools via Go
        go install github.com/projectdiscovery/nuclei/v3/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/httpx/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/subfinder/v2/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/fuff/...@latest 2>/dev/null || true
        go install github.com/OJ/gobuster/v3/...@latest 2>/dev/null || true
        go install github.com/ticarpi/jwt_tool@latest 2>/dev/null || true

        # Add Go bin to PATH
        export PATH="$PATH:$(go env GOPATH)/bin"
    fi

    # Install Python-based security tools
    print_info "Installing Python-based security tools..."
    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true
    pip install wpscan 2>/dev/null || true
    pip install droopescan 2>/dev/null || true

    # Binary analysis tools
    print_info "Installing binary analysis tools..."
    sudo apt install -y -qq \
        gdb \
        radare2 \
        binutils \
        strings \
        objdump \
        checksec 2>/dev/null || true

    # Forensics tools
    sudo apt install -y -qq \
        steghide \
        exiftool \
        foremost \
        2>/dev/null || true

    # Password tools
    sudo apt install -y -qq \
        john \
        hashcat \
        hydra \
        2>/dev/null || true

    # Print installed tools summary
    echo ""
    print_success "Installed security tools:"
    for tool in nmap masscan gobuster dirb nikto nuclei httpx subfinder; do
        if command -v $tool &> /dev/null; then
            echo "    ✓ $tool"
        fi
    done
}

install_redhat_tools() {
    print_info "Installing tools for RHEL/Fedora/CentOS..."

    sudo dnf install -y \
        nmap \
        masscan \
        curl \
        wget \
        git \
        2>/dev/null || true

    # Install Go
    if ! command -v go &> /dev/null; then
        sudo dnf install -y golang 2>/dev/null || true
    fi

    # Install tools via Go
    if command -v go &> /dev/null; then
        go install github.com/projectdiscovery/nuclei/v3/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/httpx/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/subfinder/v2/...@latest 2>/dev/null || true
    fi

    # Install Python tools
    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true
}

install_arch_tools() {
    print_info "Installing tools for Arch Linux..."

    sudo pacman -Sy --noconfirm \
        nmap \
        masscan \
        gobuster \
        nikto \
        curl \
        wget \
        git \
        2>/dev/null || true

    # Install Go
    if ! command -v go &> /dev/null; then
        sudo pacman -S --noconfirm go 2>/dev/null || true
    fi

    # Install tools via Go
    if command -v go &> /dev/null; then
        go install github.com/projectdiscovery/nuclei/v3/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/httpx/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/subfinder/v2/...@latest 2>/dev/null || true
    fi

    # Install Python tools
    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true
}

install_macos_tools() {
    print_info "Installing tools for macOS..."

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi

    # Install tools via Homebrew
    brew install \
        nmap \
        masscan \
        gobuster \
        nikto \
        curl \
        wget \
        git \
        2>/dev/null || true

    # Install Go
    if ! command -v go &> /dev/null; then
        brew install go 2>/dev/null || true
    fi

    # Install tools via Go
    if command -v go &> /dev/null; then
        go install github.com/projectdiscovery/nuclei/v3/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/httpx/...@latest 2>/dev/null || true
        go install github.com/projectdiscovery/subfinder/v2/...@latest 2>/dev/null || true
    fi

    # Install Python tools
    pip install sqlmap 2>/dev/null || true
    pip install dirsearch 2>/dev/null || true
}

# =============================================================================
# Browser Agent Setup
# =============================================================================

setup_browser_agent() {
    echo -e "${CYAN}Setting up Browser Agent...${NC}"
    echo ""

    case "$OS_FAMILY" in
        debian)
            # Try Chromium first (open source), then Chrome
            if command -v chromium &> /dev/null; then
                print_success "Chromium already installed"
            elif command -v chromium-browser &> /dev/null; then
                print_success "Chromium browser already installed"
            elif command -v google-chrome &> /dev/null; then
                print_success "Google Chrome already installed"
            else
                print_info "Installing Chromium for Browser Agent..."
                sudo apt install -y -qq chromium chromium-driver 2>/dev/null || {
                    print_warning "Installing Google Chrome instead..."
                    wget -q -O /tmp/chrome.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
                    sudo dpkg -i /tmp/chrome.deb 2>/dev/null || sudo apt install -y -qq /tmp/chrome.deb
                    rm -f /tmp/chrome.deb
                }
            fi
            ;;
        redhat)
            sudo dnf install -y chromium 2>/dev/null || {
                print_warning "Consider installing Google Chrome manually"
            }
            ;;
        macos)
            if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null; then
                print_success "Browser already installed"
            else
                print_info "Please install Google Chrome from https://www.google.com/chrome/"
            fi
            ;;
        *)
            print_warning "Please ensure Chrome/Chromium is installed for Browser Agent"
            ;;
    esac

    print_success "Browser Agent setup complete"
}

# =============================================================================
# Run Main
# =============================================================================

main "$@"
