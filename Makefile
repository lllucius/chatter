# Makefile for Chatter project linting and quality checks
.PHONY: help install lint lint-backend lint-frontend fix format test security audit clean

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)Chatter Project - Code Quality Commands$(NC)"
	@echo "$(CYAN)=====================================$(NC)"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  $(YELLOW)make install$(NC)      # Install all dependencies"
	@echo "  $(YELLOW)make lint$(NC)         # Run all linting checks"
	@echo "  $(YELLOW)make fix$(NC)          # Fix all auto-fixable issues"
	@echo "  $(YELLOW)make security$(NC)     # Run security analysis only"

install: ## Install all dependencies (backend and frontend)
	@echo "$(CYAN)Installing backend dependencies...$(NC)"
	pip install -e ".[dev]"
	@echo "$(CYAN)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✅ All dependencies installed!$(NC)"

install-hooks: ## Install pre-commit hooks
	@echo "$(CYAN)Installing pre-commit hooks...$(NC)"
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✅ Pre-commit hooks installed!$(NC)"

lint: ## Run all linting and static analysis checks
	@echo "$(CYAN)Running all linting checks...$(NC)"
	bash scripts/lint_all.sh

lint-backend: ## Run backend Python linting only
	@echo "$(CYAN)Running backend linting...$(NC)"
	python scripts/lint_backend.py

lint-frontend: ## Run frontend TypeScript/React linting only
	@echo "$(CYAN)Running frontend linting...$(NC)"
	bash scripts/lint_frontend.sh

fix: ## Automatically fix all auto-fixable issues
	@echo "$(CYAN)Fixing all auto-fixable issues...$(NC)"
	bash scripts/lint_all.sh --fix

fix-backend: ## Fix backend issues only
	@echo "$(CYAN)Fixing backend issues...$(NC)"
	python scripts/lint_backend.py --fix

fix-frontend: ## Fix frontend issues only
	@echo "$(CYAN)Fixing frontend issues...$(NC)"
	bash scripts/lint_frontend.sh --fix

format: ## Format all code (backend and frontend)
	@echo "$(CYAN)Formatting all code...$(NC)"
	black chatter tests scripts
	isort chatter tests scripts
	cd frontend && npm run format

security: ## Run security analysis only (backend)
	@echo "$(CYAN)Running security analysis...$(NC)"
	bash scripts/lint_all.sh --security-only

test-backend: ## Run backend tests
	@echo "$(CYAN)Running backend tests...$(NC)"
	pytest

test-frontend: ## Run frontend tests  
	@echo "$(CYAN)Running frontend tests...$(NC)"
	cd frontend && npm test

test: ## Run all tests (backend and frontend)
	@echo "$(CYAN)Running all tests...$(NC)"
	$(MAKE) test-backend
	$(MAKE) test-frontend

audit: ## Run dependency vulnerability audits
	@echo "$(CYAN)Running dependency audits...$(NC)"
	@echo "$(YELLOW)Backend (Python):$(NC)"
	safety scan || true
	@echo "$(YELLOW)Frontend (Node.js):$(NC)"
	cd frontend && npm audit || true

clean: ## Clean build artifacts and caches
	@echo "$(CYAN)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf dist/ 2>/dev/null || true
	rm -rf build/ 2>/dev/null || true
	rm -rf *.egg-info/ 2>/dev/null || true
	cd frontend && rm -rf dist/ build/ node_modules/.cache/ 2>/dev/null || true
	@echo "$(GREEN)✅ Cleaned up build artifacts!$(NC)"

ci: ## Run CI-like checks locally
	@echo "$(CYAN)Running CI-like checks...$(NC)"
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security
	@echo "$(GREEN)✅ All CI checks completed!$(NC)"

quick-check: ## Quick syntax and basic checks
	@echo "$(CYAN)Running quick checks...$(NC)"
	ruff check chatter --select=E,W,F
	cd frontend && npm run type-check
	@echo "$(GREEN)✅ Quick checks completed!$(NC)"

# Development workflow helpers
dev-setup: install install-hooks ## Complete development setup
	@echo "$(GREEN)🚀 Development environment ready!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  $(YELLOW)make lint$(NC)         # Check code quality"
	@echo "  $(YELLOW)make test$(NC)         # Run tests"
	@echo "  $(YELLOW)make fix$(NC)          # Fix issues"

check-syntax: ## Check syntax only (fast)
	@echo "$(CYAN)Checking syntax...$(NC)"
	python -m py_compile chatter/**/*.py
	cd frontend && npx tsc --noEmit --pretty false
	@echo "$(GREEN)✅ Syntax check passed!$(NC)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(CYAN)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

stats: ## Show code statistics
	@echo "$(CYAN)Code Statistics$(NC)"
	@echo "$(CYAN)===============$(NC)"
	@echo ""
	@echo "$(YELLOW)Backend (Python):$(NC)"
	@find chatter -name "*.py" | wc -l | awk '{print "  Files: " $$1}'
	@find chatter -name "*.py" -exec cat {} \; | wc -l | awk '{print "  Lines: " $$1}'
	@echo ""
	@echo "$(YELLOW)Frontend (TypeScript/React):$(NC)"
	@find frontend/src -name "*.ts" -o -name "*.tsx" | wc -l | awk '{print "  Files: " $$1}'
	@find frontend/src -name "*.ts" -o -name "*.tsx" -exec cat {} \; | wc -l | awk '{print "  Lines: " $$1}'
	@echo ""
	@echo "$(YELLOW)Tests:$(NC)"
	@find tests -name "*.py" 2>/dev/null | wc -l | awk '{print "  Backend test files: " $$1}' || echo "  Backend test files: 0"
	@find frontend/src -name "*.test.*" -o -name "*.spec.*" | wc -l | awk '{print "  Frontend test files: " $$1}'