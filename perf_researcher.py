import asyncio
import json
import logging
import sys
from pathlib import Path

# --- 1. SETUP & IMPORTS ---
# Ensure we can import from backend/app/priority_core
sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "backend" / "app" / "priority_core"))

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("perf_researcher")

try:
    from backend.app.priority_core.file_ops import atomic_write, safe_read_file
    from backend.app.priority_core.model_router import UnifiedModelRouter
    from backend.app.priority_core.resilience import ResilientExecutor
except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    logger.error("Ensure you are running from the ULTRON_V3 root directory.")
    sys.exit(1)

# --- 2. CONFIGURATION ---
RESEARCH_TARGETS = [
    "Python 3.12+ 3.13 performance optimization",
    "TypeScript React Next.js 15+ performance patterns",
    "Go 1.23+ performance optimization",
    "Rust 2024 Edition performance best practices",
    "Mojo Language vs Python performance benchmarks",
]

OUTPUT_DIR = Path("04_ARCHIVE/research_findings")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- 3. PROMPTS ---
RESEARCH_PROMPT_TEMPLATE = """
As an expert Performance Engineer, research the latest OFFICIAL performance optimization patterns for {target} as of December 2025.
Focus on:
1. New language features that replace slower legacy patterns.
2. Compiler flags or runtime settings (e.g., GC tuning, JIT).
3. Standard library improvements (e.g. faster JSON, better regex).
4. Deprecated patterns to avoid.

Return the findings in this exact JSON format:
{{
    "target": "{target}",
    "patterns": [
        {{
            "name": "Validation via tuple",
            "legacy": "type(x) == int",
            "modern": "isinstance(x, int)",
            "benefit": "Faster, supports inheritance"
        }}
    ],
    "sources": ["official_docs", "benchmarks"]
}}
"""


# --- 4. RESEARCH LOGIC ---
async def conduct_research(target: str, router: UnifiedModelRouter):
    logger.info(f"🔎 Researching: {target}...")

    prompt = RESEARCH_PROMPT_TEMPLATE.format(target=target)

    try:
        # Use a high-reasoning model for research
        response = await router.chat(
            system_prompt="You are a specialized research agent.",
            user_message=prompt,
            model_preference="codex_cli",  # Or appropriate model
        )

        # Save raw finding
        safe_name = target.replace(" ", "_").replace("+", "plus").lower()
        filename = OUTPUT_DIR / f"{safe_name}.json"

        # Clean response to get JSON
        content = response.get("content", "{}")
        # Basic markdown fence stripping
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        atomic_write(filename, content)
        logger.info(f"✅ Findings saved to {filename}")
        return content

    except Exception as e:
        logger.error(f"❌ Failed to research {target}: {e}")
        return None


async def main():
    logger.info("🚀 Starting Global Performance Research Task (Dec 2025 Standards)")

    router = UnifiedModelRouter()
    executor = ResilientExecutor()  # Using our new resilience class

    tasks = []
    for target in RESEARCH_TARGETS:
        tasks.append(conduct_research(target, router))

    results = await asyncio.gather(*tasks)

    logger.info("🏁 Research complete. Aggregating results...")

    # Create a master report
    master_report = []
    for res in results:
        if res:
            try:
                master_report.append(json.loads(res))
            except:
                pass

    atomic_write(
        OUTPUT_DIR / "master_report_dec_2025.json", json.dumps(master_report, indent=2)
    )
    logger.info(
        f"📜 Master report saved to {OUTPUT_DIR / 'master_report_dec_2025.json'}"
    )


if __name__ == "__main__":
    asyncio.run(main())
