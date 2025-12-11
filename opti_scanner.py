import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class OptimizationRule:
    def __init__(
        self, id: str, pattern: str, suggestion: str, priority: str = "MEDIUM"
    ):
        self.id = id
        self.pattern = re.compile(pattern)
        self.suggestion = suggestion
        self.priority = priority


# --- DEFINITIONS FILE (In-Code for now, can be extracted to json) ---
# --- PYTHON RULES ---
PY_RULES = [
    # --- IO & PERSIESTENCE ---
    OptimizationRule(
        id="OPT-IO-001",
        pattern=r"(with\s+)?open\s*\([^)]*['\"]w[b\+]?['\"]",
        suggestion="Use `priority_core.file_ops.atomic_open` to prevent corruption. Standard `open('w')` truncates immediately.",
        priority="HIGH",
    ),
    # --- CONCURRENCY & RESILIENCE ---
    OptimizationRule(
        id="OPT-RES-001",
        pattern=r"time\.sleep\s*\(\s*[0-9]+",
        suggestion="Hardcoded blocking sleep detected. Use `asyncio.sleep` or `priority_core.resilience.BackoffStrategy`.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RES-002",
        pattern=r"(requests|httpx|aiohttp)\.(get|post|put|delete)",
        suggestion="Unprotected external call. Wrap in `priority_core.resilience.CircuitBreaker` to handle timeouts/failures.",
        priority="HIGH",
    ),
    OptimizationRule(
        id="OPT-RES-003",
        pattern=r"asyncio\.create_task\s*\(",
        suggestion="Fire-and-forget task? Ensure it's tracked (e.g. `BackgroundTasks` or `TaskGroup`) to prevent swallowing exceptions.",
        priority="LOW",
    ),
    # --- CACHING & MEMORY ---
    OptimizationRule(
        id="OPT-MEM-001",
        pattern=r"(_?cache|_?memo|_?registry)\s*=\s*({}|dict\(\))",
        suggestion="Unbounded dictionary cache. Upgrade to `priority_core.smart_cache.ErrorInducedEvictionCache` to prevent OOM.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-PERF-001",
        pattern=r"\s+\+=\s+.*(str|f[\"'])",
        suggestion="String concatenation in loop? Use `list.append` and `''.join()` for O(n) performance.",
        priority="LOW",
    ),
    # --- OBSERVABILITY ---
    OptimizationRule(
        id="OPT-OBS-001",
        pattern=r"^\s*print\s*\(",
        suggestion="Blocking `print` call. Use `logger.info/debug` for non-blocking async logging and structured output.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-OBS-002",
        pattern=r"except\s+Exception\s*:",
        suggestion="Broad exception catch. Catch specific errors or ensure you log `exc_info=True`.",
        priority="MEDIUM",
    ),
    # --- PYTHON 3.12+ MODERNIZATION ---
    OptimizationRule(
        id="OPT-PY12-001",
        pattern=r"(['\"].*?['\"]\s*%\s*\(|['\"].*?['\"]\s*\.format\()",
        suggestion="Legacy string formatting detected. Use f-strings for better performance and readability.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-PY12-002",
        pattern=r"\.append\(",
        suggestion="Loop growing a list? In Python 3.12, List Comprehensions are inlined and significantly faster.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-PY12-003",
        pattern=r"type\(.+?\)\s*==\s*.+?",
        suggestion="Type checking with `type() ==` is slow and brittle. Use `isinstance()`.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-PY12-004",
        pattern=r"isinstance\(.+?\)\s+or\s+isinstance\(.+?\)",
        suggestion="Multiple `isinstance` checks found. Use `isinstance(obj, (A, B))` tuple check for faster execution.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-PY14-001",
        pattern=r"import\s+multiprocessing",
        suggestion="Python 3.14+ Sub-interpreters (PEP 734) offer lighter true parallelism than `multiprocessing`. Consider `interpreters` module.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-PY14-002",
        pattern=r"template\.render\(",
        suggestion="Python 3.14+ 't-strings' (PEP 750) provide safer, faster, native templating than external renderers.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-PY14-003",
        pattern=r"uuid\.uuid(3|4|5)\(\)",
        suggestion="Python 3.14 optimizes UUID generation (40% faster). Ensure you are on the latest runtime.",
        priority="LOW",
    ),
]

# --- TYPESCRIPT / REACT / NODE ECOSYSTEM RULES ---
TS_RULES = [
    OptimizationRule(
        id="OPT-TS-001",
        pattern=r"console\.log\(",
        suggestion="Console log in production code. Remove or use a proper logger.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-TS-002",
        pattern=r":\s*any",
        suggestion="Usage of 'any' type defeats TypeScript benefits. Define a strict interface.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-TS-003",
        pattern=r"<img\s+",
        suggestion="Standard <img> tag detected. Use Next.js `<Image />` for automatic optimization/lazy-loading.",
        priority="HIGH",
    ),
    OptimizationRule(
        id="OPT-TS-004",
        pattern=r"useEffect\(\s*\(\)\s*=>\s*{.*}\)\s*$",
        suggestion="useEffect missing dependency array. This runs on EVERY render. Pass `[]` or explicit deps.",
        priority="HIGH",
    ),
    OptimizationRule(
        id="OPT-NODE-001",
        pattern=r"\"husky\":\s*\"^[0-4]\.",
        suggestion="Legacy Husky detected. Upgrade to Husky v9+ for 1ms overhead and native git hooks.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-NODE-002",
        pattern=r"\"lint-staged\":\s*{",
        suggestion="Ensure `lint-staged` v16+ is used with `--hide-unstaged` for cleaner commits.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-NODE-003",
        pattern=r"npm\s+deprecate",
        suggestion="npm 11+ offers `npm undeprecate` and better deprecation handling. Modernize your scripts.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-CSS-001",
        pattern=r"stylelint-config-standard-scss",
        suggestion="Ensure Stylelint v16+ is used. It fixes false positives and supports modern CSS syntax natively.",
        priority="LOW",
    ),
]

# --- GO RULES (Go 1.25+) ---
GO_RULES = [
    OptimizationRule(
        id="OPT-GO-001",
        pattern=r"encoding/json",
        suggestion="Legacy `encoding/json` detected. Go 1.25+ `encoding/json/v2` is 3-10x faster and zero-alloc.",
        priority="HIGH",
    ),
    OptimizationRule(
        id="OPT-GO-002",
        pattern=r"GOMAXPROCS",
        suggestion="Manual GOMAXPROCS tuning? Go 1.25 is container-aware by default. Remove manual overrides.",
        priority="LOW",
    ),
]

# --- RUST RULES (2024 Edition / 2025) ---
RUST_RULES = [
    OptimizationRule(
        id="OPT-RS-001",
        pattern=r"\.unwrap\(\)",
        suggestion="Unsafe unwrap(). Use `match` or `?` operator to handle potential panics gracefully.",
        priority="HIGH",
    ),
    OptimizationRule(
        id="OPT-RS-002",
        pattern=r"fn\s+[a-z_]+\s*\(.*:\s*String\)",
        suggestion="Taking `String` ownership in args forces allocation. Accept `&str` to allow zero-copy slices.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RS-003",
        pattern=r"Vec::new\(\)",
        suggestion="Allocation loop ahead? Use `Vec::with_capacity(n)` to prevent resizing overhead.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RS-004",
        pattern=r"async\s+move\s*\{\s*\}",
        suggestion="Legacy async block inside closure? Rust 2024 supports native `async || {}` closures.",
        priority="MEDIUM",
    ),
]


# --- MOJO RULES ---
MOJO_RULES = [
    OptimizationRule(
        id="OPT-MOJO-001",
        pattern=r"def\s+[a-zA-Z0-9_]+\s*\(",
        suggestion="Using `def` (dynamic). For high performance, use `fn` (static) and explicit types.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-MOJO-002",
        pattern=r"var\s+[a-zA-Z0-9_]+\s*=",
        suggestion="Variable declared with `var`. If immutable, use `let` for better compiler optimization.",
        priority="LOW",
    ),
]

# --- SHELL / CLI COMMAND RULES (detected in Python subprocess or Shell scripts) ---
# We scan .py files for subprocess calls and .sh files for direct calls
SHELL_RULES = [
    OptimizationRule(
        id="OPT-CLI-001",
        pattern=r"grep\s+(-r|-R|--recursive)?",
        suggestion="Legacy `grep` detected. Use `ripgrep` (`rg`) for 10x faster searching.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-CLI-002",
        pattern=r"find\s+\.\s+-name",
        suggestion="Legacy `find` detected. Use `fd` (fd-find) for faster file system traversal.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-CLI-003",
        pattern=r"os\.system\s*\(",
        suggestion="`os.system` is blocking and insecure. Use `subprocess.run` or `asyncio.create_subprocess_exec`.",
        priority="HIGH",
    ),
]


def get_rules_for_file(file_path: Path) -> List[OptimizationRule]:
    suffix = file_path.suffix.lower()
    if suffix == ".py":
        # Python gets its own rules + Shell rules (for subprocess calls)
        return PY_RULES + SHELL_RULES
    elif suffix in [".ts", ".tsx", ".js", ".jsx"]:
        return TS_RULES
    elif suffix == ".go":
        return GO_RULES
    elif suffix == ".rs":
        return RUST_RULES
    elif suffix in [".mojo", ".🔥"]:
        return MOJO_RULES
    elif suffix == ".sh":
        return SHELL_RULES
    return []


# --- IGNORE LIST (Global Defaults for Polyglot Repos) ---
GLOBAL_IGNORE_DIRS = {
    # Version Control
    ".git",
    ".svn",
    ".hg",
    # Python
    "__pycache__",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    "site-packages",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "eggs",
    ".eggs",
    # Node/Web/JS
    "node_modules",
    ".next",
    ".nuxt",
    "coverage",
    ".yarn",
    "bower_components",
    "jspm_packages",
    "out",
    ".cache",
    # Rust / Go / Java
    "target",
    "vendor",
    "bin",
    "pkg",
    ".gradle",
    # IDEs / Editors
    ".idea",
    ".vscode",
    ".history",
    # Archives / Backups / Temporary
    "04_ARCHIVE",
    "04_ARCHIVE(1)",
    "archive",
    "backups",
    "backup",
    "tmp",
    "temp",
    "logs",
    "recycler",
    "$RECYCLE.BIN",
    "legacy",
    "old",
    "deprecated",
    "migrated",
    "_backup",
    "_ARCHIVE",
    "_archive",
    "_old",
    "_tmp",
    "_temp",
}

IGNORE_EXTENSIONS = {
    ".bak",
    ".old",
    ".tmp",
    ".swp",
    ".log",
    ".orig",
    ".rej",
}


def scan_file(file_path: Path) -> List[Dict[str, Any]]:
    # Extension Check
    if file_path.suffix in IGNORE_EXTENSIONS:
        return []

    # Path Name Check (Extra Safety for backup files like 'foo.py_backup')
    name_lower = file_path.name.lower()
    if "_backup" in name_lower or "backup_" in name_lower:
        return []

    rules = get_rules_for_file(file_path)
    if not rules:
        return []

    findings = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith(("#", "//")):
                continue

            for rule in rules:
                if rule.pattern.search(line):
                    findings.append(
                        {
                            "rule_id": rule.id,
                            "file": str(file_path),
                            "line": i + 1,
                            "code": line.strip(),
                            "suggestion": rule.suggestion,
                            "priority": rule.priority,
                        }
                    )
    except Exception:
        pass  # Skip binary or unreadable

    return findings


def main():
    total_rules = (
        len(PY_RULES)
        + len(TS_RULES)
        + len(GO_RULES)
        + len(RUST_RULES)
        + len(MOJO_RULES)
        + len(SHELL_RULES)
    )
    logger.info(f"{CYAN}🔍 Initializing Optimization Scanner (The 'Scout')...{RESET}")
    logger.info(
        f"{CYAN}🎯 Loaded {total_rules} optimization definitions (covering Py, TS, Go, Rs, Mojo, Shell).{RESET}"
    )

    root_dir = Path(os.getcwd())
    all_findings = []

    file_count = 0
    # Walk and Scan
    for root, dirs, files in os.walk(root_dir):
        # normalize path
        root_path = Path(root)

        # Modify dirs in-place to prune traversal (Performance Check)
        # We explicitly remove any directory appearing in our global ignore list
        dirs[:] = [d for d in dirs if d not in GLOBAL_IGNORE_DIRS]

        # Double check: Skip if we are inside a package directory (detected via path parts)
        # This catches nested site-packages or hidden .venv folders in case walk structure is redundant
        if any(part in GLOBAL_IGNORE_DIRS for part in root_path.parts):
            continue

        for file in files:
            file_count += 1
            if file_count % 100 == 0:
                logger.info(f"Scanned {file_count} files... (Current: {file})")

            # Basic extension filter to avoid opening binaries
            if "." not in file:
                continue

            path = Path(root) / file

            # Skip the scanner itself and the source definitions
            if path.name in [
                "opti_scanner.py",
                "resilience.py",
                "file_ops.py",
                "smart_cache.py",
            ]:
                continue

            hits = scan_file(path)
            all_findings.extend(hits)

    # Report
    if not all_findings:
        logger.info(f"{GREEN}✅ No obvious optimization opportunities found.{RESET}")
    # Results Summary
    if all_findings:
        # Sort by priority (HIGH > MEDIUM > LOW)
        priority_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        all_findings.sort(key=lambda x: priority_map.get(x["priority"], 3))

        for f in all_findings:
            color = (
                RED
                if f["priority"] == "HIGH"
                else YELLOW
                if f["priority"] == "MEDIUM"
                else CYAN
            )
            logger.info(f"\n[{color}{f['priority']}{RESET}] {f['file']}:{f['line']}")
            logger.info(f"   Match: {f['code']}")
            logger.info(f"   Tip:   {f['suggestion']}")
    else:
        logger.info(
            f"\n{GREEN}✅ No optimization opportunities found! The codebase is pristine.{RESET}"
        )
    logger.info(
        f"{CYAN}👉 Recommended Action: Use 'smart_fixer' on high-priority files to apply these patterns.{RESET}"
    )


if __name__ == "__main__":
    main()
