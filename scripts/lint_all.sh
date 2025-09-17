#!/usr/bin/env bash
"""Unified linting script for the entire project."""

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

# Default values
FIX=false
BACKEND_ONLY=false
FRONTEND_ONLY=false
SECURITY_ONLY=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX=true
            shift
            ;;
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --security-only)
            SECURITY_ONLY=true
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
            echo "  --fix             Automatically fix issues where possible"
            echo "  --backend-only    Run only backend checks"
            echo "  --frontend-only   Run only frontend checks"
            echo "  --security-only   Run only security checks"
            echo "  --verbose, -v     Verbose output"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     # Run all checks"
            echo "  $0 --fix              # Run all checks and fix issues"
            echo "  $0 --backend-only      # Run only backend checks"
            echo "  $0 --security-only     # Run only security analysis"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build script arguments
BACKEND_ARGS=""
FRONTEND_ARGS=""

if [[ "$FIX" == "true" ]]; then
    BACKEND_ARGS="$BACKEND_ARGS --fix"
    FRONTEND_ARGS="$FRONTEND_ARGS --fix"
fi

if [[ "$SECURITY_ONLY" == "true" ]]; then
    BACKEND_ARGS="$BACKEND_ARGS --security-only"
fi

if [[ "$VERBOSE" == "true" ]]; then
    BACKEND_ARGS="$BACKEND_ARGS --verbose"
    FRONTEND_ARGS="$FRONTEND_ARGS --verbose"
fi

SUCCESS=true

echo -e "${PURPLE}🚀 Chatter Project Linting and Analysis${NC}"
echo -e "${PURPLE}======================================${NC}"
echo "Working directory: $PROJECT_ROOT"

# Run backend checks
if [[ "$FRONTEND_ONLY" != "true" ]]; then
    echo -e "\n${BLUE}🐍 BACKEND (Python) ANALYSIS${NC}"
    echo -e "${BLUE}=============================${NC}"
    
    if python scripts/lint_backend.py $BACKEND_ARGS; then
        echo -e "${GREEN}✅ Backend analysis completed successfully${NC}"
    else
        echo -e "${RED}❌ Backend analysis failed${NC}"
        SUCCESS=false
    fi
fi

# Run frontend checks
if [[ "$BACKEND_ONLY" != "true" && "$SECURITY_ONLY" != "true" ]]; then
    echo -e "\n${BLUE}⚛️  FRONTEND (TypeScript/React) ANALYSIS${NC}"
    echo -e "${BLUE}=======================================${NC}"
    
    if bash scripts/lint_frontend.sh $FRONTEND_ARGS; then
        echo -e "${GREEN}✅ Frontend analysis completed successfully${NC}"
    else
        echo -e "${RED}❌ Frontend analysis failed${NC}"
        SUCCESS=false
    fi
fi

# Final summary
echo -e "\n${PURPLE}======================================${NC}"
echo -e "${PURPLE}📊 FINAL SUMMARY${NC}"
echo -e "${PURPLE}======================================${NC}"

if [[ "$SUCCESS" == "true" ]]; then
    echo -e "${GREEN}🎉 All analysis checks passed!${NC}"
    echo -e "${GREEN}Your code quality is excellent!${NC}"
    exit 0
else
    echo -e "${RED}💥 Some analysis checks failed!${NC}"
    echo -e "${YELLOW}💡 Tip: Run with --fix to automatically fix issues${NC}"
    exit 1
fi