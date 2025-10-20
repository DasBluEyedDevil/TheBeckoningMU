# Implementation TODO & Notes

This document tracks important future implementation tasks and notes for TheBeckoningMU.

## CRITICAL: AI Quadrumvirate Usage Pattern

**ALWAYS FOLLOW THIS PATTERN TO PRESERVE CLAUDE'S TOKENS**

### The Four Roles

1. **Claude Code (Orchestrator)** - Planning & decision-making only
   - Gather requirements
   - Query Gemini for analysis
   - Delegate implementation
   - Verify results
   - **NEVER read large files (>100 lines) - ask Gemini**
   - **NEVER implement complex features - delegate**
   - **ONLY trivial edits (<5 lines)**

2. **Gemini CLI (Analyst)** - 1M+ context window
   - Analyze entire codebase
   - Trace bugs across files
   - Answer architectural questions
   - Security & performance audits
   - **Note**: Has automatic fallback to Flash model when Pro quota exhausted
   - Both Pro and Flash models can hit rate limits (429 errors)
   - Use `-m, --model` flag to explicitly specify model if needed

3. **Cursor CLI (Developer #1)** - UI/visual work
   - Implement UI components
   - Complex reasoning tasks
   - Visual validation with screenshots
   - Cross-check Copilot's work
   - **Run via WSL wrapper**: `wsl.exe bash -c "cd '/mnt/c/path' && cursor-agent -p --model sonnet-4.5 --output-format text --force 'TASK'"`

4. **Copilot CLI (Developer #2)** - Backend work
   - Implement backend features
   - GitHub operations
   - Terminal tasks
   - Cross-check Cursor's work

### Token Efficiency Targets

- Feature development: <5k Claude tokens (86% savings vs 35k)
- Bug fixes: <2k Claude tokens (93% savings vs 28k)
- Code reviews: <1k Claude tokens (96% savings vs 28k)

---

## High Priority Implementation Tasks

### 1. Web-Based Character Creation (JSON Import)

**Status**: Research in progress (Gemini analyzing reference repo)

**Objective**: Integrate web-based character creation form that exports JSON for server import

**Reference**:
- Web form: https://beckon.vineyard.haus/character-creation-new.html
- Reference repo implementation at: `reference repo/BeckoningMU-master/`

**Tasks**:
- [ ] Analyze reference repo's web chargen implementation (Gemini)
- [ ] Review JSON format and validation rules
- [ ] Understand server-side import commands
- [ ] Identify Jobs system integration for approval workflow
- [ ] Refactor for new codebase architecture
- [ ] Implement Django views/URLs
- [ ] Create import command (+chargen/import)
- [ ] Integrate with approval workflow
- [ ] Add validation and security checks
- [ ] Test with example JSON characters

**Files to Create/Modify** (from Gemini analysis - pending):
- TBD after Gemini analysis completes

---

### 2. Evennia Contribs Integration

**Status**: Not started

**Objective**: Leverage Evennia contrib packages instead of building from scratch

**Reference**: https://www.evennia.com/docs/latest/Contribs/Contribs-Overview.html

**Potential Contribs to Explore**:
- Character sheet display systems
- Dice rolling systems (compare with our V5 dice engine)
- Menu systems for chargen
- Extended Room features
- Combat systems
- Mail/messaging systems
- Any MUSH-related contribs

**Tasks**:
- [ ] Review Evennia contribs documentation (Gemini)
- [ ] Identify useful contribs for V5 MUSH
- [ ] Evaluate vs custom implementation
- [ ] Integrate or adapt relevant contribs
- [ ] Document decisions in CLAUDE.md

---

### 3. ASCII Art & Border Styles Library

**Status**: Reference collected

**Objective**: Create reusable ASCII border styles for help files and output

**Border Style Examples Collected**:
```
+===================================================================+  # Current style
*******************************************************************
/-----------------------------------------------------------------\
.~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.
oOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOo
-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-
,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-.
[|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=|]
╔═════════════════════════════════════════════════════════════╗  # May not render on all clients
```

**Reference**:
- https://asciiart.website/cat.php?category_id=85
- User-provided examples in conversation

**Tasks**:
- [ ] Create `beckonmu/world/ansi_borders.py` with border templates
- [ ] Functions for generating bordered text blocks
- [ ] Support for different themes (gothic, tech, classic)
- [ ] Integration with help system
- [ ] Integration with character sheet output

---

## Medium Priority Tasks

### 4. V5 Data Models Implementation

**Status**: Reference database complete, implementation pending

**Reference**: V5_REFERENCE_DATABASE.md (if exists in reference repo)

**Tasks**:
- [ ] Create `beckonmu/world/v5_traits.py` - Trait system (attrs/skills)
- [ ] Create `beckonmu/world/v5_mechanics.py` - Core mechanics (Hunger, BP)
- [ ] Implement Character typeclass V5 extensions
- [ ] Add db attribute schema
- [ ] Create validation functions
- [ ] Unit tests for all V5 mechanics

---

### 5. Command Implementation (Follow Refactored BBS Pattern)

**Status**: Architecture defined, implementation pending

**Pattern**: Small single-responsibility commands + shared utility modules

**Reference**: `reference repo/BeckoningMU-master/bbs/new_commands.py` (gold standard)

**Tasks**:
- [ ] Implement +roll command (dice rolling)
- [ ] Implement +check command (quick roll)
- [ ] Implement +rouse command (Rouse checks)
- [ ] Implement +sheet command (character sheet display)
- [ ] Implement +spend command (XP spending)
- [ ] Create command utilities module

---

## Low Priority / Future Enhancements

### 6. Enhanced Help System Features

**Tasks**:
- [ ] Add help search functionality
- [ ] Add help aliases (e.g., "help vamp" → "help vampire")
- [ ] Create help index by topic
- [ ] Add "related topics" auto-linking
- [ ] Implement help voting/rating

---

### 7. Admin Tools

**Tasks**:
- [ ] Staff commands for character approval
- [ ] +grant command (XP, status, boons)
- [ ] +inspect command (detailed character data)
- [ ] Logging system for staff actions
- [ ] Audit trail for character changes

---

## Completed Tasks

### ✅ Phase 0: Help System (2025-10-20)
- [x] Configure FILE_HELP_ENTRY_MODULES in settings.py
- [x] Create help_entries.py with directory walker
- [x] Create 10 comprehensive help files:
  - general/welcome.txt
  - commands/commands.txt
  - v5/v5.txt, v5/hunger.txt, v5/disciplines.txt
  - v5/clans.txt, v5/status.txt, v5/boons.txt
  - v5/chargen.txt, v5/roll.txt
- [x] Use simple ASCII borders (+===+) with ANSI color codes
- [x] Add principle #0 to V5 Commands README (leverage Evennia built-ins)
- [x] Commit to git

---

## Development Guidelines Reminders

### When NOT to Use Claude Code Directly

❌ Reading files >100 lines → Use Gemini
❌ Implementing complex features → Delegate to Cursor/Copilot
❌ Analyzing large codebases → Use Gemini
❌ UI/visual work → Delegate to Cursor
❌ Backend implementation → Delegate to Copilot

### When TO Use Claude Code

✅ Gathering requirements
✅ Planning implementation approach
✅ Querying Gemini for analysis
✅ Delegating to Cursor/Copilot
✅ Trivial edits (<5 lines)
✅ Verifying final results
✅ Creating TODO lists and plans

---

## Notes

- Keep this file updated as new tasks are identified
- Use TodoWrite tool for active task tracking
- Reference this document when planning work
- Always check "Completed Tasks" before starting work
