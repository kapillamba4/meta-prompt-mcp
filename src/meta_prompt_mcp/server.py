"""
MCP Server — Exposes the Prompting Oracle as standardized MCP Tools and Prompts.

Run directly:
    python -m meta_prompt_mcp.server

Or via the installed entry point:
    meta-prompt-mcp
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from meta_prompt_mcp.index_manager import IndexManager

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger("meta-prompt-mcp")

# ---------------------------------------------------------------------------
# Server + Index
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "meta-prompt-mcp",
    instructions=(
        "You are connected to the Meta-Prompt MCP server — a Prompting Oracle "
        "backed by Google's official 68-page Prompting Guide 101. "
        "Use the `get_google_strategy` tool to look up specific prompting techniques, "
        "patterns, and best practices from the guide."
    ),
)

_index_manager = IndexManager()

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_google_strategy(query: str) -> str:
    """Look up a prompting technique or best practice from Google's Prompting Guide 101.

    Args:
        query: Natural-language question about a prompting strategy or technique.

    Returns:
        Synthesized answer grounded in the guide.
    """
    logger.info("Tool call: get_google_strategy(%r)", query)
    try:
        result = _index_manager.query(query)
        return result
    except FileNotFoundError as exc:
        return (
            f"⚠️  Setup required: {exc}\n\n"
            "Please place the Google Prompting Guide 101 PDF in the data/ directory "
            "and restart the server."
        )
    except RuntimeError as exc:
        return f"⚠️  Configuration error: {exc}"


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


@mcp.prompt()
def improve_my_prompt(draft_prompt: str) -> str:
    """Analyze a draft prompt and return an improved version using Google's prompting best practices.

    This prompt template instructs the host LLM to:
    1. Look up relevant techniques from the Prompting Guide
    2. Identify weaknesses in the draft
    3. Apply specific improvements with explanations

    Args:
        draft_prompt: The user's draft prompt that needs improvement.
    """
    return f"""You are a Prompt Engineering Expert with access to Google's official Prompting Guide 101.

Your task is to analyze and improve the following draft prompt.

## Draft Prompt
{draft_prompt}

## Instructions
1. First, use the `get_google_strategy` tool to look up relevant prompting techniques
   (e.g., few-shot patterns, chain-of-thought, delimiters, role assignment).
2. Identify specific weaknesses in the draft prompt.
3. Rewrite the prompt applying the techniques you found.
4. Explain what you changed and why, citing the specific technique from Google's guide.

Return your response in this format:

### Analysis
[What's weak about the current prompt]

### Improved Prompt
[The rewritten prompt]

### Changes Applied
[Bullet list of changes with the Google technique that motivated each]
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the MCP server using stdio transport."""
    logger.info("Starting Meta-Prompt MCP server…")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
