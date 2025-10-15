# Parade

A domain-driven project planning tool built with modern Python development practices.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

1. **Install uv** (if not already installed):

   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Or via Homebrew (macOS)
   brew install uv
   ```

2. **Clone and setup the project**:

   ```bash
   git clone <repository-url>
   cd parade
   uv sync --extra dev
   ```

   This will:
   - Create a virtual environment with Python 3.13
   - Install all dependencies including development tools
   - Set up the project for development

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run tests with detailed coverage report
uv run pytest --cov=. --cov-report=term-missing

# Run tests with HTML coverage report
uv run pytest --cov=. --cov-report=html
```

The project maintains **90% test coverage** requirement.

### Code Quality

This project uses strict code quality standards:

```bash
# Type checking with MyPy
uv run mypy .

# Linting and formatting with Ruff
uv run ruff check .
uv run ruff format .

# Run all quality checks
uv run pre-commit run --all-files
```

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit to ensure code quality:

1. **Install pre-commit hooks**:

   ```bash
   uv run pre-commit install
   ```

2. **What the hooks check**:
   - **Ruff**: Comprehensive linting and formatting
   - **MyPy**: Strict type checking
   - **Pytest**: All tests must pass
   - **YAML**: Linting for configuration files
   - **Coverage**: Maintains 90% test coverage
   - **Code Standards**: No `# noqa` or `# type-ignore` comments allowed

3. **Run hooks manually**:

   ```bash
   # Run on all files
   uv run pre-commit run --all-files

   # Run on staged files only
   uv run pre-commit run
   ```

### Project Structure

```text
parade/
├── parade/           # Main package
│   └── __init__.py
├── tests/            # Test suite
│   ├── __init__.py
│   └── test_*.py
├── pyproject.toml    # Project configuration
├── uv.lock          # Dependency lockfile
└── README.md         # This file
```

## Code Quality Standards

- **Type Safety**: Strict MyPy configuration with no untyped code
- **Test Coverage**: Minimum 90% coverage required
- **Linting**: Comprehensive Ruff rules with minimal exceptions
- **Documentation**: Google-style docstrings required
- **Formatting**: Automated with Ruff formatter

## Development Workflow

1. **Make your changes**
2. **Run tests**: `uv run pytest`
3. **Check types**: `uv run mypy .`
4. **Format code**: `uv run ruff format .`
5. **Commit**: Pre-commit hooks will run automatically
6. **Push**: All checks must pass

## Adding Dependencies

```bash
# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update all dependencies
uv sync
```

## Contributing

1. Ensure all tests pass: `uv run pytest`
2. Ensure type checking passes: `uv run mypy .`
3. Ensure pre-commit hooks pass: `uv run pre-commit run --all-files`
4. Maintain or improve test coverage (90% minimum)

## License

TBD
