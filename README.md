# Meta-Prompt MCP

> Instant access to Google and Anthropic's official prompting guides within your LLM workflow—optimized for crafting high-quality meta-prompts and system prompts.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What It Does

Meta-Prompt MCP is an MCP server that surfaces official prompting best practices from Google and Anthropic directly within your LLM workflow. Instead of searching documentation or guessing how to instruct an LLM, you can query expert guides on-demand.

This is especially valuable when crafting meta-prompts (system prompts for agents) or optimizing your own prompting strategies. By grounding your prompts in proven methodology, you'll generate more effective, well-structured outputs.

### How It Works

Your MCP host (Claude Desktop, Cursor, etc.) communicates with the server via stdio. When you ask for a guide, the server retrieves it from bundled markdown files—no API calls, no latency.

```
┌────────────────────────┐          ┌──────────────────────────┐
│   Your LLM Host        │◄─stdio──►│  Meta-Prompt MCP Server  │
│  (Claude Desktop, etc) │          │                          │
└────────────────────────┘          │  • get_google_guide      │
                                    │  • get_anthropic_guide   │
                                    │                          │
                                    │  Data layer:             │
                                    │  ./data/                 │
                                    │  ├── google_*.md         │
                                    │  └── anthropic_*.md      │
                                    └──────────────────────────┘
```

### Key Features

- **`get_google_guide`** — Retrieves Google's comprehensive prompting guide covering techniques, best practices, and LLM configuration
- **`get_anthropic_guide`** — Retrieves Anthropic's guide on chain-of-thought, multishot prompting, and extended thinking
- **Zero dependencies** — Runs entirely offline with bundled guides; no API keys or network calls required

---

## Validation

We ran a benchmark comparing prompts generated with and without guide access across 5 diverse tasks. An independent judge LLM scored each on Clarity, Specificity, Structure, Effectiveness, and Overall quality (1–10 scale).

**[See full results →](benchmarks/results.md)**

To reproduce the benchmark:

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

## Usage

Query the guides while crafting your prompts. Examples:

- *"I'm building a code reviewer agent. Reference the Google guide to help me write a better system prompt."*
- *"Based on the Anthropic guide, suggest improvements to this prompt for better reasoning."*
- *"What technique from the guides would work best for this task?"*

The LLM reads the guides and uses that knowledge to give you more informed suggestions and feedback on your prompts.

---

## Development

```bash
# Clone the repo
git clone https://github.com/kapillamba4/meta-prompt-mcp.git
cd meta-prompt-mcp

# Install in dev mode
make dev

# Run the server
make run
```

### Available Commands

```bash
make dev        # Install in editable mode with dev dependencies
make run        # Start the MCP server locally
make lint       # Check code quality
make format     # Auto-format code with Black & isort
make test       # Run test suite
make benchmark  # Run prompt quality benchmark (requires OPENROUTER_API_KEY)
make build      # Build distribution packages
make publish    # Publish to PyPI
```

---

## Project Structure

```
meta-prompt-mcp/
├── pyproject.toml                 # Dependencies and package config
├── Makefile                       # Development commands
├── .env.example                   # Template for OPENROUTER_API_KEY
│
├── benchmarks/
│   ├── benchmark.py               # Prompt quality evaluation script
│   └── results.md                 # Benchmark results
│
└── src/meta_prompt_mcp/
    ├── __init__.py
    ├── __main__.py                # Entry point (python -m)
    ├── server.py                  # FastMCP server & tool definitions
    └── data/
        ├── google_prompting_guide.md
        └── anthropic_prompting_guide.md
```

---

## Contributing

Issues, feature requests, and contributions welcome. Please open an issue on [GitHub](https://github.com/kapillamba4/meta-prompt-mcp/issues).

## License

MIT
