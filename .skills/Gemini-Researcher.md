# Gemini CLI - The Researcher (The Eyes)

## Role
**Unlimited Context Code Analyst** - You have 1M+ token context window. Claude should NEVER read large files - always ask you instead.

## Core Responsibilities
- Answer specific questions about the codebase
- Analyze entire directories or files
- Trace bugs across multiple files
- Review architectural patterns
- Security and performance audits
- Pattern recognition

## When Claude Uses You
- Before implementing: "What files affected by this change?"
- During debugging: "Trace this error through call stack"
- Before delegation: "Show current implementation of [feature]"
- After implementation: "Verify architectural consistency with Evennia"

## Query Patterns

### Pattern 1: Specific Question
```bash
.skills/gemini.agent.wrapper.sh -d "@commands/ @typeclasses/" "
Question: How are V5 dice rolls implemented?

Required information:
- File paths with line numbers
- Code excerpts showing dice pool logic
- Explanation of how Hunger dice work
- Related files or dependencies"
```

### Pattern 2: Architecture Analysis
```bash
.skills/gemini.agent.wrapper.sh -d "@commands/ @world/" "
Analyze architecture for implementing Haven system.

Provide:
1. Current Evennia patterns we follow
2. Files that will be affected
3. Dependencies and risks
4. Recommended approach following MuxCommand patterns
5. Examples from existing commands"
```

### Pattern 3: Bug Tracing
```bash
.skills/gemini.agent.wrapper.sh -d "@commands/ @typeclasses/" "
Bug: Blood Surge not increasing Hunger
Error: [error message if any]
Location: blood.py:145

Trace:
1. Root cause through call stack
2. All affected files
3. Similar patterns that might have same issue
4. Recommended fix following V5 rules

Provide file paths, line numbers, code excerpts."
```

### Pattern 4: Implementation Verification
```bash
.skills/gemini.agent.wrapper.sh -d "@commands/ @typeclasses/" "
Changes implemented:
- commands/blood.py: Added feeding mechanics
- traits/blood.py: Updated Blood Point tracking
- typeclasses/characters.py: Added hunger tracking

Verify:
1. Architectural consistency with Evennia patterns
2. No regressions introduced
3. Best practices followed (Python/Evennia)
4. V5 rules correctly implemented
5. Performance impact
6. Edge cases handled

Provide specific findings with file:line references."
```

### Pattern 5: Pattern Search
```bash
.skills/gemini.agent.wrapper.sh -d "@commands/" "
Find all implementations of MuxCommand error handling.

For each occurrence:
- File path and line number
- Code excerpt
- How it's used
- Any variations or edge cases"
```

## Output Requirements
Always request:
1. **File paths** with line numbers
2. **Code excerpts** showing relevant implementation
3. **Explanations** of how things work
4. **Related files** or dependencies
5. **Recommendations** following Evennia conventions

## Token Savings Examples

### Example 1: Find Dice Implementation
**❌ Old Way (Claude reads)**:
- Claude reads dice.py (2k tokens)
- Claude reads roller.py (3k tokens)
- Claude reads v5_mechanics.py (1k tokens)
- Claude analyzes (500 tokens)
- **Total: 6.5k tokens**

**✅ New Way (Gemini reads)**:
- Claude asks Gemini (300 tokens)
- Gemini responds with summary (0 Claude tokens)
- **Total: 300 tokens (95% savings!)**

## Best Practices

### Be Specific
❌ Vague: "How does this MUD work?"
✅ Specific: "How is Blood Point tracking managed? Show the state flow with file paths."

### Request Structured Output
❌ Vague: "Review this code"
✅ Structured: "Review for: 1) Evennia best practices, 2) V5 rule accuracy, 3) security issues. Rate severity."

### Include Context
❌ No context: "Where is the bug?"
✅ With context: "Bug: Crash at blood.py:145 when feeding. Trace the feeding flow."

## Evennia/Python Context
For TheBeckoningMU project:
- Python 3.13+ with Poetry
- Evennia MUD framework
- MuxCommand pattern for commands
- Typeclasses (Objects, Characters, Rooms, Exits)
- Persistent attributes (.db, .ndb)
- V5 (Vampire: The Masquerade 5e) mechanics

## Quick Reference Commands

```bash
# Understand feature
.skills/gemini.agent.wrapper.sh -d "@commands/" "How is [feature] implemented?"

# Find files
.skills/gemini.agent.wrapper.sh -d "@commands/ @typeclasses/" "Which files handle [functionality]?"

# Trace bug
.skills/gemini.agent.wrapper.sh -d "@commands/" "Error at [location]. Trace root cause."

# Review code
.skills/gemini.agent.wrapper.sh -d "@commands/" "Review [files] for security and Evennia patterns."

# Verify changes
.skills/gemini.agent.wrapper.sh -d "@commands/" "Changes: [summary]. Verify consistency."

# Pattern search
.skills/gemini.agent.wrapper.sh -d "@commands/" "Find all uses of [pattern]."

# Full audit
.skills/gemini.agent.wrapper.sh --all-files -o json "Security audit. Output JSON."
```

## Remember
Every time Claude is about to read a file, ask "Should Gemini read this instead?" The answer is almost always **YES**.
