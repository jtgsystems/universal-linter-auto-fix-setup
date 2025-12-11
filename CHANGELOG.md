# Changelog

All notable changes to MasterLinter.

## [2.0.0] - 2025-12-11

### Added
- **59 optimization rules** across 6 languages
- **OptiScanner**: Multi-language pattern detector
- **SmartFixer**: LLM-powered automatic code fixer
- **PerfResearcher**: Ollama-based research bot for new patterns

### Rule Categories Added
- **Python (26 rules)**: IO safety, resilience, caching, perflint anti-patterns
- **TypeScript (11 rules)**: Next.js 15, Server Components, hooks migration
- **Go (6 rules)**: json/v2, strings.Builder, sync/atomic
- **Rust (8 rules)**: unwrap safety, capacity hints, iterator chains
- **Mojo (5 rules)**: static dispatch, SIMD optimization
- **Shell (3 rules)**: modern CLI tool recommendations

### Research Sources Integrated
- perflint (Python anti-patterns with proven speedups)
- Staticcheck (Go linting)
- Clippy (Rust performance lints)
- Dec 2025 LLM research via Ollama

## [1.0.0] - 2025-01-01

### Initial Release
- ESLint 9 configuration
- Prettier 3 formatting
- Stylelint 16 for CSS/SCSS
- Husky pre-commit hooks
- lint-staged configuration
