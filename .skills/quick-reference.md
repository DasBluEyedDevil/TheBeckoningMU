# TheBeckoningMU - Quick Reference Guide

## Evennia Server Commands

### Basic Operations
```bash
# Start/Stop/Restart
evennia start                    # Start Evennia server
evennia stop                     # Stop Evennia server
evennia restart                  # Full restart (stop + start)
evennia reload                   # Hot reload code (FAST, use during development)

# Development
evennia test                     # Run all tests
evennia test commands.blood      # Run specific test module
evennia shell                    # Django shell with Evennia context
evennia migrate                  # Run Django migrations

# Information
evennia status                   # Check if server is running
evennia info                     # Display server configuration
evennia connections              # Show active connections
```

### Server Access Points
- **MUD Client**: `telnet localhost 4000`
- **Web Client**: `http://localhost:4001/webclient`
- **Admin Panel**: `http://localhost:4001/admin`
- **API**: `http://localhost:4001/api` (if enabled)

## Reload vs Restart - When to Use What

### Use `evennia reload` (FAST - ~2 seconds)
✅ When you've changed:
- Command code (`commands/*.py`)
- Typeclass code (`typeclasses/*.py`)
- Utilities and helpers (`traits/*.py`)
- Most Python code changes

❌ Don't use reload for:
- Settings changes (`server/conf/settings.py`)
- Django model changes
- New migrations
- Portal code changes

### Use `evennia restart` (SLOW - ~15 seconds)
✅ When you've changed:
- Server settings (`settings.py`)
- Added new Django apps
- Changed database models
- Modified portal code
- Installed new Python packages

💡 **Pro Tip**: During active development, use `evennia reload` constantly. Only restart when you must.

## Common Development Workflows

### Implementing a New Command
```bash
# 1. Ask Gemini for context
.skills/gemini.agent.wrapper.sh -d "@commands/" "
How are commands structured? Show examples from existing commands."

# 2. Create command file (or delegate to Copilot)
# Edit: beckonmu/commands/mycommand.py

# 3. Add to command set
# Edit: beckonmu/commands/default_cmdsets.py

# 4. Reload server
evennia reload

# 5. Test in-game
# Connect to localhost:4000 and try: +mycommand

# 6. Run tests
evennia test commands.mycommand
```

### Debugging a Bug
```bash
# 1. Check server logs
tail -f server/logs/server.log      # Live server log
tail -f server/logs/portal.log      # Live portal log

# 2. Use evennia shell for investigation
evennia shell
>>> from evennia import search_object
>>> char = search_object("CharacterName")[0]
>>> char.db.blood_pool  # Inspect attributes
>>> char.db.all()       # See all persistent attributes

# 3. Add debug prints and reload
# Edit code, add: print(f"DEBUG: {variable}")
evennia reload

# 4. Reproduce bug and check logs
```

### Testing Changes
```bash
# Run all tests
evennia test

# Run specific test file
evennia test commands.test_blood

# Run specific test class
evennia test commands.test_blood.TestFeedCommand

# Run specific test method
evennia test commands.test_blood.TestFeedCommand.test_feed_success

# With verbose output
evennia test --verbosity=2 commands.blood
```

### Creating a New Typeclass
```bash
# 1. Ask Gemini for patterns
.skills/gemini.agent.wrapper.sh -d "@typeclasses/" "
Show how Character typeclass is structured. What hooks are commonly used?"

# 2. Create/edit typeclass
# Edit: beckonmu/typeclasses/myclassname.py

# 3. Add to settings (if base typeclass)
# Edit: server/conf/settings.py
# BASE_CHARACTER_TYPECLASS = "typeclasses.myclassname.MyClass"

# 4. Restart server (settings changed)
evennia restart

# 5. Test creating new instance
# In-game: @create/drop MyObject:typeclasses.myclassname.MyClass
```

## AI Quadrumvirate Quick Commands

### Query Gemini (Unlimited Context)
```bash
# Understand existing code
.skills/gemini.agent.wrapper.sh -d "@commands/ @traits/" "
How is the Blood System implemented? Show file paths and key functions."

# Before implementing
.skills/gemini.agent.wrapper.sh -d "@commands/" "
I need to implement Haven system. What files will be affected?"

# After implementing
.skills/gemini.agent.wrapper.sh -d "@commands/ @typeclasses/" "
Review changes in commands/haven.py. Verify Evennia patterns followed."
```

### Delegate to Copilot (Backend/Python)
```bash
# Implementation
.skills/copilot.agent.wrapper.sh --allow-write "
IMPLEMENTATION TASK: Create +haven command set
Requirements: [from Gemini analysis]"

# Git operations
.skills/copilot.agent.wrapper.sh --allow-git "
Commit Haven system changes with descriptive message"

# GitHub operations
.skills/copilot.agent.wrapper.sh --allow-github "
Create PR for Haven system, closes issue #XX"
```

### Delegate to Cursor (Complex Reasoning)
```bash
# Complex algorithm
.skills/cursor.agent.wrapper.sh -m sonnet-4.5-thinking "
Optimize Discipline XP calculation algorithm. Context: [from Gemini]"

# Architectural refactoring
.skills/cursor.agent.wrapper.sh "
Refactor trait system for modularity. Context: [from Gemini]"
```

## V5 Dice System Quick Reference

### In-Game Commands
```bash
+roll 5                          # Roll 5 normal dice
+roll/hunger 5=2                 # Roll 5 dice with 2 Hunger dice
+roll/wp 5                       # Roll 5 dice, reroll up to 3 failures (Willpower)
+roll/wp/hunger 6=1              # Combined: Willpower + Hunger
```

### Dice Interpretation
- **10**: Success (two 10s = critical)
- **6-9**: Success
- **1-5**: Failure
- **Hunger 10**: Counts as success but contributes to Messy Critical
- **Hunger 1**: Counts as failure but contributes to Bestial Failure

## Blood System Quick Reference

### In-Game Commands
```bash
+blood                           # Show Blood Pool and Hunger
+feed <target>                   # Feed from target (human/animal)
+feed/messy <target>             # Messy Critical feeding
+surge                           # Blood Surge (+2 dice, Hunger +1)
+mend <damage>                   # Mend damage (BP spent = damage healed)
```

### Blood Point Costs (V5 Rules)
- **Mend 1 Superficial Damage**: 1 BP
- **Blood Surge**: 0 BP (but Hunger +1)
- **Awaken at Dusk**: 1 BP (+ Rouse Check)
- **Blush of Life**: 1 BP
- **Use Discipline**: Varies (Rouse Check)

## Troubleshooting

### "Command not found" after adding new command
```bash
# 1. Did you add to command set?
# Check: beckonmu/commands/default_cmdsets.py

# 2. Did you reload?
evennia reload

# 3. Check logs for errors
tail -f server/logs/server.log
```

### "Object has no attribute 'db'"
```python
# Wrong: Trying to access .db before object exists
def some_function(char):
    char.db.blood_pool = 5  # ERROR if char is None

# Right: Check object exists first
def some_function(char):
    if not char:
        return "Character not found"
    char.db.blood_pool = 5
```

### "Settings change not taking effect"
```bash
# Settings changes require full restart
evennia restart  # Not reload!
```

### "Tests failing after changes"
```bash
# Run tests to see what broke
evennia test

# Check specific test
evennia test commands.test_blood --verbosity=2

# Fix code, then reload and retest
evennia reload
evennia test commands.test_blood
```

## Poetry (Dependency Management)

```bash
# Add new package
poetry add package-name

# Install all dependencies
poetry install

# Update dependencies
poetry update

# Show installed packages
poetry show

# Activate virtual environment
poetry shell
```

## Git Workflow Reminders

```bash
# Always work on feature branches
git checkout -b feature/haven-system

# Commit frequently with descriptive messages
git add beckonmu/commands/haven.py
git commit -m "feat: add Haven system commands for creating and upgrading havens"

# Push to remote
git push -u origin feature/haven-system

# Use Copilot for git operations
.skills/copilot.agent.wrapper.sh --allow-git "
Stage Haven files and commit with message about Phase X implementation"
```

## Pro Tips

### 🔥 During Active Development
1. Keep `evennia reload` as muscle memory
2. Have logs open in another terminal: `tail -f server/logs/server.log`
3. Use `evennia shell` for quick attribute inspection
4. Test in-game immediately after each change

### 🧠 Token Conservation
1. **Always** query Gemini before reading code yourself
2. Delegate implementation to Cursor/Copilot
3. Use TodoWrite to track multi-step tasks
4. Target: <5k tokens per feature

### 📚 Documentation
1. Update V5_MECHANICS.md when implementing new mechanics
2. Update TODO.md when completing tasks
3. Document complex algorithms with comments
4. Add docstrings to all commands and functions

### ✅ Before Committing
1. Run tests: `evennia test`
2. Check logs for errors
3. Test in-game thoroughly
4. Update relevant documentation
5. Use descriptive commit messages

## Additional Resources

- **Full Evennia Command Reference**: `.skills/evennia-commands.md`
- **Typeclass Deep Dive**: `.skills/evennia-typeclasses.md`
- **Development Workflow**: `.skills/evennia-development-workflow.md`
- **Project Structure**: `.skills/project-structure.md`
- **Quadrumvirate Guide**: `.skills/README.md`
