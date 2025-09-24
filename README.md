# Universal Linter Auto-Fix Setup

[![npm version](https://badge.fury.io/js/universal-linter-auto-fix-setup.svg)](https://badge.fury.io/js/universal-linter-auto-fix-setup)
[![GitHub license](https://img.shields.io/github/license/jtgsystems/universal-linter-auto-fix-setup)](https://github.com/jtgsystems/universal-linter-auto-fix-setup/blob/master/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/jtgsystems/universal-linter-auto-fix-setup)](https://github.com/jtgsystems/universal-linter-auto-fix-setup/issues)

This is a portable, Git-ready, all-in-one setup for auto-formatting and linting Node.js (and web) projects to the highest standards. It supports JS/TS (ESLint 9 flat config + Prettier), CSS/SCSS (Stylelint + Prettier), YAML/JSON/HTML/MD/TOML (Prettier), and more. Auto-fixes on VS Code save and Git pre-commit (Husky + lint-staged). Ensures W3C-compliant HTML/CSS, ECMAScript JS, YAML 1.2, and best practices across files.

## Why This Setup?
- **Latest & Best**: ESLint 9.11.1 (flat config for performance), Prettier 3.3.3, Stylelint 16.8.1, TypeScript ESLint 8.8.1 (Sept 2025 versions).
- **Auto-Fix Everything**: Fixes formatting, lint errors, unused vars, invalid CSS, etc., without manual intervention.
- **Web Standards**: HTML (self-closing tags, accessibility hints), CSS (no invalid hex, standard selectors), JS (no-console off for Node, semi-colons).
- **Portable**: Works on any Node.js project – clone, npm install, done.
- **Git-Integrated**: Pre-commit auto-fixes staged files; no bad code in PRs.
- **VS Code Ready**: Extensions + settings for on-save fixes.
- **Error-Free**: Resolves all peer deps with --legacy-peer-deps; tested on mixed file types.

## Supported File Types & Auto-Fix
- **JS/TS**: ESLint (lint + fix: unused vars, no-undef, consistent style) + Prettier (format: quotes, semis, 80-width).
- **CSS/SCSS**: Stylelint (lint + fix: no invalid hex, standard rules) + Prettier (format).
- **YAML**: Prettier (format: 2-space indent, no trailing commas, validation).
- **JSON**: Prettier (format: 100-width, strict).
- **HTML**: Prettier (format: CSS whitespace, no same-line brackets) + ESLint rules for accessibility.
- **MD**: Prettier (format: GitHub-flavored).
- **Other**: TOML, GraphQL, etc., via Prettier.

## Quick Start
1. **Clone the Repo**:
   ```
   git clone https://github.com/jtgsystems/universal-linter-auto-fix-setup.git my-project
   cd my-project
   ```

2. **Install Dependencies & Setup Hooks**:
   ```
   npm install
   npx husky install  # Installs Git hooks for pre-commit auto-fix
   ```

3. **Add Your Code**: Drop files in root or subdirs (e.g., `src/app.js`, `styles/main.scss`, `config.yaml`).

4. **Test Auto-Fix**:
   - CLI: `npm run format:all` (fixes entire project).
   - Git: `git add . && git commit -m "test"` (triggers pre-commit fix).
   - VS Code: Save files (auto-fixes if extensions/settings configured).

5. **VS Code Setup** (For On-Save Auto-Fix):
   - Install Extensions:
     - ESLint (dbaeumer.vscode-eslint)
     - Prettier - Code formatter (esbenp.prettier-vscode)
     - Stylelint (stylelint.vscode-stylelint)
   - Create `.vscode/settings.json`:
     ```
     {
       "editor.formatOnSave": true,
       "editor.defaultFormatter": "esbenp.prettier-vscode",
       "editor.codeActionsOnSave": {
         "source.fixAll.eslint": "explicit",
         "source.fixAll.stylelint": "explicit"
       },
       "eslint.experimental.useFlatConfig": true,
       "[javascript][typescript][html][css][scss][yaml][json][markdown]": {
         "editor.defaultFormatter": "esbenp.prettier-vscode"
       }
     }
     ```

## Scripts
- `npm run lint`: ESLint JS/TS files + auto-fix (e.g., remove unused vars, add semis).
- `npm run format`: Prettier all files + auto-fix (e.g., quotes, indentation).
- `npm run stylelint`: Stylelint CSS/SCSS + auto-fix (e.g., fix selectors, colors).
- `npm run format:all`: Full auto-fix (Prettier + ESLint + Stylelint) for entire project.
- Pre-Commit Hook: Auto-runs lint-staged on staged files (efficient, only fixes changed code).

## Configuration Details
### ESLint (eslint.config.js - Flat Config for Performance)
- **Version**: 9.11.1
- **Features**: TypeScript parsing, Node.js/browser globals, recommended rules, Prettier integration (no conflicts).
- **Key Rules**: no-unused-vars (warn), no-undef (warn), prettier/prettier (error).
- **Ignores**: node_modules, dist, min files.

### Prettier (.prettierrc.json - Consistent Formatting)
- **Version**: 3.3.3
- **Settings**: 80-width, 2-space tabs, single quotes, semis, es5 trailing commas.
- **Overrides**:
  - JSON: 100-width.
  - YAML: 2-space, 80-width (YAML 1.2 standard).
  - HTML: CSS whitespace sensitivity, no same-line brackets (W3C best).
- **Supported**: 20+ languages; auto-fixes formatting to web standards.

### Stylelint (.stylelintrc.json - CSS/SCSS Standards)
- **Version**: 16.8.1
- **Extends**: standard, standard-scss, recommended, prettier.
- **Rules**: No unknown SCSS at-rules, dollar-var pattern, no redundant nesting, no invalid hex.
- **Ignores**: node_modules, dist.

### Git Integration
- **Husky**: Manages pre-commit hooks.
- **lint-staged** (.lintstagedrc.json): Runs fixes only on staged files:
  ```
  {
    "*.{js,ts}": "eslint --fix",
    "*.{css,scss}": "stylelint --fix",
    "*.{js,ts,json,css,scss,md,html,yaml}": "prettier --write"
  }
  ```
- On commit: Auto-fixes staged code to standards before pushing.

### Ignore Files
- .eslintignore, .prettierignore: Exclude node_modules, dist, minified files.

## Usage in Other Projects
1. **Copy Files**: package.json (devDeps), all configs (.prettierrc.json, eslint.config.js, .stylelintrc.json, .lintstagedrc.json), .husky/.
2. **Install**: `npm install` (deps + Husky prepare script).
3. **Hooks**: `npx husky install`.
4. **Test**: Add code, `git add . && git commit -m "test"` (auto-fixes).
5. **VS Code**: Copy .vscode/settings.json for on-save fixes.

For non-Node projects: Adapt package.json/scripts; Prettier works standalone.

## Examples
- **JS Fix**: Unused var removed, single quotes added.
- **HTML Fix**: Indented tags, self-closing <img />.
- **YAML Fix**: 2-space indent, no trailing commas.
- **CSS Fix**: Standard selectors, valid colors.

## Customization
- **Add Rules**: Edit eslint.config.js (e.g., `'no-console': 'off'` for Node).
- **Plugins**: Add React: `npm i -D eslint-plugin-react`, import in config.
- **Languages**: Python? Add black script; this focuses on web/Node.
- **Width**: Change printWidth in .prettierrc.json.

## Troubleshooting
- **Dep Conflicts**: `npm install --legacy-peer-deps`.
- **ESLint Errors**: Verify "type": "module" in package.json; use flat config.
- **No Auto-Fix**: Check extensions/settings; run `npm run format:all` manually.
- **Husky Not Working**: `npx husky install`; ensure Git repo initialized.
- **YAML Issues**: Prettier validates basic; for advanced, add yamllint.

## Contributing
- Fork, add features (e.g., new plugins), PR.
- Test: Run `npm run format:all` before commit.

## License
MIT – See LICENSE.

Built for developer productivity. Star/fork for your projects!
EOF && git add README.md && git commit -m "Update README with full instructions and about section" && gh repo edit --description "Portable auto-fix linter setup for Node.js/web projects: ESLint 9, Prettier, Stylelint with Git pre-commit hooks. Ensures W3C standards and best practices across JS/TS/CSS/YAML/HTML."