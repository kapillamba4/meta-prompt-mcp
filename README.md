# 🔮 Meta-Prompt MCP

> **A Prompting Oracle** — An MCP server that bridges Google's official 68-page Prompting Guide 101 with your LLM workflow using RAG.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What It Does

Meta-Prompt MCP is a specialized **Model Context Protocol (MCP)** server that acts as an automated "Prompting Oracle." It lets any MCP-compatible host (Claude Desktop, Cursor, etc.) **query Google's Prompting Guide 101** mid-conversation for specific techniques and best practices.

### Architecture

```
┌─────────────────────┐     stdio      ┌──────────────────────────┐
│   MCP Host          │◄──────────────►│   Meta-Prompt MCP        │
│   (Claude Desktop,  │                │                          │
│    Cursor, IDEs)    │                │   ┌──────────────────┐   │
│                     │                │   │  FastMCP Server   │   │
│                     │                │   │  • get_google_    │   │
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
| **`get_google_strategy` tool** | RAG-powered lookup into the 68-page PDF |
| **`improve_my_prompt` prompt** | Template that analyzes and rewrites your prompts using guide techniques |
| **Zero-cost embeddings** | Uses `BAAI/bge-small-en-v1.5` locally — no API keys after initial parse |
| **Persistent index** | Vector store cached in `./storage` for near-instant startup |
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

### 2. Set Up the Data

```bash
# Place Google's Prompting Guide 101 PDF in the data/ directory
cp ~/Downloads/prompting-guide-101.pdf data/
```

### 3. First Run (requires LLAMA_CLOUD_API_KEY)

```bash
# Get a free key at https://cloud.llamaindex.ai/
cp .env.example .env
# Edit .env and add your LLAMA_CLOUD_API_KEY

# The first run parses the PDF and builds the index
meta-prompt-mcp
```

After the first run, `./storage` is created and no API keys are needed.

### 4. Configure Your MCP Host

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
pip install -e ".[dev]"

# Run the server
meta-prompt-mcp
# or
python -m meta_prompt_mcp
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LLAMA_CLOUD_API_KEY` | First run only | LlamaParse API key for PDF parsing |

---

## Project Structure

```
meta-prompt-mcp/
├── pyproject.toml              # Package config & dependencies
├── README.md
├── .env.example                # Env template
├── data/                       # Place PDF here
│   └── README.md
├── storage/                    # Auto-generated vector index (gitignored)
└── src/
    └── meta_prompt_mcp/
        ├── __init__.py
        ├── __main__.py         # python -m support
        ├── index_manager.py    # LlamaParse + embedding + persistence
        └── server.py           # FastMCP server with tools & prompts
```

---

## License

MIT
