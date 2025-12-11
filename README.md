# 🔍 MasterLinter

> **The Ultimate Multi-Language Performance & Code Quality Scanner**  
> 59 optimization rules across Python, TypeScript, Go, Rust, Mojo, and Shell

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![Dec 2025](https://img.shields.io/badge/Updated-Dec%202025-green.svg)]()

---

## 🚀 Features

### OptiScanner (`opti_scanner.py`)
A lightning-fast optimization pattern detector with **59 rules** covering:

| Language | Rules | Focus Areas |
|----------|-------|-------------|
| **Python** | 26 | Atomic I/O, Circuit Breakers, Caching, PEP modernization, Perflint anti-patterns |
| **TypeScript/React** | 11 | Next.js 15, Server Components, Class→Hooks migration, JSON optimization |
| **Go** | 6 | json/v2 migration, strings.Builder, sync/atomic, goroutine pools |
| **Rust** | 8 | unwrap safety, String::with_capacity, iterator chains, serde optimization |
| **Mojo** | 5 | def→fn migration, static dispatch, SIMD optimization |
| **Shell** | 3 | grep→ripgrep, find→fd, os.system→subprocess |

### SmartFixer (`smart_fixer.py`)
LLM-powered automatic code fixer that:
- 🔍 Scans using OptiScanner + TScanner
- 🤖 Uses GPT-OSS to generate minimal SEARCH/REPLACE patches
- ✅ Verifies fixes before applying
- 🔄 Self-corrects up to 3 attempts per file
- 🌿 Operates on isolated Git branches for safety

### PerfResearcher (`perf_researcher.py`)
Ollama-powered research bot that:
- 📚 Researches latest optimization patterns (Python 3.14, Go 1.25, Rust 2024, etc.)
- 💾 Saves findings to JSON for rule integration
- 🔄 Uses local LLMs (gemma3, qwen3, etc.)

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/jtgsystems/MasterLinter.git
cd MasterLinter

# Install Python dependencies (for scanner)
pip install pathlib

# Install Node dependencies (for ESLint/Prettier/Stylelint)
npm install
```

---

## 🛠️ Usage

### Scan your codebase
```bash
# Run OptiScanner
python opti_scanner.py

# Output shows HIGH/MEDIUM/LOW priority findings
# [HIGH] path/to/file.py:42 - Use atomic_open for writes
# [MEDIUM] path/to/file.py:67 - Use .values() instead of .items() (10-15% faster)
```

### Auto-fix issues
```bash
# Run SmartFixer (requires OpenRouter API key)
export OPENROUTER_API_KEY=your_key_here
python smart_fixer.py
```

### Research new patterns
```bash
# Run PerfResearcher (requires local Ollama)
ollama serve &
python perf_researcher.py
```

---

## 📋 Rule Categories

### Python Performance (Dec 2025)
| ID | Pattern | Benefit |
|----|---------|---------|
| `OPT-IO-001` | `open(path, "w")` | Use atomic_open to prevent corruption |
| `OPT-PERF-PY-002` | `for _, v in d.items()` | Use `.values()` (10-15% faster) |
| `OPT-PERF-PY-005` | `for x: result.append()` | Use list comprehension (25% faster) |
| `OPT-RES-PY-002` | `run_in_executor()` | Use `asyncio.to_thread()` (Python 3.9+) |

### Go Performance (Go 1.25+)
| ID | Pattern | Benefit |
|----|---------|---------|
| `OPT-GO-001` | `encoding/json` | Use json/v2 (3-10x faster) |
| `OPT-RES-GO-001` | `"a" + "b" + "c"` | Use `strings.Builder` |
| `OPT-RES-GO-003` | `sync.Mutex` | Consider `sync/atomic` for short sections |

### TypeScript/React (Next.js 15+)
| ID | Pattern | Benefit |
|----|---------|---------|
| `OPT-RES-TS-001` | `class extends Component` | Use functional + hooks |
| `OPT-RES-TS-002` | `getServerSideProps` | Use Server Components |

---

## 🔧 Configuration

### ESLint (JavaScript/TypeScript)
```bash
# Lint
npm run lint

# Fix
npm run lint:fix
```

### Prettier (Formatting)
```bash
npm run format
```

### Stylelint (CSS/SCSS)
```bash
npm run lint:styles
```

---

## 📊 Research Sources

Rules are derived from:
- **perflint** ([tonybaloney/perflint](https://github.com/tonybaloney/perflint)) - Python anti-patterns
- **Staticcheck** ([dominikh/go-tools](https://github.com/dominikh/go-tools)) - Go linting
- **Clippy** - Rust performance lints
- **Ollama Research** - Dec 2025 patterns via local LLMs

---

## 🤝 Contributing

1. Fork the repo
2. Add new rules to `opti_scanner.py` following the pattern:
```python
OptimizationRule(
    id="OPT-LANG-XXX",
    pattern=r"your_regex_pattern",
    suggestion="Your helpful suggestion here.",
    priority="HIGH|MEDIUM|LOW",
),
```
3. Submit a PR

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Credits

Built with ❤️ by [JTG Systems](https://github.com/jtgsystems)

**Powered by:**
- Python 3.12+ / Node.js 22+
- ESLint 9 / Prettier 3 / Stylelint 16
- OpenRouter / Ollama for AI-assisted fixing
