# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HexStrike AI MCP v6.0 is an AI-powered cybersecurity automation platform that provides 150+ security tools through an MCP (Model Context Protocol) interface. It connects AI agents (Claude, GPT, Copilot) to autonomous security testing capabilities.

## Architecture

The project uses a **two-script architecture**:

1. **hexstrike_server.py** - Flask API server that manages security tools, process execution, caching, and provides REST API endpoints
2. **hexstrike_mcp.py** - FastMCP client that exposes tools to AI agents via MCP protocol

AI Agent → MCP Protocol → hexstrike_mcp.py → HTTP → hexstrike_server.py → Security Tools

## Commands

```bash
# Install dependencies
python3 -m venv hexstrike_env
source hexstrike_env/bin/activate  # Linux/Mac
# hexstrike_env\Scripts\activate   # Windows
pip3 install -r requirements.txt

# Start the server (required before MCP client)
python3 hexstrike_server.py

# Start with custom port
python3 hexstrike_server.py --port 8888

# Enable debug logging
python3 hexstrike_server.py --debug

# Verify server health
curl http://localhost:8888/health
```

## MCP Configuration

Configure Claude Desktop or other MCP clients via `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hexstrike-ai": {
      "command": "python3",
      "args": ["/path/to/hexstrike_mcp.py", "--server", "http://localhost:8888"],
      "description": "HexStrike AI v6.0 - Advanced Cybersecurity Automation Platform",
      "timeout": 300,
      "disabled": false
    }
  }
}
```

## Key Dependencies

- **flask** - Web API server
- **fastmcp** - MCP protocol integration
- **psutil** - Process management
- **selenium/webdriver** - Browser automation (Browser Agent)
- **aiohttp** - Async HTTP
- **mitmproxy** - HTTP proxy
- **pwntools, angr** - Binary analysis (optional)

## External Security Tools

150+ security tools must be installed separately. Key tools:
- **Network**: nmap, masscan, rustscan, amass, subfinder
- **Web**: gobuster, nuclei, sqlmap, nikto, ffuf
- **Cloud**: prowler, scout-suite, trivy, kube-hunter
- **Binary**: ghidra, radare2, pwntools, angr

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/api/command` | POST | Execute security tools |
| `/api/processes/list` | GET | List active processes |
| `/api/processes/terminate/<pid>` | POST | Kill process |
| `/api/intelligence/analyze-target` | POST | AI target analysis |

## Code Structure

- **hexstrike_server.py**: Main server (~2200 lines) - Flask app, tool wrappers, process management, caching, AI intelligence modules
- **hexstrike_mcp.py**: MCP client (~500 lines) - FastMCP server exposing tools to AI agents
- **ModernVisualEngine** class: Terminal UI with colors and animations (in server.py)

## Important Notes

- Server must run before MCP client connects
- Browser Agent requires Chrome/Chromium + ChromeDriver
- This is a legitimate security testing framework - authorized use only
- No test files in this repository
