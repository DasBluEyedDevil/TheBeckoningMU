# Evennia Development Workflow

## Overview

This skill covers the complete development workflow for working with Evennia-based projects, specifically tailored for TheBeckoningMU. Use this when you need to start, stop, test, or manage the Evennia server during development.

---

## Initial Setup

### First-Time Installation

```bash
# Install Evennia (if not already installed)
pip install evennia

# Initialize new game directory
evennia --init mygame

# Generate default SQLite3 database
evennia migrate
```

**TheBeckoningMU**: Database should already be initialized. Only run `evennia migrate` if you've added new models or need to update schema.

### Superuser Creation

When starting the server for the first time, you'll be prompted to create a superuser account. This is your admin account for the game.

---

## Essential Commands

### Server Control

**Start the server** (logs to console):
```bash
evennia start
```

**Stop the server** (complete shutdown):
```bash
evennia stop
```

**Restart the server** (reload without disconnecting players):
```bash
evennia restart
```

**Reload the server** (without full restart, preserves sessions):
```bash
evennia reload
```
**When to use reload**: When you've made code changes and want to apply them without disconnecting players or fully restarting.

**Reboot the server** (full stop and restart, disconnects players):
```bash
evennia reboot
```

**Check server status**:
```bash
evennia status
```

### Testing

**Run all tests**:
```bash
evennia test
```

**Run specific test**:
```bash
evennia test path.to.test.module
```

### Development Tools

**Access Python shell with Evennia context**:
```bash
evennia shell
```
This gives you a Django shell with Evennia's environment loaded, useful for testing queries and debugging.

**View real-time server logs**:
```bash
evennia --log
# or
evennia -l
```

**Log file location**: `beckonmu/server/logs/`

---

## Server Access Points

Once the server is running, access it via:

- **MUD/Telnet Client**: `localhost:4000`
- **Web Client**: `http://localhost:4001`
- **Admin Interface**: `http://localhost:4001/admin`

---

## Development Cycle

### Typical Workflow

1. **Make code changes** to typeclasses, commands, or other Python files
2. **Reload the server** to apply changes:
   ```bash
   evennia reload
   ```
3. **Test in-game** via web client or telnet
4. **Check logs** if issues occur:
   ```bash
   evennia -l
   ```
5. **Run tests** to verify functionality:
   ```bash
   evennia test
   ```

### When to Use Each Command

| Situation | Command | Reason |
|-----------|---------|--------|
| Code changes (typeclasses, commands) | `evennia reload` | Fastest; preserves sessions |
| Settings changes | `evennia restart` | Settings require full restart |
| Database migrations | `evennia migrate` then `evennia restart` | Apply schema changes |
| Server not responding | `evennia stop` then `evennia start` | Full reset |
| Fresh development session | `evennia start` | Initial startup |

---

## Testing Strategy

### Running Tests

Evennia uses Django's testing framework. Tests should be placed in test files within your app directories.

**Run all tests**:
```bash
evennia test
```

**Run specific app tests**:
```bash
evennia test beckonmu.typeclasses
evennia test beckonmu.commands
```

**Run specific test class**:
```bash
evennia test beckonmu.typeclasses.tests.TestCharacter
```

### Writing Tests

Create test files in your modules:
- `beckonmu/typeclasses/tests.py`
- `beckonmu/commands/tests.py`
- etc.

Example test structure:
```python
from evennia.utils.test_resources import EvenniaTest

class TestMyCommand(EvenniaTest):
    def test_command_execution(self):
        # Test your command
        self.call(MyCommand(), "arguments", "Expected output")
```

---

## Debugging

### Common Issues and Solutions

**Server won't start**:
1. Check if server is already running: `evennia status`
2. Check logs: `evennia -l` or view `server/logs/`
3. Check database: ensure `evennia migrate` has been run

**Code changes not applying**:
1. Ensure you're reloading: `evennia reload`
2. Some changes require full restart: `evennia restart`
3. Settings always require restart

**Database issues**:
1. Run migrations: `evennia migrate`
2. Check for migration conflicts
3. Restart server after migrations

**Import errors**:
1. Ensure `__init__.py` files exist in new directories
2. Check Python paths in settings
3. Verify virtual environment is activated

### Debugging with Shell

Use the Evennia shell for quick debugging:
```bash
evennia shell
```

```python
# In the shell
from evennia import search_object
obj = search_object("MyObject")[0]
print(obj.db.attribute)
obj.at_object_creation()  # Re-run creation hook
```

### Debugging with Logs

**Enable debug logging** in `beckonmu/server/conf/settings.py`:
```python
DEBUG = True
```

**View logs in real-time**:
```bash
evennia -l
```

**Add custom logging** in your code:
```python
from evennia.utils import logger

logger.log_info(f"Debug info: {variable}")
```

---

## Updating Existing Game Objects

When you change typeclass code, existing objects need to be updated:

### Automatic Updates (Code Only)

Code changes apply automatically on server reload. However, database-saved attributes do NOT change.

### Manual Updates (Attributes/Data)

**Update single object in-game**:
```
@py obj.at_object_creation()
```

**Update all objects of a type** (use shell):
```python
from typeclasses.characters import Character

for char in Character.objects.all():
    if not char.db.some_new_attribute:
        char.at_object_creation()  # Re-initialize
```

**Best Practice**: Place attribute initialization in `at_object_creation()` hooks to make updates easier.

---

## Migration Workflow

### When Migrations Are Needed

- Adding new typeclass DB fields
- Changing model structure
- Adding new Django apps
- Modifying database schema

### Migration Commands

**Create migrations** (after model changes):
```bash
evennia makemigrations
```

**Apply migrations**:
```bash
evennia migrate
```

**Check migration status**:
```bash
evennia showmigrations
```

**Rollback migration**:
```bash
evennia migrate appname migration_name
```

### Migration Best Practices

1. Always create migrations in a clean state
2. Test migrations on a copy of production data
3. Back up database before running migrations
4. Commit migration files to version control
5. Run migrations in production during maintenance windows

---

## Performance Monitoring

### Check Server Performance

**Memory usage**:
```
@server
```
(in-game command showing server stats)

**Database queries**:
Enable query logging in settings:
```python
DATABASES = {
    'default': {
        # ... other settings
        'OPTIONS': {
            'timeout': 25,
        }
    }
}
```

**Profiling**:
Use Django's debug toolbar or custom profiling in views.

---

## Project-Specific Commands (TheBeckoningMU)

### Trait System Commands

**Load traits from JSON**:
```bash
evennia load_traits path/to/traits.json
```

### Custom Management Commands

Located in `beckonmu/commands/management/` (if any).

Run with:
```bash
evennia <command_name> [args]
```

---

## Virtual Environment

**TheBeckoningMU uses Poetry** for dependency management.

### Activating Environment

The `.venv` directory contains Python packages.

**Windows**:
```bash
.venv\Scripts\activate
```

**Linux/Mac**:
```bash
source .venv/bin/activate
```

### Adding Dependencies

**With Poetry**:
```bash
poetry add package_name
```

**Installing all dependencies**:
```bash
poetry install
```

---

## Configuration Management

### Settings Files

**Main settings**: `beckonmu/server/conf/settings.py`
- Override only what you need
- Reference: https://www.evennia.com/docs/latest/Setup/Settings-Default.html

**Secret settings**: `beckonmu/server/conf/secret_settings.py` (gitignored)
- Use for API keys, passwords, etc.

### Important Settings to Know

**Server name**:
```python
SERVERNAME = "TheBeckoningMU"
```

**Game directories**:
```python
GAME_DIR  # Path to beckonmu/
EVENNIA_DIR  # Path to Evennia installation
```

**Web settings**:
```python
WEBSERVER_PORTS = [(4001, 4002)]  # HTTP, HTTPS
```

**Connection screen**:
Edit `beckonmu/server/conf/connection_screens.py`

---

## Git Workflow with Evennia

### What to Commit

**Always commit**:
- Python code (typeclasses, commands, etc.)
- Configuration files (except secrets)
- Migration files
- Static files (web assets)
- Documentation

**Never commit**:
- `secret_settings.py`
- Database files (`*.db`, `*.db3`)
- Log files (`server/logs/`)
- Cache files (`__pycache__/`)
- Virtual environment (`.venv/`)

### Example .gitignore

Already configured in project, but key entries:
```
*.db
*.db3
server/logs/
secret_settings.py
__pycache__/
.venv/
```

---

## Production Deployment

### Pre-Deployment Checklist

1. ✅ All tests passing: `evennia test`
2. ✅ Migrations created and tested: `evennia migrate`
3. ✅ Secret settings configured for production
4. ✅ DEBUG = False in production settings
5. ✅ Database backed up
6. ✅ Static files collected (if using separate web server)

### Deployment Steps

1. Pull latest code
2. Activate virtual environment
3. Install/update dependencies: `poetry install`
4. Run migrations: `evennia migrate`
5. Restart server: `evennia restart`
6. Monitor logs: `evennia -l`

---

## Troubleshooting Guide

### Server Won't Stop

**Solution**:
```bash
# Find Evennia process
ps aux | grep evennia  # Linux/Mac
tasklist | findstr evennia  # Windows

# Kill process manually
kill -9 <PID>  # Linux/Mac
taskkill /F /PID <PID>  # Windows
```

### Port Already in Use

**Solution**:
1. Check if server is already running: `evennia status`
2. Stop existing server: `evennia stop`
3. Change ports in settings if needed

### Permission Errors

**Solution**:
- Never run as administrator/superuser
- Check file permissions on server directories
- Ensure virtual environment is activated

### Import Errors After Adding New Module

**Solution**:
1. Add `__init__.py` to new directory
2. Restart server (not just reload): `evennia restart`
3. Check PYTHONPATH in settings

---

## Quick Reference

```bash
# Server control
evennia start           # Start server
evennia stop            # Stop server
evennia restart         # Full restart
evennia reload          # Reload code (fast)
evennia status          # Check if running

# Development
evennia test            # Run tests
evennia shell           # Django shell with Evennia
evennia -l              # Watch logs

# Database
evennia migrate         # Apply migrations
evennia makemigrations  # Create migrations

# Access points
# MUD client:    localhost:4000
# Web client:    http://localhost:4001
# Admin panel:   http://localhost:4001/admin
```

---

## Summary

**Development Cycle**:
1. Edit code → `evennia reload` → Test → Repeat
2. Run tests frequently: `evennia test`
3. Check logs when debugging: `evennia -l`
4. Use shell for quick experiments: `evennia shell`

**Key Commands**:
- `reload`: Fast code updates (preserves sessions)
- `restart`: Full restart (for settings changes)
- `migrate`: Database schema updates
- `test`: Run test suite

**Remember**:
- Use Poetry for dependency management
- Don't commit secrets or databases
- Reload after code changes, restart after settings changes
- Place initialization logic in hooks for easier updates
