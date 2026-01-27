#!/usr/bin/env bash
#
# run-import.sh - Simple wrapper for sdlc-import
# Makes it easier to run from Claude Code or terminal
#
# Usage:
#   ./run-import.sh /path/to/project
#   ./run-import.sh .  # Import current directory
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ANALYZER="${SCRIPT_DIR}/scripts/project_analyzer.py"

# Check if project_analyzer.py exists
if [[ ! -f "$PROJECT_ANALYZER" ]]; then
    echo -e "${RED}Error: project_analyzer.py not found at ${PROJECT_ANALYZER}${NC}"
    exit 1
fi

# Get project path (default to current directory)
PROJECT_PATH="${1:-.}"

# Resolve absolute path
PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"

echo -e "${GREEN}SDLC Import - Reverse Engineering Tool${NC}"
echo -e "Project: ${YELLOW}${PROJECT_PATH}${NC}"
echo ""

# Check if project exists
if [[ ! -d "$PROJECT_PATH" ]]; then
    echo -e "${RED}Error: Project path does not exist: ${PROJECT_PATH}${NC}"
    exit 1
fi

# Run project analyzer
echo -e "${GREEN}Starting analysis...${NC}"
python3 "$PROJECT_ANALYZER" "$PROJECT_PATH" "${@:2}"

exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    echo -e "${GREEN}✅ Import complete!${NC}"
    echo -e "Check: ${YELLOW}${PROJECT_PATH}/.project/${NC}"
else
    echo -e "${RED}❌ Import failed with exit code ${exit_code}${NC}"
fi

exit $exit_code
