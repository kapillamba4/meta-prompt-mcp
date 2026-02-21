.PHONY: install dev lint format test build publish clean run build-index

# --------------------------------------------------------------------------
# Development
# --------------------------------------------------------------------------

install:  ## Install the package
	pip install .

dev:  ## Install in editable mode with dev dependencies
	pip install -e ".[dev]"

lint:  ## Run linter
	ruff check src/

format:  ## Auto-format code
	ruff check --fix src/
	ruff format src/

test:  ## Run tests
	pytest -v

# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------

run:  ## Start the MCP server
	meta-prompt-mcp

build-index:  ## Pre-build the vector index from PDFs in data/
	meta-prompt-mcp-build-index

# --------------------------------------------------------------------------
# Build & Publish
# --------------------------------------------------------------------------

build: clean  ## Build distribution packages
	pip install build
	python -m build

publish: build  ## Publish to PyPI
	pip install twine
	twine upload dist/*

publish-test: build  ## Publish to Test PyPI
	pip install twine
	twine upload --repository testpypi dist/*

# --------------------------------------------------------------------------
# Cleanup
# --------------------------------------------------------------------------

clean:  ## Remove build artifacts
	rm -rf dist/ build/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true

clean-index:  ## Remove the cached vector index (forces rebuild on next run)
	rm -rf storage/

# --------------------------------------------------------------------------
# Help
# --------------------------------------------------------------------------

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
