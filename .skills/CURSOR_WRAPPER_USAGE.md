# Cursor CLI Wrapper - Fixed Usage Guide

## Issue That Was Fixed

**Problem:** When passing prompts with code blocks directly to the wrapper via bash, the code blocks would be interpreted by bash before reaching cursor-agent, causing syntax errors and execution failures.

**Example of problematic usage:**
```bash
bash .skills/cursor.agent.wrapper.sh "Task with code:
```python
def feed(character, target):
    blood = calculate_blood(target)
```
"
# This fails because bash tries to execute the python code!
```

## Solution: Prompt File Option

Added `--prompt-file` / `-f` option to read prompts from files, completely avoiding bash escaping issues.

## Correct Usage Patterns

### ✅ Method 1: Use Prompt File (RECOMMENDED for complex prompts)

```bash
# 1. Create prompt file with your task
cat > /tmp/cursor_task.txt << 'EOF'
IMPLEMENTATION TASK: Blood Pool Algorithm Optimization

## Task
Optimize the Blood Pool sharing calculation for Coterie system.

## Current Implementation
```python
# Current O(n²) approach
def calculate_pool_share(coterie_members):
    for member in coterie_members:
        for other in coterie_members:
            calculate_contribution(member, other)
```

## Required Changes
- Optimize to O(n log n)
- Maintain V5 accuracy
- Handle edge cases (leaving, death)

## Files to Update
- traits/blood.py: optimize calculation
- typeclasses/coteries.py: update pool logic
EOF

# 2. Invoke wrapper with file
bash .skills/cursor.agent.wrapper.sh -f /tmp/cursor_task.txt
```

### ✅ Method 2: Simple String (for short prompts without code)

```bash
bash .skills/cursor.agent.wrapper.sh "Implement validation for Hunger dice in dice roller"
```

### ❌ Method 3: AVOID - Direct code blocks in string

```bash
# DON'T DO THIS:
bash .skills/cursor.agent.wrapper.sh "Task: update feeding
```python
def feed(character):
    return blood
```
"
```

## Usage from Claude Code Bash Tool

When using the Bash tool to invoke Cursor wrapper:

**BAD:**
```xml
<invoke name="Bash">
<parameter name="command">bash .skills/cursor.agent.wrapper.sh "Task with ```python code``` blocks"</parameter>
</invoke>
```

**GOOD:**
```xml
<!-- Step 1: Create prompt file -->
<invoke name="Write">
<parameter name="file_path">/tmp/cursor_task_001.txt</parameter>
<parameter name="content">IMPLEMENTATION TASK: [task with code blocks]

```python
# Code examples here work fine
def example():
    pass
```

Files to modify:
- file.py
</parameter>
</invoke>

<!-- Step 2: Invoke with file -->
<invoke name="Bash">
<parameter name="command">bash .skills/cursor.agent.wrapper.sh -f /tmp/cursor_task_001.txt</parameter>
</invoke>
```

## Model Selection

Use the `-m` / `--model` flag to select the appropriate model:

### For Standard Tasks
```bash
bash .skills/cursor.agent.wrapper.sh "Fix bug in feeding command"
# Uses default: sonnet-4.5
```

### For Complex Reasoning
```bash
bash .skills/cursor.agent.wrapper.sh -m sonnet-4.5-thinking "
Optimize XP calculation algorithm for Disciplines.
Current: O(n²)
Target: O(n log n)
Maintain V5 accuracy.
"
```

### For Extremely Hard Problems
```bash
bash .skills/cursor.agent.wrapper.sh -m opus-4.1 -f /tmp/hard_task.txt
```

## Complete Workflow Example

```bash
# 1. Ask Gemini for context
bash .skills/gemini.agent.wrapper.sh -d "@commands/ @traits/" "
How is the Blood Pool system currently implemented?
Provide:
- File paths
- Code excerpts
- Dependencies
"

# 2. Create detailed task file based on Gemini's response
cat > /tmp/blood_optimization.txt << 'EOF'
IMPLEMENTATION TASK: Optimize Blood Pool Calculation

**Objective**: Reduce algorithmic complexity for Coterie Blood Pool

**Context from Gemini**:
Current implementation in traits/blood.py:245
Uses nested loops for contribution calculation
Dependencies: typeclasses/coteries.py

**Requirements**:
```python
# Current O(n²) - SLOW
def calculate_pool():
    for member in members:
        for other in members:
            process(member, other)

# Target O(n) - FAST
def calculate_pool():
    # Use single pass with accumulator
    pass
```

**Files to Modify**:
- traits/blood.py: optimize calculation
- tests/test_blood.py: add performance tests

**After Completion**:
1. Run: evennia test traits.blood
2. Report: performance comparison, changes
EOF

# 3. Delegate to Cursor with thinking model
bash .skills/cursor.agent.wrapper.sh -m sonnet-4.5-thinking -f /tmp/blood_optimization.txt

# 4. Have Copilot review Cursor's work
bash .skills/copilot.agent.wrapper.sh "CODE REVIEW:
Review Cursor's blood pool optimization in traits/blood.py
Check: correctness, V5 accuracy, test coverage
Run tests and report."
```

## Advanced Options

### Interactive Mode
Use `-i` for interactive exploration:
```bash
bash .skills/cursor.agent.wrapper.sh -i "Explore the trait system architecture and suggest improvements"
```

### JSON Output
Use `-o json` for structured output:
```bash
bash .skills/cursor.agent.wrapper.sh -o json "Analyze dice.py for potential bugs" > analysis.json
```

### Custom WSL Path
If project is in different location:
```bash
bash .skills/cursor.agent.wrapper.sh --wsl-path "/mnt/d/Projects/TheBeckoningMU" "Task here"
```

## Troubleshooting

### Issue: Cursor times out
**Solution**: Break task into smaller subtasks or increase timeout in wrapper script

### Issue: WSL path not found
**Solution**: Check WSL_PATH in wrapper script matches your project location

### Issue: Bash still interpreting code
**Solution**: Always use `-f` flag with prompt file for tasks containing code blocks

### Issue: Permission denied
**Solution**: Ensure wrapper script is executable: `chmod +x .skills/cursor.agent.wrapper.sh`

## Best Practices

1. **Always use prompt files** for tasks with code blocks
2. **Use thinking model** for complex algorithms and architectural decisions
3. **Keep prompts focused** - one task per invocation
4. **Include context** from Gemini in task description
5. **Specify files** to modify explicitly
6. **Request reporting** - ask agent to report changes and test results
7. **Cross-check** - have Copilot review Cursor's work and vice versa

## Summary

The prompt file option (`-f`) solves bash escaping issues and makes complex task delegation reliable. Use it for all tasks that include code blocks, multiline strings, or special characters.

**Remember**: Cursor is your complex reasoning specialist. Use thinking models for hard problems, and always have Copilot cross-check the results.
