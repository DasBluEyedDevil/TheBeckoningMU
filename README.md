# TheBeckoningMU

A Vampire: The Masquerade 5th Edition MUD built on Evennia.

## Quick Start

**IMPORTANT:** Always run Evennia commands from the project root directory (`TheBeckoningMU/`), not from inside `beckonmu/`.

### Helper Scripts (Recommended)

```powershell
# Start the server
.\start-evennia.ps1

# Stop the server
.\stop-evennia.ps1

# Reload the server (preserves sessions)
.\reload-evennia.ps1
```

### Manual Commands

If you prefer to run commands manually:

```powershell
# Make sure you're in the project root
cd C:\Users\dasbl\PycharmProjects\TheBeckoningMU

# Then run evennia commands
evennia start
evennia stop
evennia reload
evennia status
```

## Directory Structure

- **Project Root** (`TheBeckoningMU/`) - Run Evennia commands from here
- `beckonmu/` - Main game code (Python package)
  - `server/conf/` - Configuration files
  - `world/` - Game data (v5_data.py, v5_dice.py, etc.)
  - `commands/` - Game commands
  - `typeclasses/` - Game entity definitions
  - `web/` - Web interface
- `server/` - Server runtime (database, logs)

## Access Points

- **MUD Client:** `localhost:4000`
- **Web Client:** `http://localhost:4001`
- **Web Character Creation:** `http://localhost:4001/character-creation/`
- **Staff Character Approval:** `http://localhost:4001/staff/character-approval/`
- **Admin Interface:** `http://localhost:4001/admin`

## Documentation

See `CLAUDE.md` for development guidelines and architecture details.
