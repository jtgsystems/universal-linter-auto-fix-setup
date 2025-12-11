![Banner](banner.png)

# ✨ Universal Linter Auto-Fix Setup

[![npm](https://img.shields.io/badge/npm-template-informational)](https://www.npmjs.com/package/universal-linter-auto-fix-setup)
[![GitHub](https://img.shields.io/badge/repo-jtgsystems/universal--linter--auto--fix--setup-24292F?logo=github&logoColor=white)](https://github.com/jtgsystems/universal-linter-auto-fix-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

The plug-and-play toolkit for opinionated, auto-fixing linting across modern Node.js and web projects. Drop it in, run `npm install`, and enjoy consistent code on every save and commit. 🧼

---

## 🚀 What's Inside

- **ESLint 9 (flat config)** + Prettier integration for JS/TS sanity.
- **Stylelint 16** + SCSS plugin to keep styles squeaky clean.
- **Prettier 3** for JSON, YAML, Markdown, HTML, TOML, and more.
- **Husky + lint-staged** so every commit fixes itself before it lands.
- **Performance Optimization Suite**:
  - `opti_scanner.py`: A regex-based scanner for Dec 2025 optimization patterns across Python (3.14+), Go (1.25+), Rust (2024), and Node.js.
  - `smart_fixer.py`: An automated fixer that applies these optimizations.
  - `perf_researcher.py`: A tool to actively research new performance trends using LLMs.
- Sensible defaults for browser + Node globals, with overrides ready to tweak.

## 🛠️ Quick Start

1. **Clone or copy the template**

   ```bash
   git clone https://github.com/jtgsystems/universal-linter-auto-fix-setup.git my-project
   cd my-project
   ```

2. **Install dependencies (installs Husky hook automatically)**

   ```bash
   npm install
   ```

3. **Run Optimization Scan (New!)**

   ```bash
   python3 opti_scanner.py
   python3 smart_fixer.py # To auto-apply fixes
   ```

4. **Format everything (optional warm-up)**

   ```bash
   npm run format:all
   ```

4. **Commit with confidence** – any staged files are auto-fixed thanks to lint-staged + Husky. ✅

> Bringing this into an existing repo? Copy the config files (`eslint.config.js`, `.stylelintrc.json`, `.prettierrc.json`, `.prettierignore`, `.husky/`) and merge the `scripts`, `devDependencies`, and `lint-staged` block into your `package.json`.

## 📜 npm Scripts

| Command                 | What it does                               |
| ----------------------- | ------------------------------------------ |
| `npm run lint`          | ESLint check for JS/TS (no fixes)          |
| `npm run lint:fix`      | ESLint with auto-fix                       |
| `npm run stylelint`     | Stylelint check for CSS/SCSS               |
| `npm run stylelint:fix` | Stylelint with auto-fix                    |
| `npm run format`        | Prettier write across supported files      |
| `npm run format:check`  | Prettier check mode (CI friendly)          |
| `npm run format:all`    | Runs ESLint fix → Stylelint fix → Prettier |

`lint-staged` mirrors that behaviour on staged files so only the files you touched are processed during commits.

## 🧠 Config Highlights

### ESLint (`eslint.config.js`)

- Flat config powered by `@eslint/js` and `@typescript-eslint`.
- Shared browser + Node globals via `globals` package.
- Prettier plugin surfaces formatting drift as ESLint errors.

### Prettier (`.prettierrc.json`)

- 80 character lines, 2-space indentation, single quotes.
- JSON files widen to 100 chars; YAML keeps 2-space softness.

### Stylelint (`.stylelintrc.json`)

- Extends Standard + SCSS + Recommended presets.
- Includes `stylelint-scss` for modern SCSS linting rules.

### Git Automation

- `.husky/pre-commit` runs `npx lint-staged`.
- `lint-staged` block lives in `package.json` so you can tweak per file type.

## 💡 VS Code On-Save Magic

Add this to `.vscode/settings.json` for instant feedback:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.fixAll.stylelint": "explicit"
  },
  "eslint.experimental.useFlatConfig": true
}
```

_Tip: install the ESLint, Prettier, and Stylelint extensions for the best experience._

## 🔧 Customisation Ideas

- Need React, Vitest, Jest, or Next.js rules? Add their plugins and extend the ESLint array.
- Want different Prettier widths? Tweak `printWidth` and `tabWidth`.
- Strict CSS conventions? Layer in `stylelint-order` or custom rules.

## 🆘 Troubleshooting

- **Husky hook not firing?** Ensure `npm install` ran (it triggers the `prepare` script) and that `.husky/pre-commit` is executable.
- **ESLint complaining about parser options?** Create a `tsconfig.json` or swap to `@typescript-eslint/eslint-plugin`'s type-checked config if you need type-aware rules.
- **Prettier missing file types?** Add new globs to the `lint-staged` block or run Prettier directly on folders.

## 🤝 Contributing & Feedback

PRs, issues, and stars are all welcome! Feel free to open a discussion if you have ideas for additional presets.

## 📄 License

Released under the [MIT License](LICENSE). Have fun building! ✌️

Made with ❤️ for teams that want linting to “just work.”

### SEO Keyword Cloud

`eslint` `stylelint` `prettier` `husky` `lintstaged` `autofix` `nodejs` `javascript` `typescript` `css` `scss` `formatting` `quality` `pipeline` `ci` `automation` `hooks` `git` `precommit` `vscode` `editor` `tooling` `workflow` `productivity` `codestyle` `standards` `configuration` `templates` `setup` `boilerplate` `devops` `testing` `coverage` `refactor` `maintainability` `consistency` `bestpractices` `guidelines` `teams` `collaboration` `monorepo` `microservices` `webapps` `frontend` `backend` `scripts` `cli` `npm` `package` `repository`
