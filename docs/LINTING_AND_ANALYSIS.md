# Code Quality and Static Analysis Guide

This document describes the comprehensive linting and static analysis tools available in the Chatter project.

## Quick Start

### Installation
```bash
# Install all dependencies and set up development environment
make dev-setup

# Or install manually
pip install -e ".[dev]"
cd frontend && npm install
```

### Running All Checks
```bash
# Run all linting and analysis tools
make lint

# Run all checks and automatically fix issues
make fix

# Run security analysis only
make security
```

## Available Tools

### Backend (Python)

#### 1. **Ruff** - Fast Python Linter
- **Purpose**: Code style, import sorting, common bugs
- **Config**: `pyproject.toml` (`[tool.ruff]`)
- **Usage**:
  ```bash
  ruff check chatter                # Check only
  ruff check chatter --fix          # Fix auto-fixable issues
  ```

#### 2. **Black** - Code Formatter
- **Purpose**: Consistent code formatting
- **Config**: `pyproject.toml` (`[tool.black]`)
- **Usage**:
  ```bash
  black --check chatter             # Check formatting
  black chatter                     # Format code
  ```

#### 3. **isort** - Import Sorting
- **Purpose**: Organize and sort import statements
- **Config**: `pyproject.toml` (`[tool.isort]`)
- **Usage**:
  ```bash
  isort --check-only chatter         # Check import order
  isort chatter                      # Sort imports
  ```

#### 4. **MyPy** - Static Type Checking
- **Purpose**: Type checking and inference
- **Config**: `pyproject.toml` (`[tool.mypy]`)
- **Usage**:
  ```bash
  mypy chatter                      # Type check
  ```

#### 5. **Bandit** - Security Analysis
- **Purpose**: Security vulnerability detection
- **Config**: `pyproject.toml` (`[tool.bandit]`)
- **Usage**:
  ```bash
  bandit -r chatter                 # Security scan
  bandit -r chatter -f json -o bandit-report.json  # JSON report
  ```

#### 6. **Safety** - Dependency Vulnerability Scanner
- **Purpose**: Check for known security vulnerabilities in dependencies
- **Usage**:
  ```bash
  safety scan                       # Check dependencies
  safety scan --json --save-json safety-report.json  # JSON report
  ```

### Frontend (TypeScript/React)

#### 1. **ESLint** - JavaScript/TypeScript Linter
- **Purpose**: Code quality, best practices, React-specific rules
- **Config**: `frontend/eslint.config.js`
- **Usage**:
  ```bash
  cd frontend
  npm run lint                      # Check issues
  npm run lint:fix                  # Fix auto-fixable issues
  npm run lint:check               # Check with zero warnings tolerance
  ```

#### 2. **Prettier** - Code Formatter
- **Purpose**: Consistent code formatting
- **Config**: `frontend/.prettierrc.json`
- **Usage**:
  ```bash
  cd frontend
  npm run format:check              # Check formatting
  npm run format                    # Format code
  ```

#### 3. **TypeScript** - Type Checking
- **Purpose**: Static type checking
- **Config**: `frontend/tsconfig.json`
- **Usage**:
  ```bash
  cd frontend
  npm run type-check                # Type check
  ```

## Scripts and Automation

### Custom Scripts

#### 1. **Backend Script** (`scripts/lint_backend.py`)
```bash
python scripts/lint_backend.py                    # Run all backend checks
python scripts/lint_backend.py --fix              # Auto-fix issues
python scripts/lint_backend.py --security-only    # Security checks only
python scripts/lint_backend.py --verbose          # Verbose output
```

#### 2. **Frontend Script** (`scripts/lint_frontend.sh`)
```bash
bash scripts/lint_frontend.sh                     # Run all frontend checks
bash scripts/lint_frontend.sh --fix               # Auto-fix issues
bash scripts/lint_frontend.sh --lint-only         # Linting only
bash scripts/lint_frontend.sh --format-only       # Formatting only
```

#### 3. **Unified Script** (`scripts/lint_all.sh`)
```bash
bash scripts/lint_all.sh                          # Run everything
bash scripts/lint_all.sh --fix                    # Auto-fix everything
bash scripts/lint_all.sh --backend-only           # Backend only
bash scripts/lint_all.sh --frontend-only          # Frontend only
bash scripts/lint_all.sh --security-only          # Security only
```

### Makefile Commands

The project includes a comprehensive Makefile for easy access:

```bash
make help                          # Show all available commands
make lint                          # Run all linting checks
make fix                           # Fix all auto-fixable issues
make security                      # Run security analysis
make test                          # Run all tests
make audit                         # Dependency vulnerability audit
make ci                            # Run CI-like checks locally
make clean                         # Clean build artifacts
```

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

### Setup
```bash
pip install pre-commit
pre-commit install                 # Install git hooks
pre-commit install --hook-type commit-msg  # Install commit message hooks
```

### Manual Execution
```bash
pre-commit run --all-files         # Run on all files
pre-commit run --files file1.py file2.tsx  # Run on specific files
```

### Configured Hooks
- **Backend**: Black, isort, Ruff, MyPy, Bandit
- **Frontend**: ESLint, Prettier
- **General**: Trailing whitespace, end-of-file-fixer, YAML/JSON validation
- **Security**: Secret detection, private key detection

## CI/CD Integration

### GitHub Actions

The project includes automated quality checks in `.github/workflows/quality.yml`:

- **Backend Analysis**: Ruff, Black, isort, MyPy, Bandit, Safety
- **Frontend Analysis**: ESLint, Prettier, TypeScript, npm audit
- **Code Coverage**: Test coverage reporting
- **Artifact Upload**: Security reports and coverage data

### Workflow Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual workflow dispatch

## Configuration Files

### Backend Configuration (`pyproject.toml`)
```toml
[tool.ruff]
target-version = "py312"
line-length = 72

[tool.black]
line-length = 72
target-version = ["py312"]

[tool.mypy]
python_version = "3.12"
check_untyped_defs = true

[tool.bandit]
exclude_dirs = ["tests", "venv"]
```

### Frontend Configuration

#### ESLint (`frontend/eslint.config.js`)
- TypeScript/React rules
- No explicit `any` enforcement
- React hooks rules
- Import/export validation

#### Prettier (`frontend/.prettierrc.json`)
```json
{
  "printWidth": 80,
  "tabWidth": 2,
  "singleQuote": true,
  "trailingComma": "es5"
}
```

## Development Workflow

### Recommended Daily Workflow

1. **Before Starting Work**:
   ```bash
   make quick-check                # Fast syntax validation
   ```

2. **During Development**:
   ```bash
   make fix                        # Fix issues as you go
   ```

3. **Before Committing**:
   ```bash
   make lint                       # Full quality check
   make test                       # Run tests
   ```

4. **Security Review** (periodic):
   ```bash
   make security                   # Security analysis
   make audit                      # Dependency audit
   ```

### IDE Integration

#### VS Code
Recommended extensions:
- **Python**: Pylance, Black Formatter, isort
- **TypeScript/React**: ESLint, Prettier, TypeScript Importer
- **General**: GitLens, Error Lens

#### Settings
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "typescript.preferences.organizeImports": true,
  "editor.formatOnSave": true
}
```

## Troubleshooting

### Common Issues

#### 1. **Ruff Conflicts with Black**
- Solution: Both tools are configured to work together with matching line lengths

#### 2. **MyPy Import Errors**
- Check `[tool.mypy]` overrides in `pyproject.toml`
- Add missing type stubs: `pip install types-<package>`

#### 3. **ESLint Configuration Errors**
- Ensure all dependencies are installed: `cd frontend && npm install`
- Check `eslint.config.js` for syntax errors

#### 4. **Pre-commit Hook Failures**
- Update hooks: `pre-commit autoupdate`
- Skip problematic hooks temporarily: `git commit --no-verify`

### Performance Tips

#### 1. **Speed up MyPy**
```bash
mypy --install-types                # Install missing type stubs
mypy --cache-dir=.mypy_cache chatter  # Use persistent cache
```

#### 2. **Parallel Execution**
```bash
# Run backend and frontend checks in parallel
make lint-backend & make lint-frontend & wait
```

#### 3. **Incremental Checks**
```bash
# Check only changed files
git diff --name-only | grep '\.py$' | xargs ruff check
```

## Reports and Artifacts

### Security Reports
- **Bandit**: `bandit-report.json` - Security vulnerabilities
- **Safety**: `safety-report.json` - Dependency vulnerabilities

### Coverage Reports
- **Backend**: `htmlcov/` directory - HTML coverage report
- **Frontend**: Coverage integrated with test runners

### Accessing Reports
```bash
# View HTML coverage report
python -m http.server 8000 -d htmlcov/

# Parse JSON security reports
jq '.results[] | select(.issue_severity=="MEDIUM" or .issue_severity=="HIGH")' bandit-report.json
```

## Best Practices

### Code Quality
1. **Fix linting issues immediately** - Don't let them accumulate
2. **Use type hints** - Help MyPy catch issues early
3. **Write descriptive commit messages** - Follow conventional commit format
4. **Review security warnings** - Don't ignore Bandit findings
5. **Keep dependencies updated** - Regular `safety scan` and `npm audit`

### Security
1. **Never commit secrets** - Use environment variables
2. **Review dependency vulnerabilities** - Address high/critical issues quickly
3. **Use `# nosec` sparingly** - Only for false positives with explanations
4. **Regular security audits** - Weekly `make security` runs

### Performance
1. **Cache tool outputs** - Use persistent caches where available
2. **Run checks early** - Use pre-commit hooks
3. **Parallel execution** - Run frontend/backend checks simultaneously
4. **Incremental analysis** - Check only changed files when possible

## Advanced Usage

### Custom Rule Configuration

#### Adding Custom Ruff Rules
```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "RUF"]
ignore = ["E501", "B008"]  # Ignore specific rules
```

#### Custom ESLint Rules
```javascript
// eslint.config.js
rules: {
  '@typescript-eslint/no-explicit-any': 'error',
  'react-hooks/exhaustive-deps': 'warn',
  // Add custom rules here
}
```

### Integration with External Tools

#### SonarQube Integration
```bash
# Generate reports in SonarQube format
ruff check --output-format=json chatter > ruff-report.json
```

#### Code Climate Integration
```yaml
# .codeclimate.yml
engines:
  eslint:
    enabled: true
  bandit:
    enabled: true
```

This comprehensive setup ensures high code quality, security, and maintainability across the entire Chatter project.