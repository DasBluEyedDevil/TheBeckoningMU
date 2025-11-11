# AI Quadrumvirate - Token-Efficient Orchestration System

This directory contains the AI Quadrumvirate orchestration system for TheBeckoningMU - a token-efficient approach where Claude Code orchestrates multiple AI agents to maximize session lifespan.

## Core Philosophy

**Token Conservation Through Strategic Delegation**

The AI Quadrumvirate maximizes Claude Code's token lifespan by treating Cursor CLI and Copilot CLI as expendable developer subagents, and Gemini CLI as an unlimited-context code analyst. Claude Code serves as the orchestrator who coordinates all work but performs minimal direct implementation.

## The Four Roles

### 1. Claude Code - The Orchestrator (You)
**Role**: Strategist, Architect, Decision-Maker, Coordinator

**Responsibilities**:
- Gather and clarify requirements
- Query Gemini for code analysis
- Create implementation specifications
- Delegate tasks to Cursor/Copilot
- Coordinate cross-checking
- Verify final results

**Token Budget**: ~3-5k per feature (vs 35k+ old approach)

**Read**: `Claude-Orchestrator.md` for detailed patterns

---

### 2. Gemini CLI - The Researcher (The Eyes)
**Role**: Unlimited-Context Code Analyst

**Responsibilities**:
- Answer questions about codebase (unlimited tokens!)
- Analyze entire directories or files
- Trace bugs across multiple files
- Review architectural patterns
- Security and performance audits
- Pattern recognition

**Token Budget**: Unlimited (1M+ context window) - use freely

**Read**: `Gemini-Researcher.md` for query patterns

**Wrapper**: `.skills/gemini.agent.wrapper.sh`

---

### 3. Cursor CLI - Engineer #1
**Role**: Complex Reasoning Specialist

**Responsibilities**:
- Complex algorithmic problems (using Thinking models)
- Difficult architectural decisions
- Complex refactoring
- Multi-step logical problems
- Cross-check Copilot's work

**Token Budget**: Expendable - use for all complex reasoning work

**Read**: `Cursor-Engineer.md` for task templates

**Wrapper**: `.skills/cursor.agent.wrapper.sh`

---

### 4. Copilot CLI - Engineer #2
**Role**: Backend/Python/GitHub Operations

**Responsibilities**:
- Backend Python implementation (commands, typeclasses)
- GitHub operations (PRs, issues)
- Git operations
- Terminal tasks (evennia commands, tests)
- Cross-check Cursor's work

**Token Budget**: Expendable - use for all backend/GitHub work

**Read**: `Copilot-Engineer.md` for task templates

**Wrapper**: `.skills/copilot.agent.wrapper.sh`

---

## Quick Start

### Example: Implement New Feature

#### Step 1: Ask Gemini for Analysis
```bash
.skills/gemini.agent.wrapper.sh -d "@commands/ @typeclasses/" "
Feature: Add Coterie system with shared resources

Questions:
1. What existing patterns should I follow?
2. Where is similar group data currently stored?
3. What files will be affected?
4. Recommended implementation approach following Evennia?

Provide file paths and code excerpts."
```

#### Step 2: Delegate to Copilot (Backend)
```bash
.skills/copilot.agent.wrapper.sh --allow-write "IMPLEMENTATION TASK:

**Objective**: Create Coterie system commands

**Requirements**:
- +coterie/create: Create new coterie
- +coterie/join: Join existing coterie
- +coterie/pool: Manage shared Blood Pool
- +coterie/leave: Leave coterie

**Context from Gemini**:
[paste Gemini's response]

**Files to Modify**:
- commands/coterie.py: new command set
- typeclasses/characters.py: add coterie attribute

**After Completion**:
1. Run tests: evennia test
2. Test with evennia reload
3. Report changes"
```

#### Step 3: Delegate to Cursor (Complex Logic)
```bash
.skills/cursor.agent.wrapper.sh -m sonnet-4.5-thinking "IMPLEMENTATION TASK:

**Objective**: Implement shared Blood Pool calculation algorithm

**Requirements**:
- Pool size based on coterie size and dots
- Distribution logic for feeding
- Handle edge cases (member death, leaving)

**Context from Gemini**:
[paste Gemini's response]

**Files to Modify**:
- traits/blood.py: add pool calculation

**After Completion**:
1. Run tests
2. Report algorithm and changes"
```

#### Step 4: Cross-Check
```bash
# Copilot reviews Cursor's algorithm
.skills/copilot.agent.wrapper.sh "CODE REVIEW:
Review Cursor's Blood Pool algorithm.
Check: logic, V5 accuracy, edge cases, tests."

# Cursor reviews Copilot's commands
.skills/cursor.agent.wrapper.sh "CODE REVIEW:
Review Copilot's coterie commands.
Check: correctness, error handling, Evennia patterns."
```

#### Step 5: Verify with Gemini
```bash
.skills/gemini.agent.wrapper.sh -d "@commands/ @traits/" "
Changes implemented:
- commands/coterie.py: new command set
- traits/blood.py: shared pool logic

Verify:
1. Architectural consistency with Evennia
2. No regressions
3. V5 rules followed
4. Performance acceptable"
```

**Claude's Token Usage**: ~3k (orchestration only)
**Gemini/Cursor/Copilot**: Handle all analysis and implementation

---

## Wrapper Scripts

All three CLIs have wrapper scripts for convenient invocation:

### Gemini Wrapper
```bash
.skills/gemini.agent.wrapper.sh [OPTIONS] "<prompt>"

Options:
  -d, --dir "@path/"      Directories to analyze
  -a, --all-files         Analyze entire codebase
  -o, --output json       Output format (text, json)
```

### Cursor Wrapper
```bash
.skills/cursor.agent.wrapper.sh [OPTIONS] "<prompt>"

Options:
  -m, --model MODEL       sonnet-4.5, sonnet-4.5-thinking, opus-4.1
  --wsl                   Use WSL execution (default: true)
  -f, --prompt-file       Read prompt from file (avoids bash escaping)
```

### Copilot Wrapper
```bash
.skills/copilot.agent.wrapper.sh [OPTIONS] "<prompt>"

Options:
  --allow-write           Allow file writes
  --allow-git             Allow git operations
  --allow-github          Allow GitHub operations
```

---

## Token Savings Examples

### Feature Development
| Approach | Claude Tokens | Savings |
|----------|--------------|---------|
| Old (Claude does everything) | 35k | - |
| New (Quadrumvirate) | 3-5k | **86-91%** |

### Bug Investigation
| Approach | Claude Tokens | Savings |
|----------|--------------|---------|
| Old | 28k | - |
| New | 2k | **93%** |

### Code Review
| Approach | Claude Tokens | Savings |
|----------|--------------|---------|
| Old | 28k | - |
| New | 1k | **96%** |

---

## Success Criteria

You're using the Quadrumvirate correctly when:
1. ✅ Claude's token usage is <5k per task
2. ✅ Gemini is queried before implementation
3. ✅ Cursor/Copilot do all implementation work
4. ✅ Developers cross-check each other
5. ✅ TodoWrite tracks progress
6. ✅ Final verification uses Gemini + minimal Claude reads

---

## Project Context: TheBeckoningMU

**Evennia MUD** for Vampire: The Masquerade 5th Edition:
- **Language**: Python 3.13+ with Poetry
- **Framework**: Evennia (MUD framework)
- **Commands**: MuxCommand pattern
- **Typeclasses**: Objects, Characters, Rooms, Exits
- **Attributes**: .db (persistent), .ndb (temporary)
- **Game System**: V5 (Vampire: The Masquerade 5e)

**Core Features**:
- V5 dice system (Hunger dice, willpower rerolls)
- Blood Point and Hunger tracking
- Disciplines and powers
- Character traits (Physical, Social, Mental)
- Jobs system for character actions

---

## Files in This Directory

**⭐ Start Here**:
- **README.md** - This file: Complete Quadrumvirate overview

**Role Documentation**:
- **Claude-Orchestrator.md** - Your role as orchestrator with detailed delegation patterns
- **Gemini-Researcher.md** - Gemini's role as unlimited-context analyst
- **Cursor-Engineer.md** - Cursor's role as complex reasoning specialist
- **Copilot-Engineer.md** - Copilot's role as backend/Python/GitHub specialist

**Wrapper Scripts**:
- **gemini.agent.wrapper.sh** - Gemini CLI wrapper script
- **cursor.agent.wrapper.sh** - Cursor CLI wrapper script
- **copilot.agent.wrapper.sh** - Copilot CLI wrapper script
- **CURSOR_WRAPPER_USAGE.md** - Cursor wrapper usage guide

**Project Context**:
- **project-structure.md** - Directory tree, patterns, conventions
- **quick-reference.md** - Common commands, workflows, troubleshooting

**Evennia Framework Skills**:
- **evennia-framework-basics.md** - Core Evennia concepts
- **evennia-development-workflow.md** - Server commands, testing
- **evennia-typeclasses.md** - Deep dive on typeclasses
- **evennia-commands.md** - Command system patterns

**AI Workflow Skills** (legacy, superseded by role docs):
- **ai-quadrumvirate-coordination.md** - Original coordination guide
- **cursor-agent-advanced-usage.md** - Original Cursor guide
- **gemini-cli-codebase-analysis.md** - Original Gemini guide
- **github-copilot-cli-usage.md** - Original Copilot guide

---

## Integration with Claude Code

This system is designed to work seamlessly with Claude Code's native features:

- **TodoWrite**: Track progress and coordinate multi-step tasks
- **Task Tool**: Can still use for subagent delegation when appropriate
- **CLAUDE.md**: Session start protocol and token conservation rules

---

## Summary

**The New Philosophy**:
- **Claude**: Conductor who never plays instruments directly
- **Gemini**: Unlimited knowledge base, always consulted
- **Cursor/Copilot**: Expendable developers who do the work
- **Result**: 80-90% token savings, 8-10x session lifespan

**Remember**: Your value is in orchestration and decision-making, not in reading files or writing code. Delegate everything except strategic thinking.

**Target**: <5k tokens per feature, enabling 40+ features per 200k token session (vs 5-7 in old approach).
