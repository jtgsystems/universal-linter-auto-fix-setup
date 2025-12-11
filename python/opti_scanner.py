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
        self,
        id: str,
        pattern: str,
        suggestion: str,
        priority: str = "MEDIUM",
        fix_example: str = "",
    ):
        self.id = id
        self.pattern = re.compile(pattern)
        self.suggestion = suggestion
        self.priority = priority
        self.fix_example = fix_example  # Before→After code example for LLM


# --- DEFINITIONS FILE (In-Code for now, can be extracted to json) ---
# --- PYTHON RULES ---
PY_RULES = [
    # --- IO & PERSIESTENCE ---
    OptimizationRule(
        id="OPT-IO-001",
        pattern=r"(with\s+)?open\s*\([^)]*['\"]w[b\+]?['\"]",
        suggestion="Use `priority_core.file_ops.atomic_open` to prevent corruption. Standard `open('w')` truncates immediately.",
        priority="HIGH",
        fix_example='BEFORE: with open(path, "w") as f:\n    f.write(data)\nAFTER:  from priority_core.file_ops import atomic_open\nwith atomic_open(path, "w") as f:\n    f.write(data)',
    ),
    # --- CONCURRENCY & RESILIENCE ---
    OptimizationRule(
        id="OPT-RES-001",
        pattern=r"time\.sleep\s*\(\s*[0-9]+",
        suggestion="Hardcoded blocking sleep detected. Use `asyncio.sleep` or `priority_core.resilience.BackoffStrategy`.",
        priority="MEDIUM",
        fix_example="BEFORE: time.sleep(5)\nAFTER:  await asyncio.sleep(5)  # For async code\n# OR use BackoffStrategy for retry logic",
    ),
    OptimizationRule(
        id="OPT-RES-002",
        pattern=r"(requests|httpx|aiohttp)\.(get|post|put|delete)",
        suggestion="Unprotected external call. Wrap in `priority_core.resilience.CircuitBreaker` to handle timeouts/failures.",
        priority="HIGH",
        fix_example="BEFORE: response = requests.get(url)\nAFTER:  from priority_core.resilience import CircuitBreaker\ncb = CircuitBreaker()\nresponse = await cb.call(requests.get, url)",
    ),
    OptimizationRule(
        id="OPT-RES-003",
        pattern=r"asyncio\.create_task\s*\(",
        suggestion="Fire-and-forget task? Ensure it's tracked (e.g. `BackgroundTasks` or `TaskGroup`) to prevent swallowing exceptions.",
        priority="LOW",
        fix_example="BEFORE: asyncio.create_task(do_work())\nAFTER:  async with asyncio.TaskGroup() as tg:\n    tg.create_task(do_work())",
    ),
    # --- CACHING & MEMORY ---
    OptimizationRule(
        id="OPT-MEM-001",
        pattern=r"(_?cache|_?memo|_?registry)\s*=\s*({}|dict\(\))",
        suggestion="Unbounded dictionary cache. Upgrade to `priority_core.smart_cache.ErrorInducedEvictionCache` to prevent OOM.",
        priority="MEDIUM",
        fix_example="BEFORE: cache = {}\nAFTER:  from priority_core.smart_cache import ErrorInducedEvictionCache\ncache = ErrorInducedEvictionCache(max_size=1000)",
    ),
    OptimizationRule(
        id="OPT-PERF-001",
        pattern=r"\s+\+=\s+.*(str|f[\"'])",
        suggestion="String concatenation in loop? Use `list.append` and `''.join()` for O(n) performance.",
        fix_example='BEFORE:\nresult = ""\nfor s in items:\n    result += s\nAFTER:\nparts = []\nfor s in items:\n    parts.append(s)\nresult = "".join(parts)',
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
    # --- RESEARCH BOT FINDINGS (Dec 2025) ---
    OptimizationRule(
        id="OPT-RES-PY-001",
        pattern=r"if\s+.+:\s*\n.*elif\s+.+:\s*\n.*elif",
        suggestion="Long if/elif chains detected. Use `match` statement (Python 3.10+) for cleaner dispatch.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RES-PY-002",
        pattern=r"run_in_executor\s*\(",
        suggestion="Legacy executor pattern. Use `asyncio.to_thread()` (Python 3.9+) for cleaner blocking call offload.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RES-PY-003",
        pattern=r"bytes\([^)]+\)",
        suggestion="Copying bytes data? Use `memoryview` for zero-copy access to raw buffer data.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RES-PY-004",
        pattern=r"for\s+.+:\s*\n\s+.*self\.\w+.*self\.\w+",
        suggestion="Repeated attribute access in loop. Cache `self.attr` in local variable for faster access.",
        priority="LOW",
    ),
    # --- PERFLINT ANTI-PATTERNS (GitHub: tonybaloney/perflint) ---
    OptimizationRule(
        id="OPT-PERF-PY-001",
        pattern=r"for\s+\w+\s+in\s+list\(",
        suggestion="Unnecessary list() on iterable. Iterating directly is faster.",
        priority="MEDIUM",
        fix_example="BEFORE: for x in list(items):\nAFTER:  for x in items:",
    ),
    OptimizationRule(
        id="OPT-PERF-PY-002",
        pattern=r"for\s+_,\s*\w+\s+in\s+\w+\.items\(\)",
        suggestion="Discarding key in .items() loop. Use `.values()` instead (10-15% faster).",
        priority="MEDIUM",
        fix_example="BEFORE: for _, value in data.items():\nAFTER:  for value in data.values():",
    ),
    OptimizationRule(
        id="OPT-PERF-PY-003",
        pattern=r"for\s+\w+,\s*_\s+in\s+\w+\.items\(\)",
        suggestion="Discarding value in .items() loop. Use `.keys()` instead (10-15% faster).",
        priority="MEDIUM",
        fix_example="BEFORE: for key, _ in data.items():\nAFTER:  for key in data.keys():  # or just: for key in data:",
    ),
    OptimizationRule(
        id="OPT-PERF-PY-004",
        pattern=r"for\s+.+:\s*\n\s+try:",
        suggestion="try-except inside loop has overhead (pre-Python 3.10). Move loop inside try block.",
        priority="MEDIUM",
        fix_example="BEFORE:\nfor item in items:\n    try:\n        process(item)\n    except Error:\n        pass\nAFTER:\ntry:\n    for item in items:\n        process(item)\nexcept Error:\n    pass",
    ),
    OptimizationRule(
        id="OPT-PERF-PY-005",
        pattern=r"\[\s*\].*\n.*for\s+.+:\s*\n\s+.*\.append\(",
        suggestion="Building list with for-loop + append. Use list comprehension (25% faster).",
        priority="MEDIUM",
        fix_example="BEFORE:\nresult = []\nfor x in items:\n    result.append(x * 2)\nAFTER:\nresult = [x * 2 for x in items]",
    ),
    OptimizationRule(
        id="OPT-PERF-PY-006",
        pattern=r"=\s*\[\s*\"[^\"]+\"\s*,",
        suggestion="Non-mutated list literal? Use tuple instead for faster construction and indexing.",
        priority="LOW",
        fix_example='BEFORE: colors = ["red", "green", "blue"]\nAFTER:  colors = ("red", "green", "blue")',
    ),
    OptimizationRule(
        id="OPT-PERF-PY-007",
        pattern=r"for\s+.+:\s*\n\s+.*os\.\w+\.",
        suggestion="Dotted import in loop (os.path.xxx). Import directly for 10-15% speedup.",
        priority="LOW",
        fix_example="BEFORE:\nimport os\nfor f in files:\n    os.path.exists(f)\nAFTER:\nfrom os.path import exists\nfor f in files:\n    exists(f)",
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
    # --- RESEARCH BOT FINDINGS (Dec 2025) ---
    OptimizationRule(
        id="OPT-RES-TS-001",
        pattern=r"class\s+\w+\s+extends\s+(React\.)?Component",
        suggestion="Class components are legacy. Use functional components with hooks for better performance and smaller bundles.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RES-TS-002",
        pattern=r"getServerSideProps|getStaticProps",
        suggestion="Legacy data fetching. Next.js 15+ Server Components with `async` are faster and simpler.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RES-TS-003",
        pattern=r"JSON\.(parse|stringify)",
        suggestion="Large JSON operations? Consider `fast-json-stringify` for 2-5x speedup.",
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
    # --- RESEARCH BOT FINDINGS (Dec 2025) ---
    OptimizationRule(
        id="OPT-RES-GO-001",
        pattern=r'"\s*\+\s*"',
        suggestion="String concatenation with `+`. Use `strings.Builder` for O(n) performance in loops.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RES-GO-002",
        pattern=r"regexp\.Compile\(",
        suggestion="Compile regex inside function? Move to package level `var` for reuse and avoid re-compilation.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RES-GO-003",
        pattern=r"sync\.Mutex",
        suggestion="Mutex for short critical sections? Consider `sync/atomic` for lock-free performance.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RES-GO-004",
        pattern=r"go\s+func\(",
        suggestion="Excessive goroutine creation? Consider worker pools to reduce overhead.",
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
    # --- RESEARCH BOT FINDINGS (Dec 2025) ---
    OptimizationRule(
        id="OPT-RES-RS-001",
        pattern=r"String::new\(\)",
        suggestion="String allocation loop? Use `String::with_capacity(n)` to pre-allocate and avoid resizing.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RES-RS-002",
        pattern=r"\.collect::<Vec<",
        suggestion="Collecting into Vec for processing? Chain iterators directly to avoid intermediate allocations.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RES-RS-003",
        pattern=r"#\[inline\]",
        suggestion="Manual inlining? Profile first. Overuse increases binary size with marginal gains.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RES-RS-004",
        pattern=r"serde_json::(from_str|to_string)",
        suggestion="High-throughput JSON? Use `serde_json::with_capacity` or `postcard` for specialized perf.",
        priority="LOW",
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
    # --- RESEARCH BOT FINDINGS (Dec 2025) ---
    OptimizationRule(
        id="OPT-RES-MOJO-001",
        pattern=r"fn\s+[a-zA-Z0-9_]+\(",
        suggestion="Add `final` to methods returning `Self` for static dispatch and inlining benefits.",
        priority="LOW",
    ),
    OptimizationRule(
        id="OPT-RES-MOJO-002",
        pattern=r"import\s+Python",
        suggestion="Python interop has overhead. Re-implement perf-critical parts in native Mojo for max speed.",
        priority="MEDIUM",
    ),
    OptimizationRule(
        id="OPT-RES-MOJO-003",
        pattern=r"List\[",
        suggestion="Generic List detected. Use `Sequence` with explicit types for SIMD optimizations.",
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


def scan_text(
    content: str, extension: str, file_path_str: str = "memory"
) -> List[Dict[str, Any]]:
    """Scans raw text content using rules for the given extension."""
    mock_path = Path(f"dummy{extension}")
    rules = get_rules_for_file(mock_path)

    if not rules:
        return []

    findings = []
    lines = content.splitlines()

    for i, line in enumerate(lines):
        # Skip comments (Basic heuristic)
        if line.strip().startswith(("#", "//")):
            continue

        for rule in rules:
            if rule.pattern.search(line):
                findings.append(
                    {
                        "rule_id": rule.id,
                        "file": file_path_str,
                        "line": i + 1,
                        "code": line.strip(),
                        "suggestion": rule.suggestion,
                        "priority": rule.priority,
                        "fix_example": rule.fix_example,  # Concrete before/after code
                    }
                )

    return findings


def scan_file(file_path: Path) -> List[Dict[str, Any]]:
    # Extension Check
    if file_path.suffix in IGNORE_EXTENSIONS:
        return []

    # Path Name Check (Extra Safety for backup files like 'foo.py_backup')
    name_lower = file_path.name.lower()
    if "_backup" in name_lower or "backup_" in name_lower:
        return []

    # Pre-check rules to avoid reading file if no rules apply
    if not get_rules_for_file(file_path):
        return []

    try:
        content = file_path.read_text(encoding="utf-8")
        return scan_text(content, file_path.suffix, str(file_path))
    except Exception:
        pass  # Skip binary or unreadable

    return []


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
