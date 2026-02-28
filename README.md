<!-- mcp-name: io.github.kapillamba4/meta-prompt-mcp -->

# Meta-Prompt MCP

> **A Prompting Oracle** — An MCP server that bridges official Prompting Guides with your LLM workflow to help you generate highly accurate, effective, and structured meta-prompts.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What It Does

Meta-Prompt MCP is a specialized **Model Context Protocol (MCP)** server that acts as an automated "Prompting Oracle." It empowers any MCP-compatible host (Claude Desktop, Cursor, etc.) to **query expert Prompting Guides** mid-conversation. 

When building AI workflows, creating robust "meta-prompts" (system prompts for agents) is critical. Instead of guessing how to instruct an LLM, this server provides immediate access to authoritative guidelines. By surfacing these best practices on-demand, it ensures the meta-prompts you generate are exceptionally accurate, helpful, and grounded in proven methodology.

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
| **`get_google_guide` tool** | Retrieves the comprehensive Google Prompting Guide to inform clear, context-rich prompting strategies |
| **`get_anthropic_guide` tool** | Retrieves the full Anthropic Prompting Guide for mastering capabilities and system prompts |
| **Offline capable** | Runs entirely locally, reading from bundled markdown files with zero API dependencies |

---

## Benchmark Results

To validate the tool's impact, we ran a benchmark comparing prompts generated **with** and **without** the prompting guides across 5 diverse tasks. An independent judge LLM scored each prompt on Clarity, Specificity, Structure, Effectiveness, and Overall quality (1–10 scale).

> **[View Full Benchmark Results →](benchmarks/results.md)**

Run the benchmark yourself:

```bash
export OPENROUTER_API_KEY=sk-or-...
make benchmark
```

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

#### Claude Code

Run the following command in your terminal:

```bash
claude mcp add meta-prompt-mcp -- uvx meta-prompt-mcp
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
| `make benchmark` | Run prompt quality benchmark (requires `OPENROUTER_API_KEY`) |
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
├── .env.example                # Env template (OPENROUTER_API_KEY)
├── benchmarks/
│   ├── benchmark.py            # Prompt quality benchmark
│   └── results.md              # Generated benchmark results
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
