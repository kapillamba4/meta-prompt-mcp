# Meta-Prompt MCP

> **A Prompting Oracle** — An MCP server that bridges official Prompting Guides with your LLM workflow.
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What It Does

Meta-Prompt MCP is a specialized **Model Context Protocol (MCP)** server that acts as an automated "Prompting Oracle." It lets any MCP-compatible host (Claude Desktop, Cursor, etc.) **query your prompting Guides** mid-conversation for specific techniques and best practices.

### Architecture

```
┌─────────────────────┐     stdio      ┌──────────────────────────┐
│   MCP Host          │◄──────────────►│   Meta-Prompt MCP        │
│   (Claude Desktop,  │                │                          │
│    Cursor, IDEs)    │                │   ┌──────────────────┐   │
│                     │                │   │  FastMCP Server   │   │
│                     │                │   │  • get_google_    │   │
│                     │                │   │    guide          │   │
│                     │                │   │  • get_anthropic_ │   │
│                     │                │   │    guide          │   │
│                     │                │   └────────┬─────────┘   │
│                     │                │            │              │
│                     │                │   ┌────────▼─────────┐   │
│                     │                │   │  ./data/         │   │
│                     │                │   │  (markdown files) │   │
│                     │                │   └──────────────────┘   │
└─────────────────────┘                └──────────────────────────┘
```

### Key Features

| Feature | Details |
|---------|---------|
| **`get_google_guide` tool** | Dumps the full Google Prompting Guide 101 markdown |
| **`get_anthropic_guide` tool** | Dumps the full Anthropic Prompting Guide markdown |
| **Offline capable** | Runs entirely locally, reading from bundled markdown files |

---

## Quick Start

### 1. Install

```bash
# Via uvx (recommended — run without installing globally)
uvx meta-prompt-mcp

# Or install via pip
pip install meta-prompt-mcp
```

The package ships with bundled markdown guides — no API keys or setup needed.

### 2. Configure Your MCP Host

#### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "meta-prompt-mcp": {
      "command": "uvx",
      "args": ["meta-prompt-mcp"]
    }
  }
}
```

#### Cursor

Add to your MCP settings:

```json
{
  "mcpServers": {
    "meta-prompt-mcp": {
      "command": "uvx",
      "args": ["meta-prompt-mcp"]
    }
  }
}
```

---

## Development

```bash
# Clone the repo
git clone <your-repo-url>
cd meta-prompt-mcp

# Install in dev mode
make dev

# Run the server
make run
```

### Make Targets

| Command | Description |
|---------|-------------|
| `make dev` | Install in editable mode with dev dependencies |
| `make run` | Start the MCP server |
| `make lint` | Run linter |
| `make format` | Auto-format code |
| `make test` | Run tests |
| `make build` | Build distribution packages |
| `make publish` | Publish to PyPI |

---

## Project Structure

```
meta-prompt-mcp/
├── pyproject.toml              # Package config & dependencies
├── Makefile                    # Dev commands (make help)
├── README.md
├── .env.example                # Env template
└── src/
    └── meta_prompt_mcp/
        ├── __init__.py
        ├── __main__.py         # python -m support
        ├── server.py           # FastMCP server with tools
        └── data/               # Bundled markdown guides
```

---

## License

MIT
