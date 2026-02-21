#!/usr/bin/env python3
"""
Benchmark: Meta-Prompt MCP — With vs. Without the Tool

Generates prompts for diverse tasks using a baseline LLM and a tool-assisted
LLM (injecting the Google + Anthropic prompting guides), then scores both
via a judge LLM on OpenRouter.

Usage:
    export OPENROUTER_API_KEY=sk-or-...
    python benchmarks/benchmark.py

Requires: pip install openai python-dotenv
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GENERATOR_MODEL = os.getenv("BENCHMARK_GENERATOR_MODEL", "google/gemini-3.1-pro-preview")
JUDGE_MODEL = os.getenv("BENCHMARK_JUDGE_MODEL", "google/gemini-3.1-pro-preview")

DATA_DIR = Path(__file__).resolve().parent.parent / "src" / "meta_prompt_mcp" / "data"
RESULTS_PATH = Path(__file__).resolve().parent / "results.md"

BENCHMARK_TASKS = [
    "Write a system prompt for an AI code-review agent that reviews pull requests",
    "Write a system prompt for a customer-support chatbot for a SaaS product",
    "Write a prompt to summarize complex legal documents into plain language",
    "Write a system prompt for an AI assistant that generates SQL queries from natural language",
    "Write a prompt to translate dense technical documentation into beginner-friendly tutorials",
]

RUBRIC_DIMENSIONS = ["Clarity", "Specificity", "Structure", "Effectiveness", "Overall"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _client() -> OpenAI:
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY is not set. Export it or add it to .env")
        sys.exit(1)
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )


def _load_guides() -> str:
    """Load both prompting guides and concatenate them."""
    guides: list[str] = []
    for fname in ("google_prompting_guide.md", "anthropic_prompting_guide.md"):
        path = DATA_DIR / fname
        if path.exists():
            guides.append(f"--- {fname} ---\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(guides)


def _chat(client: OpenAI, model: str, system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        seed=42,
    )
    return resp.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

BASELINE_SYSTEM = (
    "You are an expert prompt engineer. "
    "Write a high-quality, production-ready prompt for the task described by the user. "
    "Output ONLY the prompt text, nothing else."
)


def generate_baseline(client: OpenAI, task: str) -> str:
    return _chat(client, GENERATOR_MODEL, BASELINE_SYSTEM, task)


def generate_with_tool(client: OpenAI, task: str, guides: str) -> str:
    system = (
        "You are an expert prompt engineer with access to official prompting guides. "
        "Use the techniques, patterns, and best practices from the guides below to "
        "craft a high-quality, production-ready prompt for the task described by the user.\n\n"
        f"{guides}\n\n"
        "Output ONLY the prompt text, nothing else."
    )
    return _chat(client, GENERATOR_MODEL, system, task)


# ---------------------------------------------------------------------------
# Judging
# ---------------------------------------------------------------------------

JUDGE_SYSTEM = textwrap.dedent("""\
    You are an impartial expert judge evaluating prompt quality.

    You will receive two prompts (Prompt A and Prompt B) written for the same task.
    Score EACH prompt independently on these dimensions (1-10 scale):

    - Clarity: How clear and unambiguous is the prompt?
    - Specificity: How specific and detailed are the instructions?
    - Structure: How well-organized is the prompt (sections, formatting, flow)?
    - Effectiveness: How likely is this prompt to produce high-quality LLM output?
    - Overall: Holistic quality score.

    Respond with ONLY valid JSON in this exact format (no markdown, no commentary):
    {
      "prompt_a": {"Clarity": N, "Specificity": N, "Structure": N, "Effectiveness": N, "Overall": N},
      "prompt_b": {"Clarity": N, "Specificity": N, "Structure": N, "Effectiveness": N, "Overall": N}
    }
""")


def judge_prompts(
    client: OpenAI, task: str, prompt_a: str, prompt_b: str
) -> tuple[dict[str, int], dict[str, int]]:
    user_msg = (
        f"**Task:** {task}\n\n"
        f"**Prompt A (Baseline):**\n{prompt_a}\n\n"
        f"**Prompt B (Tool-Assisted):**\n{prompt_b}"
    )
    raw = _chat(client, JUDGE_MODEL, JUDGE_SYSTEM, user_msg)

    # Strip markdown fences if the model wraps its response
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])

    data = json.loads(cleaned.strip())
    return data["prompt_a"], data["prompt_b"]


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def _pct_change(baseline: float, tool: float) -> str:
    if baseline == 0:
        return "N/A"
    change = ((tool - baseline) / baseline) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%"


def build_report(results: list[dict]) -> str:
    """Build a markdown report from results."""
    lines: list[str] = []
    lines.append("# Benchmark Results — Meta-Prompt MCP\n")
    lines.append(
        "> Prompts generated **with** the tool (injecting official prompting guides) "
        "vs. **without** (baseline LLM), scored by an independent judge LLM.\n"
    )
    lines.append(f"| Detail | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| **Generator model** | `{GENERATOR_MODEL}` |")
    lines.append(f"| **Judge model** | `{JUDGE_MODEL}` |")
    lines.append(f"| **Date** | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} |")
    lines.append(f"| **Tasks evaluated** | {len(results)} |")
    lines.append("")

    # --- Summary table ---
    lines.append("## Summary\n")
    header = "| Task | " + " | ".join(f"{d} (B / T / Δ)" for d in RUBRIC_DIMENSIONS) + " |"
    sep = "|------|" + "|".join("---:" for _ in RUBRIC_DIMENSIONS) + "|"
    lines.append(header)
    lines.append(sep)

    all_baseline_overalls: list[float] = []
    all_tool_overalls: list[float] = []

    for r in results:
        short_task = r["task"][:50] + ("…" if len(r["task"]) > 50 else "")
        cells = []
        for d in RUBRIC_DIMENSIONS:
            b = r["baseline_scores"][d]
            t = r["tool_scores"][d]
            pct = _pct_change(b, t)
            cells.append(f"{b} / {t} / {pct}")
        all_baseline_overalls.append(r["baseline_scores"]["Overall"])
        all_tool_overalls.append(r["tool_scores"]["Overall"])
        lines.append(f"| {short_task} | " + " | ".join(cells) + " |")

    # --- Averages ---
    lines.append("")
    lines.append("### Averages Across All Tasks\n")
    lines.append("| Dimension | Baseline (avg) | Tool-Assisted (avg) | Improvement |")
    lines.append("|-----------|:--------------:|:-------------------:|:-----------:|")
    for d in RUBRIC_DIMENSIONS:
        b_avg = statistics.mean(r["baseline_scores"][d] for r in results)
        t_avg = statistics.mean(r["tool_scores"][d] for r in results)
        lines.append(f"| {d} | {b_avg:.1f} | {t_avg:.1f} | {_pct_change(b_avg, t_avg)} |")

    overall_b = statistics.mean(all_baseline_overalls)
    overall_t = statistics.mean(all_tool_overalls)
    lines.append("")
    lines.append(
        f"**Overall improvement: {_pct_change(overall_b, overall_t)}** "
        f"(baseline avg {overall_b:.1f} → tool-assisted avg {overall_t:.1f})\n"
    )

    # --- Per-task detail ---
    lines.append("---\n")
    lines.append("## Per-Task Details\n")
    for i, r in enumerate(results, 1):
        lines.append(f"### Task {i}: {r['task']}\n")
        lines.append("<details>")
        lines.append("<summary>View generated prompts</summary>\n")
        lines.append("**Baseline prompt:**")
        lines.append(f"````\n{r['baseline_prompt']}\n````\n")
        lines.append("**Tool-assisted prompt:**")
        lines.append(f"````\n{r['tool_prompt']}\n````\n")
        lines.append("</details>\n")
        lines.append("| Dimension | Baseline | Tool-Assisted | Δ |")
        lines.append("|-----------|:--------:|:-------------:|:-:|")
        for d in RUBRIC_DIMENSIONS:
            b = r["baseline_scores"][d]
            t = r["tool_scores"][d]
            lines.append(f"| {d} | {b} | {t} | {_pct_change(b, t)} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _run_single_task(
    task_idx: int, task: str, client: OpenAI, guides: str
) -> dict:
    """Run a single benchmark task: generate both prompts and judge them."""
    label = f"[{task_idx}/{len(BENCHMARK_TASKS)}]"
    print(f"{label} {task[:60]}...")

    print(f"{label}   Generating baseline prompt...")
    baseline_prompt = generate_baseline(client, task)

    print(f"{label}   Generating tool-assisted prompt...")
    tool_prompt = generate_with_tool(client, task, guides)

    print(f"{label}   Judging...")
    try:
        baseline_scores, tool_scores = judge_prompts(client, task, baseline_prompt, tool_prompt)
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"{label}   WARN: Judge returned invalid JSON, retrying... ({exc})")
        try:
            baseline_scores, tool_scores = judge_prompts(
                client, task, baseline_prompt, tool_prompt
            )
        except Exception as exc2:
            print(f"{label}   ERROR: Judge failed: {exc2}")
            baseline_scores = {d: 0 for d in RUBRIC_DIMENSIONS}
            tool_scores = {d: 0 for d in RUBRIC_DIMENSIONS}

    b_overall = baseline_scores.get("Overall", 0)
    t_overall = tool_scores.get("Overall", 0)
    print(f"{label}   Done. Baseline: {b_overall}/10 | Tool: {t_overall}/10")

    return {
        "idx": task_idx,
        "task": task,
        "baseline_prompt": baseline_prompt,
        "tool_prompt": tool_prompt,
        "baseline_scores": baseline_scores,
        "tool_scores": tool_scores,
    }


def main() -> None:
    print("Meta-Prompt MCP Benchmark")
    print(f"   Generator: {GENERATOR_MODEL}")
    print(f"   Judge:     {JUDGE_MODEL}")
    print(f"   Tasks:     {len(BENCHMARK_TASKS)} (parallel)")
    print()

    client = _client()
    guides = _load_guides()

    if not guides.strip():
        print("ERROR: Could not load prompting guides from", DATA_DIR)
        sys.exit(1)

    results: list[dict] = []

    with ThreadPoolExecutor(max_workers=len(BENCHMARK_TASKS)) as pool:
        futures = {
            pool.submit(_run_single_task, i, task, client, guides): i
            for i, task in enumerate(BENCHMARK_TASKS, 1)
        }
        for future in as_completed(futures):
            results.append(future.result())

    # Sort by original task order
    results.sort(key=lambda r: r["idx"])

    # Build and write report
    report = build_report(results)
    RESULTS_PATH.write_text(report, encoding="utf-8")
    print(f"\nResults written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()

