#!/usr/bin/env bash
"""Frontend code quality script."""

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(cd "${SCRIPT_DIR}/../frontend" && pwd)"

cd "$FRONTEND_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
FIX=false
LINT_ONLY=false
FORMAT_ONLY=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX=true
            shift
            ;;
        --lint-only)
            LINT_ONLY=true
            shift
            ;;
        --format-only)
            FORMAT_ONLY=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --fix          Automatically fix issues where possible"
            echo "  --lint-only    Run only linting checks"
            echo "  --format-only  Run only formatting checks"
            echo "  --verbose, -v  Verbose output"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Print step header
print_step() {
    echo -e "\n${BLUE}🔍 $1${NC}"
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${YELLOW}Running: $2${NC}"
    fi
}

# Run command and check result
run_check() {
    local description="$1"
    shift
    local cmd=("$@")
    
    print_step "$description" "${cmd[*]}"
    
    if "${cmd[@]}"; then
        echo -e "${GREEN}✅ $description passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $description failed${NC}"
        return 1
    fi
}

# Initialize success flag
SUCCESS=true

echo "Working directory: $FRONTEND_DIR"

if [[ "$FORMAT_ONLY" != "true" ]]; then
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}🛠️  LINTING CHECKS${NC}"
    echo -e "${BLUE}================================${NC}"
    
    # TypeScript type checking
    if ! run_check "TypeScript type checking" npm run type-check; then
        SUCCESS=false
    fi
    
    # ESLint
    if [[ "$FIX" == "true" ]]; then
        if ! run_check "ESLint (with fixes)" npm run lint:fix; then
            SUCCESS=false
        fi
    else
        if ! run_check "ESLint" npm run lint:check; then
            SUCCESS=false
        fi
    fi
fi

if [[ "$LINT_ONLY" != "true" ]]; then
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}✨ CODE FORMATTING${NC}"
    echo -e "${BLUE}================================${NC}"
    
    # Prettier
    if [[ "$FIX" == "true" ]]; then
        if ! run_check "Prettier formatting (with fixes)" npm run format; then
            SUCCESS=false
        fi
    else
        if ! run_check "Prettier formatting check" npm run format:check; then
            SUCCESS=false
        fi
    fi
fi

echo -e "\n${BLUE}================================${NC}"
if [[ "$SUCCESS" == "true" ]]; then
    echo -e "${GREEN}✅ All frontend checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some frontend checks failed!${NC}"
    exit 1
fi