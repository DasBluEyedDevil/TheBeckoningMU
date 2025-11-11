#!/bin/bash

# Copilot CLI Wrapper Script - Developer Subagent #2
# This script provides a convenient interface to invoke GitHub Copilot CLI
# for backend/Python/terminal operations

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default settings
MODEL=""
ALLOW_TOOLS=()
DENY_TOOLS=()

# Function to display usage
usage() {
    cat << EOF
${GREEN}Copilot CLI Wrapper - Developer Subagent #2 (Backend/GitHub/Terminal)${NC}

${BLUE}USAGE:${NC}
    $0 [OPTIONS] "<prompt>"

${BLUE}OPTIONS:${NC}
    -m, --model MODEL          Set the model (default: sonnet-4, options: sonnet-4.5)
    --allow-write              Allow file write operations
    --allow-git                Allow git operations (denies force push by default)
    --allow-github             Allow GitHub operations (PRs, issues, etc.)
    --allow-tool PATTERN       Allow specific tool (can be used multiple times)
    --deny-tool PATTERN        Deny specific tool (can be used multiple times)
    -h, --help                 Display this help message

${BLUE}EXAMPLES:${NC}
    ${YELLOW}# Basic implementation task${NC}
    $0 "IMPLEMENTATION TASK: Create command for feeding mechanics..."

    ${YELLOW}# With write permissions${NC}
    $0 --allow-write "Create new world/prototypes file for Disciplines"

    ${YELLOW}# With git operations${NC}
    $0 --allow-git "Commit Blood System changes and push to branch"

    ${YELLOW}# With GitHub operations${NC}
    $0 --allow-github "Create PR for Phase 6 Blood System, link to docs"

    ${YELLOW}# Complex task with multiple permissions${NC}
    $0 --allow-write --allow-git "Implement feature, test with evennia reload, and commit"

${BLUE}ROLE IN QUADRUMVIRATE:${NC}
    Copilot is "Developer #2" - Backend, GitHub, and terminal operations
    - Backend/Python implementation (commands, typeclasses, utilities)
    - GitHub operations (PRs, issues, Actions)
    - Git operations
    - Terminal-based tasks (evennia commands, tests)
    - Cross-checks Cursor's work

${BLUE}TASK TEMPLATE:${NC}
    IMPLEMENTATION TASK:

    **Objective**: [Clear, one-line goal]

    **Requirements**:
    - [Requirement 1]
    - [Requirement 2]

    **Acceptance Criteria**:
    - [Success definition]

    **Context from Gemini**:
    [Paste Gemini's analysis]

    **Files to Modify**:
    - file1.py: [changes needed]

    **TDD Required**: Yes/No

    **After Completion**:
    1. Run tests: evennia test
    2. Report: changes, test results, issues

${BLUE}CROSS-CHECK TEMPLATE:${NC}
    CODE REVIEW TASK:

    Cursor has implemented [feature].

    **Files Changed**: [list]
    **Changes Summary**: [summary]

    **Review For**:
    1. Logic errors
    2. Python best practices
    3. Evennia patterns
    4. Test coverage

    Run tests and report findings.

EOF
    exit 1
}

# Parse arguments
PROMPT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        --allow-write)
            ALLOW_TOOLS+=("read_file")
            ALLOW_TOOLS+=("write_to_file")
            ALLOW_TOOLS+=("file_edit")
            shift
            ;;
        --allow-git)
            ALLOW_TOOLS+=("shell")
            DENY_TOOLS+=("shell(git push --force)")
            shift
            ;;
        --allow-github)
            ALLOW_TOOLS+=("github")
            shift
            ;;
        --allow-tool)
            ALLOW_TOOLS+=("$2")
            shift 2
            ;;
        --deny-tool)
            DENY_TOOLS+=("$2")
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -p)
            PROMPT="$2"
            shift 2
            ;;
        *)
            if [ -z "$PROMPT" ]; then
                PROMPT="$1"
            fi
            shift
            ;;
    esac
done

# Validate prompt
if [ -z "$PROMPT" ]; then
    echo -e "${RED}Error: Prompt is required${NC}"
    usage
fi

# Check if copilot CLI is available
if ! command -v copilot &> /dev/null; then
    echo -e "${RED}Error: copilot CLI not found. Please install GitHub Copilot CLI.${NC}"
    echo -e "${YELLOW}Installation: npm install -g @github/copilot-cli${NC}"
    exit 1
fi

# Build the command arguments array
CMD_ARGS=()

# Add YOLO mode flags (always enable for non-interactive use)
CMD_ARGS+=("--allow-all-paths")
CMD_ARGS+=("--allow-all-tools")

# Add model if specified
if [ -n "$MODEL" ]; then
    case $MODEL in
        "sonnet-4.5")
            CMD_ARGS+=("--model" "sonnet-4.5")
            ;;
        *)
            # Use default model
            ;;
    esac
fi

# Note: Individual tool permissions are overridden by --allow-all-tools above
# But we keep this logic for potential future selective permission modes
for tool in "${ALLOW_TOOLS[@]}"; do
    # Skip adding individual tools since --allow-all-tools is set
    :
done

for tool in "${DENY_TOOLS[@]}"; do
    CMD_ARGS+=("--deny-tool" "$tool")
done

# Execute
echo -e "${MAGENTA}╔════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║ Copilot CLI - Developer #2 (Implementing) ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Model:${NC} ${MODEL:-default}"
if [ ${#ALLOW_TOOLS[@]} -gt 0 ]; then
    echo -e "${BLUE}Allowed Tools:${NC} ${ALLOW_TOOLS[@]}"
else
    echo -e "${BLUE}Allowed Tools:${NC} ALL (YOLO mode)"
fi
if [ ${#DENY_TOOLS[@]} -gt 0 ]; then
    echo -e "${BLUE}Denied Tools:${NC} ${DENY_TOOLS[@]}"
fi
echo ""
echo -e "${YELLOW}Task Prompt:${NC}"
echo "$PROMPT"
echo ""
echo -e "${MAGENTA}════════════════════════════════════════════${NC}"
echo ""

# Execute copilot command with -p flag and proper argument handling
CMD_ARGS+=("-p")
copilot "${CMD_ARGS[@]}" "$PROMPT"

EXIT_CODE=$?

echo ""
echo -e "${MAGENTA}════════════════════════════════════════════${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Copilot implementation complete${NC}"
else
    echo -e "${RED}✗ Copilot implementation failed (exit code: $EXIT_CODE)${NC}"
fi
echo -e "${MAGENTA}════════════════════════════════════════════${NC}"

exit $EXIT_CODE
