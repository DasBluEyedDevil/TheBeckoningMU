#!/bin/bash

# Cursor CLI Wrapper Script - Developer Subagent #1
# This script provides a convenient interface to invoke Cursor CLI
# for UI/visual work and complex reasoning tasks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default settings
MODEL="sonnet-4.5"
PROGRAMMATIC=true
FORCE=true
OUTPUT_FORMAT="text"
USE_WSL=true  # Default to WSL since cursor-agent is installed there
WSL_USER="devil"
WSL_PATH="/mnt/c/Users/dasbl/PycharmProjects/TheBeckoningMU"
PROMPT_FILE=""  # Optional: read prompt from file

# Function to display usage
usage() {
    cat << EOF
${GREEN}Cursor CLI Wrapper - Developer Subagent #1 (Complex Reasoning/Analysis)${NC}

${BLUE}USAGE:${NC}
    $0 [OPTIONS] "<prompt>"

${BLUE}OPTIONS:${NC}
    -m, --model MODEL          Set the model (default: sonnet-4.5)
                              Options: sonnet-4.5, sonnet-4.5-thinking, opus-4.1
    -i, --interactive          Interactive mode (not programmatic)
    --no-force                Disable force mode (require approval for operations)
    -o, --output FORMAT       Output format (default: text, options: json, markdown)
    -f, --prompt-file FILE    Read prompt from file (avoids bash escaping issues)
    --wsl                     Use WSL for execution (default: true)
    --wsl-user USER           WSL user (default: devil)
    --wsl-path PATH           WSL project path (default: current project)
    -h, --help                Display this help message

${BLUE}EXAMPLES:${NC}
    ${YELLOW}# Standard implementation${NC}
    $0 "IMPLEMENTATION TASK: Refactor dice roller for V5 mechanics..."

    ${YELLOW}# Complex algorithm (use thinking model)${NC}
    $0 -m sonnet-4.5-thinking "Optimize Hunger dice calculation algorithm"

    ${YELLOW}# Maximum capability for hardest tasks${NC}
    $0 -m opus-4.1 "Implement complex state machine for Haven system"

    ${YELLOW}# Interactive mode for exploration${NC}
    $0 -i "Review and analyze the trait system implementation"

    ${YELLOW}# Use prompt file (recommended for complex prompts with code blocks)${NC}
    $0 -f /tmp/task.txt

${BLUE}ROLE IN QUADRUMVIRATE:${NC}
    Cursor is "Developer #1" - Complex reasoning and analysis specialist
    - Complex algorithmic problems (using Thinking models)
    - Difficult architectural decisions
    - Code analysis and refactoring
    - Multi-step logical problems
    - Cross-checks Copilot's work

${BLUE}MODEL SELECTION GUIDE:${NC}
    ${CYAN}sonnet-4.5${NC}           Standard implementation, bug fixes, refactoring
    ${CYAN}sonnet-4.5-thinking${NC}  Complex algorithms, difficult architectural decisions
    ${CYAN}opus-4.1${NC}             Maximum capability for extremely complex tasks

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
    1. Run tests
    2. Report: changes, test results, issues

${BLUE}CROSS-CHECK TEMPLATE:${NC}
    CODE REVIEW TASK:

    Copilot has implemented [feature].

    **Files Changed**: [list]
    **Changes Summary**: [summary]

    **Review For**:
    1. Logic errors
    2. Code quality
    3. Edge cases
    4. Architectural consistency

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
        -i|--interactive)
            PROGRAMMATIC=false
            shift
            ;;
        --no-force)
            FORCE=false
            shift
            ;;
        -o|--output)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -f|--prompt-file)
            PROMPT_FILE="$2"
            shift 2
            ;;
        --wsl)
            USE_WSL=true
            shift
            ;;
        --wsl-user)
            WSL_USER="$2"
            shift 2
            ;;
        --wsl-path)
            WSL_PATH="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            PROMPT="$1"
            shift
            ;;
    esac
done

# Read prompt from file if specified
if [ -n "$PROMPT_FILE" ]; then
    if [ ! -f "$PROMPT_FILE" ]; then
        echo -e "${RED}Error: Prompt file not found: $PROMPT_FILE${NC}"
        exit 1
    fi
    PROMPT=$(cat "$PROMPT_FILE")
fi

# Validate prompt
if [ -z "$PROMPT" ]; then
    echo -e "${RED}Error: Prompt is required (provide directly or via --prompt-file)${NC}"
    usage
fi

# Validate WSL settings if WSL is enabled
if [ "$USE_WSL" = true ] && [ -z "$WSL_PATH" ]; then
    echo -e "${RED}Error: --wsl-path is required when using --wsl${NC}"
    exit 1
fi

# Build the cursor-agent command arguments
CURSOR_ARGS="--force --model $MODEL --output-format $OUTPUT_FORMAT"

# Build the full WSL command
if [ "$USE_WSL" = true ]; then
    # WSL execution mode - call cursor-agent in WSL
    # Escape the prompt for proper bash -c handling
    ESCAPED_PROMPT="${PROMPT//\'/\'\\\'\'}"

    WSL_CMD="cd '$WSL_PATH' && sudo -u $WSL_USER /home/$WSL_USER/.local/bin/cursor-agent $CURSOR_ARGS '$ESCAPED_PROMPT'"
else
    echo -e "${RED}Error: cursor-agent is only available in WSL. Use --wsl flag.${NC}"
    exit 1
fi

# Execute
echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Cursor CLI - Developer #1 (Coding...)   ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Model:${NC} $MODEL"
echo -e "${BLUE}Programmatic:${NC} $PROGRAMMATIC"
echo -e "${BLUE}Force Mode:${NC} $FORCE"
echo -e "${BLUE}Output Format:${NC} $OUTPUT_FORMAT"
if [ "$USE_WSL" = true ]; then
    echo -e "${BLUE}WSL Execution:${NC} Yes (user: $WSL_USER, path: $WSL_PATH)"
fi
echo ""
echo -e "${YELLOW}Task Prompt:${NC}"
echo "$PROMPT"
echo ""
echo -e "${CYAN}════════════════════════════════════════════${NC}"
echo ""

# Create log file
LOG_FILE="/tmp/cursor-agent-$(date +%s).log"

# Cleanup function to kill orphaned processes
cleanup() {
  echo -e "${YELLOW}Cleaning up orphaned cursor-agent processes...${NC}"
  wsl.exe bash -c "pkill -f 'cursor-agent.*worker-server' 2>/dev/null || true"
  rm -f "$LOG_FILE" 2>/dev/null || true
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Execute cursor-agent via WSL in background, redirect to log
wsl.exe bash -c "$WSL_CMD" > "$LOG_FILE" 2>&1 &
CURSOR_PID=$!

echo -e "${BLUE}Cursor Agent PID:${NC} $CURSOR_PID"
echo -e "${BLUE}Log file:${NC} $LOG_FILE"
echo -e "${YELLOW}Monitoring for completion...${NC}"
echo ""

# Monitor for success in logs or process completion
TIMEOUT=300  # 5 minutes
ELAPSED=0
SUCCESS_DETECTED=false

while kill -0 $CURSOR_PID 2>/dev/null; do
  # Check if success indicators appear in output
  if grep -qiE "success|completed|done|implementation complete|changes made" "$LOG_FILE" 2>/dev/null; then
    echo -e "${GREEN}Success detected in logs, allowing graceful completion...${NC}"
    SUCCESS_DETECTED=true
    sleep 5  # Give it a moment to finish writing
    kill $CURSOR_PID 2>/dev/null || true
    break
  fi

  # Check for timeout
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo -e "${YELLOW}Timeout reached ($TIMEOUT seconds), terminating...${NC}"
    kill -TERM $CURSOR_PID 2>/dev/null || true
    sleep 2
    kill -KILL $CURSOR_PID 2>/dev/null || true
    break
  fi

  sleep 2
  ELAPSED=$((ELAPSED + 2))

  # Show progress every 30 seconds
  if [ $((ELAPSED % 30)) -eq 0 ]; then
    echo -e "${BLUE}Still running... (${ELAPSED}s elapsed)${NC}"
  fi
done

# Wait for process to finish
wait $CURSOR_PID 2>/dev/null || true
EXIT_CODE=$?

echo ""
echo -e "${CYAN}════════════════════════════════════════════${NC}"
echo -e "${CYAN}Cursor Agent execution complete${NC}"
echo -e "${CYAN}════════════════════════════════════════════${NC}"
echo ""
echo "=== OUTPUT ==="
cat "$LOG_FILE"
echo "=== END OUTPUT ==="
echo ""

if [ "$SUCCESS_DETECTED" = true ] || [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Cursor implementation complete${NC}"
else
    echo -e "${RED}✗ Cursor implementation failed or timed out (exit code: $EXIT_CODE)${NC}"
fi
echo -e "${CYAN}════════════════════════════════════════════${NC}"

exit $EXIT_CODE
