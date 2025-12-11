# 🔍 MasterLinter

> **The Ultimate Multi-Language Performance & Code Quality Scanner**  
> 59 optimization rules across Python, TypeScript, Go, Rust, Mojo, and Shell

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![Dec 2025](https://img.shields.io/badge/Updated-Dec%202025-green.svg)]()

---

## 🚀 Features

### Python Tools (`python/`)

#### OptiScanner (`opti_scanner.py`)
A lightning-fast optimization pattern detector with **59 rules** covering:

| Language | Rules | Focus Areas |
|----------|-------|-------------|
| **Python** | 26 | Atomic I/O, Circuit Breakers, Caching, PEP modernization, Perflint anti-patterns |
| **TypeScript/React** | 11 | Next.js 15, Server Components, Class→Hooks migration, JSON optimization |
| **Go** | 6 | json/v2 migration, strings.Builder, sync/atomic, goroutine pools |
| **Rust** | 8 | unwrap safety, String::with_capacity, iterator chains, serde optimization |
| **Mojo** | 5 | def→fn migration, static dispatch, SIMD optimization |
| **Shell** | 3 | grep→ripgrep, find→fd, os.system→subprocess |

#### SmartFixer (`smart_fixer.py`)
LLM-powered automatic code fixer that:
- 🔍 Scans using OptiScanner + TScanner
- 🤖 Uses GPT-OSS to generate minimal SEARCH/REPLACE patches
- ✅ Provides **concrete BEFORE/AFTER code examples** to the LLM
- 🔄 Self-corrects up to 3 attempts per file
- 🌿 Operates on isolated Git branches for safety

#### PerfResearcher (`perf_researcher.py`)
Ollama-powered research bot that:
- 📚 Researches latest optimization patterns (Python 3.14, Go 1.25, Rust 2024)
- 💾 Saves findings to JSON for rule integration
- �� Uses local LLMs (gemma3, qwen3, etc.)

### JavaScript/TypeScript Tools (Root)
- **ESLint 9** - Modern flat config with auto-fix
- **Prettier 3** - Opinionated formatting
- **Stylelint 16** - CSS/SCSS linting
- **Husky + lint-staged** - Pre-commit hooks

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/jtgsystems/MasterLinter.git
cd MasterLinter

# Install Python dependencies
pip install pathlib

# Install Node dependencies (for ESLint/Prettier/Stylelint)
npm install
```

---

## 🛠️ Usage

### Python Scanner
```bash
cd python
python opti_scanner.py

# Output:
# [HIGH] path/to/file.py:42 - Use atomic_open for writes
#    FIX: BEFORE: with open(path, "w") as f:
#         AFTER:  with atomic_open(path, "w") as f:
```

### Auto-fix with LLM
```bash
export OPENROUTER_API_KEY=your_key_here
python python/smart_fixer.py
```

### Research new patterns
```bash
ollama serve &
python python/perf_researcher.py
```

### JavaScript/TypeScript
```bash
npm run lint        # ESLint check
npm run lint:fix    # ESLint auto-fix
npm run format      # Prettier format
npm run lint:styles # Stylelint check
```

---

## 📋 Key Rule Examples

| ID | Pattern | Fix |
|----|---------|-----|
| `OPT-PERF-PY-002` | `for _, v in d.items()` | `for v in d.values()` |
| `OPT-PERF-PY-005` | `for x: list.append()` | List comprehension |
| `OPT-IO-001` | `open(path, "w")` | `atomic_open(path, "w")` |
| `OPT-RES-002` | `requests.get(url)` | Wrap in `CircuitBreaker` |
| `OPT-GO-001` | `encoding/json` | `encoding/json/v2` |
| `OPT-RS-001` | `.unwrap()` | Use `?` operator |

---

## 📁 Project Structure

```
MasterLinter/
├── python/
│   ├── opti_scanner.py    # 59-rule pattern detector
│   ├── smart_fixer.py     # LLM-powered auto-fixer
│   └── perf_researcher.py # Ollama research bot
├── eslint.config.js       # ESLint 9 flat config
├── .prettierrc.json       # Prettier settings
├── .stylelintrc.json      # Stylelint settings
├── .husky/                # Git pre-commit hooks
├── package.json           # Node dependencies
├── CHANGELOG.md           # Version history
└── README.md              # This file
```

---

## 📊 Research Sources

Rules derived from:
- **perflint** ([tonybaloney/perflint](https://github.com/tonybaloney/perflint)) - Python anti-patterns with proven speedups
- **Staticcheck** ([dominikh/go-tools](https://github.com/dominikh/go-tools)) - Go linting
- **Clippy** - Rust performance lints
- **Dec 2025 LLM Research** via Ollama

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

Built with ❤️ by [JTG Systems](https://github.com/jtgsystems)
