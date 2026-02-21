"""
MCP Server — Exposes the Prompting Oracle as standardized MCP Tools and Prompts.

Run directly:
    python -m meta_prompt_mcp.server

Or via the installed entry point:
    meta-prompt-mcp
"""

from __future__ import annotations

import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger("meta-prompt-mcp")

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "meta-prompt-mcp",
    instructions=(
        "You are connected to the Meta-Prompt MCP server — a Prompting Oracle "
        "backed by official prompting guides. "
        "Use the `get_google_guide` and `get_anthropic_guide` tools to look up "
        "comprehensive prompting techniques, patterns, and best practices."
    ),
)


def _read_guide(filename: str) -> str:
    """Read a guide from the data directory."""
    data_dir = Path(__file__).parent / "data"
    filepath = data_dir / filename
    try:
        return filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"⚠️  Guide not found: {filename}. Please ensure it exists in the data directory."
    except Exception as exc:
        return f"⚠️  Error reading guide: {exc}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_google_guide() -> str:
    """Get the full Google Prompting Guide markdown content.
    
    Returns:
        The complete markdown text of the Google Prompting Guide.
    """
    logger.info("Tool call: get_google_guide()")
    return _read_guide("google_prompting_guide.md")


@mcp.tool()
def get_anthropic_guide() -> str:
    """Get the full Anthropic Prompting Guide markdown content.
    
    Returns:
        The complete markdown text of the Anthropic Prompting Guide.
    """
    logger.info("Tool call: get_anthropic_guide()")
    return _read_guide("anthropic_prompting_guide.md")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the MCP server using stdio transport."""
    logger.info("Starting Meta-Prompt MCP server…")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
