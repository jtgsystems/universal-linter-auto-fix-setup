# Universal Linter Auto-Fix Setup - Project Documentation

This file contains comprehensive documentation for the Universal Linter Auto-Fix Setup project. Claude Code automatically loads this on startup when working in this repository.

---

## Project Overview

### Purpose
Universal Linter Auto-Fix Setup is a portable, plug-and-play linting and formatting toolkit for modern Node.js and web projects. It provides opinionated, auto-fixing code quality tools that work on every save and commit, ensuring consistent code style across teams without manual intervention.

### Key Features
- **Zero Configuration** - Drop in and run `npm install` to get started
- **Auto-Fix Everything** - Linting and formatting happen automatically on save and commit
- **Multi-Language Support** - JavaScript, TypeScript, CSS, SCSS, JSON, YAML, Markdown, HTML, TOML
- **Git Hooks Integration** - Pre-commit hooks ensure only clean code enters the repository
- **Editor Integration** - Works seamlessly with VS Code and other modern editors
- **Modern Standards** - Uses latest versions of ESLint 9, Prettier 3, Stylelint 16

### Author & License
- **Author**: JTGS Systems
- **License**: MIT License (Copyright 2024)
- **Repository**: https://github.com/jtgsystems/universal-linter-auto-fix-setup
- **Type**: Template/Starter Kit

---

## Directory Structure

```
universal-linter-auto-fix-setup/
├── .git/                    # Git repository data
├── .husky/                  # Git hooks directory (Husky)
│   └── pre-commit          # Pre-commit hook script
├── eslint.config.js        # ESLint 9 flat config (JS/TS linting)
├── .prettierrc.json        # Prettier configuration (formatting)
├── .prettierignore         # Files to exclude from Prettier
├── .stylelintrc.json       # Stylelint configuration (CSS/SCSS)
├── .gitignore              # Git exclusions
├── package.json            # npm package configuration & scripts
├── package-lock.json       # Dependency lock file
├── LICENSE                 # MIT License
├── README.md               # User-facing documentation
└── banner.png              # Project banner image (448KB)
```

### Key Files Explained

#### Configuration Files
- **eslint.config.js**: ESLint 9 flat configuration supporting JS/TS with TypeScript parser
- **.prettierrc.json**: Prettier code formatting rules (80 char width, 2 spaces, single quotes)
- **.stylelintrc.json**: Stylelint CSS/SCSS linting with Standard + SCSS presets
- **.prettierignore**: Excludes node_modules, dist, minified files, package-lock.json
- **.gitignore**: Standard Node.js exclusions plus IDE and environment files

#### Git Automation
- **.husky/pre-commit**: Executes `npx lint-staged` on every commit
- **lint-staged configuration**: Lives in package.json, auto-fixes staged files by type

#### Documentation
- **README.md**: Comprehensive user guide with quick start, scripts, customization
- **LICENSE**: MIT License with JTGS Systems copyright

---

## Technology Stack

### Core Dependencies (All DevDependencies)

#### Linting & Formatting
- **ESLint 9.36.0** - JavaScript/TypeScript linting engine
  - `@eslint/js` ^9.36.0 - ESLint recommended JS rules
  - `eslint-config-prettier` ^9.1.2 - Disables conflicting ESLint rules
  - `eslint-plugin-prettier` ^5.5.4 - Runs Prettier as ESLint rule

- **TypeScript Support**
  - `@typescript-eslint/parser` ^8.44.1 - TypeScript parser for ESLint
  - `@typescript-eslint/eslint-plugin` ^8.44.1 - TypeScript-specific linting rules
  - `typescript` ^5.9.2 - TypeScript compiler (peer dependency)

- **Prettier 3.6.2** - Opinionated code formatter
  - `prettier-plugin-packagejson` ^2.5.19 - Formats package.json files

- **Stylelint 16.24.0** - CSS/SCSS linting engine
  - `stylelint-config-standard` ^36.0.1 - Standard CSS rules
  - `stylelint-config-recommended` ^14.0.1 - Recommended rules
  - `stylelint-config-standard-scss` ^13.1.0 - SCSS-specific rules
  - `stylelint-scss` ^6.4.1 - SCSS syntax plugin

#### Git Automation
- **Husky 9.1.6** - Git hooks management
- **lint-staged 15.2.9** - Run linters on staged git files only

#### Utilities
- **globals 15.12.0** - Browser and Node.js global variables for ESLint

### Node.js Requirements
- **Type**: ESM (ES Modules) - `"type": "module"` in package.json
- **Minimum Version**: Node.js 16+ (required by Husky 9.x and ESLint 9.x)

---

## Development Workflow

### Initial Setup

1. **Clone or Copy Template**
   ```bash
   git clone https://github.com/jtgsystems/universal-linter-auto-fix-setup.git my-project
   cd my-project
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```
   - Automatically runs `prepare` script which initializes Husky hooks
   - Installs all linting tools and configures pre-commit hooks

3. **Optional: Format Existing Code**
   ```bash
   npm run format:all
   ```
   - Runs ESLint fix, Stylelint fix, and Prettier on entire codebase

### Integration with Existing Projects

To add this to an existing repository:

1. **Copy Configuration Files**
   - `eslint.config.js`
   - `.prettierrc.json`
   - `.prettierignore`
   - `.stylelintrc.json`
   - `.husky/` directory

2. **Merge package.json Sections**
   - `scripts` - Add linting/formatting scripts
   - `devDependencies` - Add all linting dependencies
   - `lint-staged` - Add the lint-staged configuration block

3. **Run Installation**
   ```bash
   npm install
   ```

### npm Scripts Reference

| Command | Purpose | Auto-Fix | Files Processed |
|---------|---------|----------|-----------------|
| `npm run lint` | Check JS/TS for errors | No | All JS/TS files |
| `npm run lint:fix` | Fix JS/TS errors | Yes | All JS/TS files |
| `npm run stylelint` | Check CSS/SCSS for errors | No | All CSS/SCSS files |
| `npm run stylelint:fix` | Fix CSS/SCSS errors | Yes | All CSS/SCSS files |
| `npm run format` | Format all supported files | Yes | All (see Prettier config) |
| `npm run format:check` | Check formatting (CI mode) | No | All (see Prettier config) |
| `npm run format:all` | Run all fixes in sequence | Yes | All files |
| `npm run prepare` | Initialize Husky (auto-run) | N/A | Git hooks setup |

### Git Commit Workflow

**Automatic Linting on Commit:**

1. Developer stages files: `git add .`
2. Developer commits: `git commit -m "message"`
3. **Husky pre-commit hook triggers** `.husky/pre-commit`
4. **lint-staged runs** on staged files only:
   - `*.{js,jsx,ts,tsx}` → ESLint --fix
   - `*.{css,scss}` → Stylelint --fix
   - `*.{js,jsx,ts,tsx,css,scss,json,yaml,yml,html,md}` → Prettier --write
5. If fixes applied, files are re-staged automatically
6. If linting errors remain, commit is aborted
7. Commit proceeds only if all checks pass

**Benefits:**
- Only modified files are processed (fast)
- Impossible to commit code with linting errors
- Team maintains consistent style without manual effort

---

## Configuration Details

### ESLint Configuration (eslint.config.js)

**Type**: ESLint 9 Flat Config (modern format)

**Structure**: Array of configuration objects

#### JavaScript Files (*.js, *.mjs, *.cjs)
- **Parser**: ECMAScript latest
- **Source Type**: Module (ESM)
- **Globals**: Browser + Node.js combined
- **Plugins**: Prettier integration
- **Rules**: ESLint recommended + Prettier errors

#### TypeScript Files (*.ts, *.tsx)
- **Parser**: @typescript-eslint/parser
- **Source Type**: Module (ESM)
- **Globals**: Browser + Node.js combined
- **Plugins**: TypeScript ESLint + Prettier
- **Rules**: TypeScript recommended + Prettier errors

#### Ignored Patterns
- `node_modules/**`
- `dist/**`
- `*.min.js`

**Key Features:**
- Prettier formatting enforced as ESLint errors
- Supports both browser and Node.js environments
- Type-aware rules available (requires tsconfig.json)

### Prettier Configuration (.prettierrc.json)

**Core Settings:**
- **Line Width**: 80 characters (default)
- **Indentation**: 2 spaces
- **Quotes**: Single quotes (singleQuote: true)
- **Semicolons**: Required (semi: true)
- **Trailing Commas**: ES5 compatible
- **Bracket Spacing**: Enabled
- **Arrow Function Parens**: Avoid when possible

**File-Specific Overrides:**
- **JSON Files**: 100 character line width (easier reading)
- **YAML Files**: 2 spaces, 80 character width (strict)

**Supported File Types:**
JavaScript, TypeScript, JSX, TSX, CSS, SCSS, JSON, YAML, Markdown, HTML, TOML

### Stylelint Configuration (.stylelintrc.json)

**Extended Configs:**
- `stylelint-config-standard` - Standard CSS rules
- `stylelint-config-standard-scss` - SCSS-specific standards
- `stylelint-config-recommended` - Recommended best practices

**Plugins:**
- `stylelint-scss` - SCSS syntax support

**Custom Rules:**
- `scss/at-rule-no-unknown`: Disallow unknown SCSS at-rules
- `scss/dollar-variable-pattern`: Variable naming (camelCase)
- `scss/selector-no-redundant-nesting-selector`: Prevent unnecessary nesting

**Ignored Patterns:**
- `node_modules/**/*`
- `dist/**/*`

### lint-staged Configuration (package.json)

**File Type Handlers:**

```json
{
  "*.{js,jsx,ts,tsx}": "eslint --fix",
  "*.{css,scss}": "stylelint --fix",
  "*.{js,jsx,ts,tsx,css,scss,json,yaml,yml,html,md}": "prettier --write"
}
```

**Execution Order:**
1. ESLint runs first on JS/TS files
2. Stylelint runs on CSS/SCSS files
3. Prettier runs last on all supported files (ensures final formatting)

**Performance:**
- Only processes staged files (fast commits)
- Runs in parallel where possible
- Auto-stages fixed files

---

## Editor Integration

### VS Code Configuration

**Recommended .vscode/settings.json:**

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

**Required Extensions:**
- **ESLint** (dbaeumer.vscode-eslint) - JavaScript/TypeScript linting
- **Prettier** (esbenp.prettier-vscode) - Code formatting
- **Stylelint** (stylelint.vscode-stylelint) - CSS/SCSS linting

**Behavior with This Config:**
1. On save, Prettier formats the file
2. ESLint auto-fixes issues
3. Stylelint auto-fixes CSS/SCSS issues
4. Developer sees immediate feedback in editor
5. Pre-commit hook acts as safety net

### Other Editors

**JetBrains IDEs (WebStorm, IntelliJ):**
- Enable ESLint in Settings → Languages & Frameworks → JavaScript → Code Quality Tools
- Enable Prettier in Settings → Languages & Frameworks → JavaScript → Prettier
- Enable "On Save" actions for auto-fix

**Vim/Neovim:**
- Use ALE, CoC, or native LSP with ESLint/Prettier integrations
- Configure auto-fix on save via editor config

---

## Customization Guide

### Adding Framework-Specific Rules

#### React
```bash
npm install --save-dev eslint-plugin-react eslint-plugin-react-hooks
```

Update `eslint.config.js`:
```javascript
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';

// Add to config array
{
  plugins: {
    react: reactPlugin,
    'react-hooks': reactHooksPlugin,
  },
  rules: {
    ...reactPlugin.configs.recommended.rules,
    ...reactHooksPlugin.configs.recommended.rules,
  },
}
```

#### Next.js
```bash
npm install --save-dev @next/eslint-plugin-next
```

#### Vue.js
```bash
npm install --save-dev eslint-plugin-vue
```

### Modifying Code Style

#### Change Line Width
Edit `.prettierrc.json`:
```json
{
  "printWidth": 120  // Change from 80 to 120
}
```

#### Use Tabs Instead of Spaces
Edit `.prettierrc.json`:
```json
{
  "useTabs": true,
  "tabWidth": 4
}
```

#### Stricter TypeScript Rules
Edit `eslint.config.js` for TS files section:
```javascript
rules: {
  ...tsPlugin.configs.strict.rules,  // Use strict instead of recommended
  '@typescript-eslint/no-explicit-any': 'error',
}
```

### Adding CSS Rule Ordering
```bash
npm install --save-dev stylelint-order
```

Update `.stylelintrc.json`:
```json
{
  "plugins": ["stylelint-scss", "stylelint-order"],
  "rules": {
    "order/properties-alphabetical-order": true
  }
}
```

---

## Testing Approach

### No Built-in Tests
This is a configuration template, not an application, so it doesn't include test files or testing frameworks.

### Validation Methods

#### Manual Testing
1. **Create Test Files**
   ```bash
   echo "const x=1" > test.js
   echo "body{color:red}" > test.css
   ```

2. **Run Linters**
   ```bash
   npm run lint
   npm run stylelint
   npm run format:check
   ```

3. **Verify Auto-Fix**
   ```bash
   npm run format:all
   cat test.js  # Should see "const x = 1;"
   ```

#### Git Hook Testing
1. **Stage Intentionally Broken File**
   ```bash
   echo "const x=1;const y=2" > broken.js
   git add broken.js
   ```

2. **Attempt Commit**
   ```bash
   git commit -m "test"
   ```

3. **Expected Result**
   - lint-staged runs
   - ESLint fixes formatting
   - Prettier formats file
   - File re-staged with fixes
   - Commit proceeds

#### CI/CD Integration Testing
```yaml
# Example GitHub Actions workflow
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run stylelint
      - run: npm run format:check
```

---

## Performance Considerations

### Optimization Strategies

#### 1. Staged Files Only (lint-staged)
- **Impact**: 10-100x faster than linting entire codebase
- **Reason**: Only processes files in git staging area
- **Typical Commit**: 3-5 files (seconds) vs entire project (minutes)

#### 2. Parallel Processing
- **ESLint**: Multi-core processing enabled by default
- **Prettier**: Runs concurrently on different file types
- **lint-staged**: Processes file types in parallel

#### 3. Caching
- **ESLint**: Uses `.eslintcache` (add to .gitignore if needed)
- **Stylelint**: Built-in cache for repeated runs
- **Prettier**: Fast by design, no caching needed

#### 4. Ignored Patterns
- `node_modules/` - Never lint dependencies
- `dist/` - Skip build output
- `*.min.js` - Skip minified files
- `package-lock.json` - Binary format, skip formatting

### Large Project Considerations

#### For 1000+ Files
```bash
# Run format:all in CI only, not locally
npm run format:check  # Local - fast check only
npm run format:all    # CI - one-time full format
```

#### For Monorepos
- Consider workspace-specific linting scripts
- Use `lerna run lint` or `nx run-many --target=lint`
- Adjust lint-staged to respect workspace boundaries

#### For Legacy Codebases
- Gradually enable rules via `.eslintrc.override.js`
- Use `eslint-disable-next-line` for technical debt
- Create migration plan to full compliance

---

## Troubleshooting

### Common Issues & Solutions

#### 1. Husky Hook Not Firing

**Symptoms**: Commits succeed without linting

**Causes & Fixes:**
- **`npm install` didn't run**: Delete `node_modules/`, run `npm install` again
- **Hook not executable**: `chmod +x .husky/pre-commit`
- **Git hooks disabled**: `git config core.hooksPath .husky`
- **Inside subdirectory**: Husky must be installed at repo root

**Verification:**
```bash
ls -la .husky/pre-commit  # Should show executable bit (-rwxr-xr-x)
git config core.hooksPath  # Should show .husky
```

#### 2. ESLint Parser Errors (TypeScript)

**Symptoms**: "Parsing error: Cannot find module 'tsconfig.json'"

**Cause**: TypeScript parser needs tsconfig.json for type-aware rules

**Fix Option 1 - Create Basic tsconfig.json:**
```bash
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules", "dist"]
}
EOF
```

**Fix Option 2 - Disable Type-Aware Rules:**
Remove `parserOptions.project` from TypeScript config (already done in this setup)

#### 3. Prettier Conflicts with ESLint

**Symptoms**: ESLint and Prettier fight over formatting

**Cause**: ESLint formatting rules override Prettier

**Fix**: This setup already includes `eslint-config-prettier` which disables conflicting rules. If still seeing issues:

```bash
npm install --save-dev eslint-config-prettier
```

Ensure `eslint-plugin-prettier` is loaded LAST in plugins array.

#### 4. Stylelint Not Finding Files

**Symptoms**: "No files matching the pattern were found"

**Cause**: No CSS/SCSS files in project

**Fix**: This is expected behavior if you only have JS/TS files. The `--allow-empty-input` flag prevents errors. Remove CSS linting if not needed:

```bash
# Remove from package.json scripts
"stylelint": "...",  # DELETE
"stylelint:fix": "...",  # DELETE
```

Update `lint-staged` to remove CSS patterns.

#### 5. Git Hooks Fail on Windows

**Symptoms**: Pre-commit hook fails with "command not found: npx"

**Cause**: Windows line endings (CRLF) in `.husky/pre-commit`

**Fix:**
```bash
# Convert to LF line endings
dos2unix .husky/pre-commit

# Or use Git to normalize
git config core.autocrlf input
git rm --cached -r .
git reset --hard
```

#### 6. Slow Commits

**Symptoms**: Pre-commit hook takes >10 seconds

**Causes & Fixes:**
- **Too many staged files**: Commit smaller changesets
- **First run**: ESLint/Prettier cache not built yet (subsequent runs faster)
- **Large files**: Add to `.prettierignore` if not needed
- **Network issues**: Ensure no network calls in linting

**Optimization:**
```bash
# Skip hooks temporarily (NOT RECOMMENDED for regular use)
git commit --no-verify -m "emergency fix"
```

#### 7. False Positives in Linting

**Symptoms**: ESLint/Stylelint reports errors on valid code

**Fix - Disable Specific Rules:**

ESLint inline:
```javascript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const data: any = fetchData();
```

Stylelint inline:
```css
/* stylelint-disable-next-line scss/dollar-variable-pattern */
$My-Variable: red;
```

Or disable rule globally in config files.

#### 8. Prettier Not Formatting Certain Files

**Symptoms**: Markdown/YAML files not formatted

**Cause**: Files in `.prettierignore` or unsupported file type

**Fix:**
1. Check `.prettierignore` - remove entry if needed
2. Verify file extension matches lint-staged patterns
3. Ensure Prettier supports the file type (check docs)

---

## Known Issues

### Current Limitations

1. **No TypeScript Compilation**
   - This setup lints TypeScript but doesn't compile it
   - Add `tsc --noEmit` to scripts if type-checking needed

2. **No Test File Linting**
   - Template doesn't include Jest/Vitest/Mocha configurations
   - Add test framework plugins manually if needed

3. **No Import Sorting**
   - ESLint/Prettier don't sort imports by default
   - Consider adding `eslint-plugin-import` or `prettier-plugin-organize-imports`

4. **No CSS Autoprefixer**
   - Stylelint doesn't add vendor prefixes
   - Use PostCSS with autoprefixer in build process

5. **Limited SCSS Validation**
   - Only syntax and style rules, no Sass compilation errors
   - Use `sass --no-emit` for compilation checks

### Compatibility Notes

- **Node.js**: Requires Node 16+ (Husky 9.x requirement)
- **Windows**: Git Bash or WSL recommended for hooks
- **Git**: Requires Git 2.9+ for core.hooksPath
- **npm**: Works with npm 7+, Yarn 2+, pnpm 7+

---

## Roadmap & Next Steps

### Immediate Enhancements (Future Versions)

1. **Framework Presets**
   - React preset with Hooks rules
   - Next.js preset with App Router support
   - Vue 3 Composition API preset
   - Svelte preset

2. **Testing Integration**
   - Jest + Testing Library configs
   - Vitest preset for modern projects
   - Playwright/Cypress E2E linting

3. **Advanced TypeScript**
   - Strict mode preset
   - Type-aware rules enabled by default
   - Path alias resolution

4. **Import Management**
   - Auto-sort imports by category
   - Enforce import order (external → internal → relative)
   - Remove unused imports

5. **CSS Enhancements**
   - CSS Modules support
   - Tailwind CSS compatibility
   - Property ordering presets

### Integration Ideas

1. **CI/CD Templates**
   - GitHub Actions workflow example
   - GitLab CI template
   - CircleCI config

2. **Pre-Push Hooks**
   - Run full test suite before push
   - Prevent pushing to main/master
   - Enforce branch naming conventions

3. **Commit Message Linting**
   - Add Commitlint for conventional commits
   - Enforce semantic versioning messages
   - Block commits without issue references

4. **Documentation**
   - JSDoc/TSDoc linting
   - Enforce comment coverage
   - Generate docs from comments

### Community Contributions Welcome

- Additional language support (Go, Rust configs via similar tools)
- Editor integration examples (Sublime, Atom)
- Docker integration for containerized development
- Custom rule presets for specific industries

---

## Quick Reference

### Essential Commands
```bash
npm install                  # Initial setup
npm run format:all           # Fix everything once
npm run lint:fix             # Fix JS/TS only
npm run stylelint:fix        # Fix CSS/SCSS only
git commit -m "message"      # Auto-lints on commit
```

### File Locations
- ESLint config: `eslint.config.js`
- Prettier config: `.prettierrc.json`
- Stylelint config: `.stylelintrc.json`
- Git hooks: `.husky/pre-commit`
- Package scripts: `package.json`

### Support & Resources
- **Repository**: https://github.com/jtgsystems/universal-linter-auto-fix-setup
- **Issues**: https://github.com/jtgsystems/universal-linter-auto-fix-setup/issues
- **Discussions**: GitHub Discussions (enable in repo settings)

### Keywords for Search
eslint, stylelint, prettier, husky, lint-staged, autofix, nodejs, javascript, typescript, css, scss, formatting, quality, automation, hooks, git, precommit, vscode, tooling, workflow, productivity, codestyle, standards, configuration, templates, setup, boilerplate

---

**Last Updated**: 2024-10-26
**Version**: 1.0.0
**Maintained By**: JTGS Systems

## Framework Versions

- **TypeScript**: ^5.9.2

