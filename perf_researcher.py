#!/usr/bin/env python3
"""
Performance Researcher - Uses Ollama + INFOGRABER pattern for Dec 2025 Optimization Research
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import ollama  # Direct Ollama integration like INFOGRABER

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("perf_researcher")

# --- Configuration ---
RESEARCH_TARGETS = [
    "Python 3.12 3.13 3.14 performance optimization patterns 2025",
    "TypeScript React Next.js 15 performance patterns 2025",
    "Go 1.23 1.24 1.25 performance optimization 2025",
    "Rust 2024 Edition performance best practices",
    "Mojo Language performance vs Python benchmarks 2025",
]

OUTPUT_DIR = Path("04_ARCHIVE/research_findings")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Default Model (using Gemma3 which is confirmed available)
DEFAULT_MODEL = "gemma3:12b"

# --- Research Prompt Template ---
RESEARCH_PROMPT = """You are an expert Performance Engineer researching the latest OFFICIAL performance optimization patterns for: {target}

Focus on:
1. New language features that replace slower legacy patterns.
2. Compiler flags or runtime settings (e.g., GC tuning, JIT).
3. Standard library improvements (e.g., faster JSON, better regex).
4. Deprecated patterns to avoid.

Return the findings in this exact JSON format:
{{
    "target": "{target}",
    "patterns": [
        {{
            "name": "Short descriptive name",
            "legacy": "The old/slow way",
            "modern": "The new/fast way",
            "benefit": "Why it's better"
        }}
    ],
    "sources": ["list", "of", "source", "types"]
}}

IMPORTANT: Return ONLY the JSON. No explanations, no markdown fences.
"""


def get_available_models() -> list[str]:
    """Get list of available Ollama models."""
    try:
        result = ollama.list()
        # The API returns {"models": [Model objects with .model attribute]}
        models_data = result.get("models", [])
        models = []
        for m in models_data:
            # Handle both dict and object responses
            if hasattr(m, "model"):
                # It's a Model object, get the .model attribute (the name string)
                models.append(m.model)
            elif isinstance(m, dict) and "name" in m:
                models.append(m["name"])
            elif isinstance(m, str):
                models.append(m)
        return models if models else [DEFAULT_MODEL]
    except Exception as e:
        logger.warning(f"Could not list Ollama models: {e}")
        return [DEFAULT_MODEL]


def research_topic(target: str, model: str = DEFAULT_MODEL) -> dict | None:
    """Conduct research on a single topic using Ollama."""
    logger.info(f"🔎 Researching: {target}...")

    prompt = RESEARCH_PROMPT.format(target=target)

    try:
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        content = response.get("response", "").strip()

        # Clean up response (remove markdown fences if present)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Try to parse as JSON
        try:
            parsed = json.loads(content)
            logger.info(
                f"✅ Found {len(parsed.get('patterns', []))} patterns for {target}"
            )
            return parsed
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Could not parse JSON for {target}, saving raw")
            return {"target": target, "raw_response": content, "patterns": []}

    except ollama.ResponseError as e:
        logger.error(f"❌ Ollama response error for {target}: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to research {target}: {e}")

    return None


def save_findings(findings: list[dict]) -> Path:
    """Save all findings to a master report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save individual findings
    for finding in findings:
        if finding:
            target = finding.get("target", "unknown")
            safe_name = target.replace(" ", "_").replace("+", "plus").lower()[:50]
            filename = OUTPUT_DIR / f"{safe_name}_{timestamp}.json"
            filename.write_text(json.dumps(finding, indent=2), encoding="utf-8")
            logger.info(f"📄 Saved: {filename.name}")

    # Save master report
    master_file = OUTPUT_DIR / f"master_report_{timestamp}.json"
    master_file.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    logger.info(f"📜 Master report: {master_file}")

    return master_file


def main():
    logger.info("🚀 Starting Performance Research (Ollama + INFOGRABER Pattern)")

    # Check available models
    models = get_available_models()
    model = (
        DEFAULT_MODEL if DEFAULT_MODEL in models else models[0] if models else "phi4"
    )
    logger.info(f"🤖 Using model: {model}")

    # Conduct research
    findings = []
    for target in RESEARCH_TARGETS:
        result = research_topic(target, model)
        if result:
            findings.append(result)

    # Save everything
    if findings:
        master_file = save_findings(findings)
        logger.info(f"\n🏁 Research complete! {len(findings)} topics researched.")
        logger.info(f"📁 Results saved to: {OUTPUT_DIR}")
    else:
        logger.warning("⚠️ No research findings generated.")


if __name__ == "__main__":
    main()
