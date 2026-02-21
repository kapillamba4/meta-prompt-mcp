# Meta-Prompt MCP

> **A Prompting Oracle** — An MCP server that bridges official Prompting Guides with your LLM workflow using RAG.

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
│                     │                │   │  • get_prompting_ │   │
│                     │                │   │    strategy       │   │
│                     │                │   │  • improve_my_    │   │
│                     │                │   │    prompt         │   │
│                     │                │   └────────┬─────────┘   │
│                     │                │            │              │
│                     │                │   ┌────────▼─────────┐   │
│                     │                │   │  LlamaIndex RAG  │   │
│                     │                │   │  • bge-small-en   │   │
│                     │                │   │  • VectorStore    │   │
│                     │                │   └────────┬─────────┘   │
│                     │                │            │              │
│                     │                │   ┌────────▼─────────┐   │
│                     │                │   │  ./storage/       │   │
│                     │                │   │  (persisted idx)  │   │
│                     │                │   └──────────────────┘   │
└─────────────────────┘                └──────────────────────────┘
```

### Key Features

| Feature | Details |
|---------|---------|
| **`get_prompting_strategy` tool** | RAG-powered lookup into the prompting guides |
| **`improve_my_prompt` prompt** | Template that analyzes and rewrites your prompts using guide techniques |
| **Zero-cost embeddings** | Uses `BAAI/bge-small-en-v1.5` locally — no API keys after initial parse |
| **Persistent index** | Vector store cached inside the package for near-instant startup |
| **Offline capable** | Runs entirely locally after the one-time index build |

---

## Quick Start

### 1. Install

```bash
# Via uvx (recommended — run without installing globally)
uvx meta-prompt-mcp

# Or install via pip
pip install meta-prompt-mcp
```

The package ships with a **pre-built vector index** — no API keys or setup needed.

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

# Build (or rebuild) the vector index
make build-index

# Run the server
make run
```

### Make Targets

| Command | Description |
|---------|-------------|
| `make dev` | Install in editable mode with dev dependencies |
| `make build-index` | Pre-build the vector index from documents |
| `make clean-index` | Remove cached index (forces rebuild on next run) |
| `make run` | Start the MCP server |
| `make lint` | Run linter |
| `make format` | Auto-format code |
| `make test` | Run tests |
| `make build` | Build distribution packages |
| `make publish` | Publish to PyPI |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLAMA_CLOUD_API_KEY` | Only for rebuilding index | LlamaParse API key for PDF parsing |

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
        ├── index_manager.py    # LlamaParse + embedding + persistence
        ├── server.py           # FastMCP server with tools & prompts
        ├── data/               # Place PDFs/MDs here
        └── storage/            # Auto-generated vector index (gitignored)
```

---

## License

MIT
