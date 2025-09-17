#!/usr/bin/env bash
"""Quick health check for code quality - runs essential checks fast."""

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}⚡ Quick Code Health Check${NC}"
echo -e "${PURPLE}=========================${NC}"

# Track overall success
SUCCESS=true

# Quick syntax checks
echo -e "\n${BLUE}🔍 Syntax Checks${NC}"
echo "Checking Python syntax..."
if python -m compileall chatter -q; then
    echo -e "${GREEN}✅ Python syntax OK${NC}"
else
    echo -e "${RED}❌ Python syntax errors${NC}"
    SUCCESS=false
fi

echo "Checking TypeScript syntax..."
if cd frontend && npx tsc --noEmit --pretty false > /dev/null 2>&1; then
    echo -e "${GREEN}✅ TypeScript syntax OK${NC}"
    cd ..
else
    echo -e "${RED}❌ TypeScript syntax errors${NC}"
    cd ..
    SUCCESS=false
fi

# Quick linting (fast rules only)
echo -e "\n${BLUE}⚡ Fast Linting${NC}"
echo "Running Ruff (syntax and imports only)..."
if ruff check chatter --select=E,W,F,I --quiet --no-fix; then
    echo -e "${GREEN}✅ Basic Python linting OK${NC}"
else
    echo -e "${YELLOW}⚠️  Python linting issues found (run 'make lint-backend' for details)${NC}"
fi

echo "Checking import formatting..."
if isort --check-only chatter --quiet; then
    echo -e "${GREEN}✅ Import sorting OK${NC}"
else
    echo -e "${YELLOW}⚠️  Import sorting issues (run 'make fix' to resolve)${NC}"
fi

# Security quick scan (high severity only)
echo -e "\n${BLUE}🔒 Security Quick Scan${NC}"
echo "Checking for obvious security issues..."
if bandit -r chatter --severity-level high --quiet --format=custom --msg-template="{abspath}:{line}: {severity}: {msg}" 2>/dev/null | head -5; then
    echo -e "${GREEN}✅ No high-severity security issues found${NC}"
else
    echo -e "${YELLOW}⚠️  Security issues detected (run 'make security' for full report)${NC}"
fi

# Git status
echo -e "\n${BLUE}📁 Git Status${NC}"
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${YELLOW}📝 Uncommitted changes detected${NC}"
    echo "Modified files:"
    git status --porcelain | head -10
    if [[ $(git status --porcelain | wc -l) -gt 10 ]]; then
        echo "... and $(( $(git status --porcelain | wc -l) - 10 )) more files"
    fi
else
    echo -e "${GREEN}✅ Working directory clean${NC}"
fi

# Dependencies check
echo -e "\n${BLUE}📦 Dependencies${NC}"
echo "Checking for critical dependency vulnerabilities..."

# Backend - only check for critical/high
if safety scan --short-report --severity high 2>/dev/null | grep -q "No vulnerabilities found"; then
    echo -e "${GREEN}✅ No critical Python dependency vulnerabilities${NC}"
else
    echo -e "${YELLOW}⚠️  Dependency vulnerabilities found (run 'make audit' for details)${NC}"
fi

# Frontend - quick audit
if cd frontend && npm audit --audit-level high --dry-run > /dev/null 2>&1; then
    echo -e "${GREEN}✅ No critical Node.js dependency vulnerabilities${NC}"
    cd ..
else
    echo -e "${YELLOW}⚠️  Node.js dependency vulnerabilities found (run 'cd frontend && npm audit' for details)${NC}"
    cd ..
fi

# Summary
echo -e "\n${PURPLE}=========================${NC}"
if [[ "$SUCCESS" == "true" ]]; then
    echo -e "${GREEN}🎉 Quick health check passed!${NC}"
    echo -e "${GREEN}Your code is in good shape for development.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  • Run ${YELLOW}make lint${NC} for comprehensive analysis"
    echo -e "  • Run ${YELLOW}make test${NC} to execute test suite"
    echo -e "  • Run ${YELLOW}make fix${NC} to auto-resolve issues"
else
    echo -e "${RED}⚠️  Issues detected in health check${NC}"
    echo -e "${YELLOW}Run the following for detailed analysis:${NC}"
    echo -e "  • ${YELLOW}make lint${NC} - Full linting analysis"
    echo -e "  • ${YELLOW}make security${NC} - Security analysis"
    echo -e "  • ${YELLOW}make audit${NC} - Dependency audit"
    echo -e "  • ${YELLOW}make fix${NC} - Auto-fix issues"
    exit 1
fi