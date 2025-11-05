# V:tM Theming & Aesthetics Guide

## Design Philosophy: Gothic Atmosphere

V:tM MUSHes require a dark, gothic aesthetic that reinforces the game's themes of personal horror, political intrigue, and the Beast within. All output should be atmospheric and immersive.

## ANSI Color Scheme Standards

### Core Color Palette

```python
# beckonmu/world/ansi_theme.py

# Primary Colors (V:tM Gothic Theme)
BLOOD_RED = "|r"           # Hunger, damage, warnings
DARK_RED = "|[R"           # Clan names, disciplines
PALE_IVORY = "|w"          # Text, descriptions
SHADOW_GREY = "|x"         # Borders, separators
DEEP_PURPLE = "|m"         # Mystical (Auspex, Blood Sorcery)
MIDNIGHT_BLUE = "|b"       # Night, status, nobility
BONE_WHITE = "|W"          # Headers, emphasis
DECAY_GREEN = "|g"         # Necromancy, decay (Oblivion)
GOLD = "|y"                # Status, boons, highlights

# Semantic Colors
SUCCESS = "|g"             # Successful actions
FAILURE = "|r"             # Failed actions
MESSY = "|[R|h"            # Messy critical (bright red, hilite)
BESTIAL = "|[r|h"          # Bestial failure (dark red, hilite)
CRITICAL = "|y|h"          # Critical success (gold, hilite)
HUNGER_0 = "|W"            # Sated (white)
HUNGER_1_2 = "|w"          # Peckish/Hungry (pale)
HUNGER_3_4 = "|y"          # Ravenous/Famished (gold)
HUNGER_5 = "|[R|h"         # Starving (bright red, hilite)
```

## ASCII Art Standards

### Character Sheet Header

```python
# beckonmu/commands/v5/utils/display_utils.py

SHEET_HEADER = """
|[R╔═══════════════════════════════════════════════════════════════╗
|[R║  |[rT|rH|rE  |[rB|rE|rC|rK|rO|rN|rI|rN|rG  |[r-  |WCharacter Dossier        |[R║
|[R╚═══════════════════════════════════════════════════════════════╝|n
"""

HUNGER_BAR = """
|xHunger: {hunger_dots}  |x[{bar}|x]|n
"""
# Example output: Hunger: ●●●○○  [|[R█████|x░░░░░]
```

### Clan Sigils (ASCII Art)

```python
# beckonmu/world/v5_data.py - Add to each clan definition

CLAN_SIGILS = {
    "Brujah": """
    |[R    ╱╲
    |[R   ╱  ╲
    |[R  ╱ |r⚡|[R ╲
    |[R ╱______╲|n
    """,

    "Toreador": """
    |m    ❦
    |m   ╱|W◈|m╲
    |m  ╱   ╲
    |m ╱_____╲|n
    """,

    "Ventrue": """
    |b   ♛
    |b  ═╬═
    |b   ║
    |b  ═╩═|n
    """,
}
```

### Dice Roll Output Format

```python
# beckonmu/commands/v5/dice.py

ROLL_TEMPLATE = """
|x┌─ Dice Roll ─────────────────────────────────────────────┐
|x│ |WPool:|n {pool} dice |x({normal} normal|x, |[R{hunger} hunger|x)
|x│ |WDifficulty:|n {difficulty}
|x├───────────────────────────────────────────────────────────┤
|x│ |WResults:|n {dice_display}
|x│ |WSuccesses:|n {successes} {outcome}
|x└───────────────────────────────────────────────────────────┘|n
"""

# Dice symbols:
# Normal die success (6-9): |W●|n
# Normal die critical (10): |y◆|n
# Hunger die success (6-9): |[R●|n
# Hunger die critical (10): |[R◆|n (MESSY CRITICAL!)
# Failure (1-5): |x○|n

MESSY_CRITICAL_BANNER = """
|[R╔═══════════════════════════════════════════════════════════════╗
|[R║  |[r⚠  |WMESSY CRITICAL|[r  ⚠                                  |[R║
|[R║  |wYour Beast feeds on your success...                      |[R║
|[R╚═══════════════════════════════════════════════════════════════╝|n
"""

BESTIAL_FAILURE_BANNER = """
|[r╔═══════════════════════════════════════════════════════════════╗
|[r║  |r⚠  |WBESTIAL FAILURE|r  ⚠                                 |[r║
|[r║  |wThe Beast stirs within you...                           |[r║
|[r║  |yCompulsion: {compulsion}                                |[r║
|[r╚═══════════════════════════════════════════════════════════════╝|n
"""
```

### Character Sheet Layout

```python
SHEET_TEMPLATE = """
{header}

|x╔══════════════════════════════════════════════════════════════════╗
|x║ |W{name:<30}|x  Clan: |[R{clan:<25}|x║
|x║ |wGeneration: |n{generation:<3} |wBlood Potency: |n{bp:<2} |wHumanity: |n{humanity:<2}   |x║
|x╠══════════════════════════════════════════════════════════════════╣
|x║  {hunger_display:<60} |x║
|x╠══════════════════════════════════════════════════════════════════╣
|x║  |WATTRIBUTES                                                   |x║
|x╠══════════════════════════════════════════════════════════════════╣
|x║  |wPhysical    |n {physical_attrs:<42} |x║
|x║  |wSocial      |n {social_attrs:<42} |x║
|x║  |wMental      |n {mental_attrs:<42} |x║
|x╠══════════════════════════════════════════════════════════════════╣
|x║  |WDISCIPLINES                                                  |x║
|x╠══════════════════════════════════════════════════════════════════╣
{disciplines}
|x╠══════════════════════════════════════════════════════════════════╣
|x║  |WSTATUS & BOONS                                               |x║
|x╠══════════════════════════════════════════════════════════════════╣
|x║  |wStatus:|n {status:<10} |wBoons Owed:|n {boons_owed:<3} |wBoons Held:|n {boons_held:<3}  |x║
|x╚══════════════════════════════════════════════════════════════════╝|n
"""
```

## Login/Connection Screen

```python
# beckonmu/server/conf/connection_screens.py

CONNECTION_SCREEN = """
|[R
      ██╗   ██╗ █████╗ ███╗   ███╗██████╗ ██╗██████╗ ███████╗
      ██║   ██║██╔══██╗████╗ ████║██╔══██╗██║██╔══██╗██╔════╝
      ██║   ██║███████║██╔████╔██║██████╔╝██║██████╔╝█████╗
      ╚██╗ ██╔╝██╔══██║██║╚██╔╝██║██╔═══╝ ██║██╔══██╗██╔══╝
       ╚████╔╝ ██║  ██║██║ ╚═╝ ██║██║     ██║██║  ██║███████╗
        ╚═══╝  ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
|n
|[r            ╔════════════════════════════════════════╗
|[r            ║  |WT H E   B E C K O N I N G           |[r║
|[r            ║  |wThe Masquerade - 5th Edition       |[r║
|[r            ╚════════════════════════════════════════╝|n

|x┌──────────────────────────────────────────────────────────────┐
|x│  |W"The night has a thousand eyes, and the blood has a     |x│
|x│  |W thousand secrets. Welcome, Kindred, to your Danse      |x│
|x│  |W Macabre."|n                                             |x│
|x└──────────────────────────────────────────────────────────────┘|n

         |wConnect with:|n  connect <username> <password>
         |wCreate char:|n  create <username> <password>

|[R═══════════════════════════════════════════════════════════════════|n
"""
```

## BBS/News Theming

```python
# beckonmu/bbs/utils.py

BBS_BOARD_HEADER = """
|[R╔═══════════════════════════════════════════════════════════════╗
|[R║  |[r⚜  |WBULLETIN BOARD|[r  ⚜  |x- {board_name:<30}      |[R║
|[R╚═══════════════════════════════════════════════════════════════╝|n

|x┌──────┬────────────────────────┬──────────────┬────────────┐
|x│ |W#    |x│ |WSubject                |x│ |WAuthor       |x│ |WDate      |x│
|x├──────┼────────────────────────┼──────────────┼────────────┤
{posts}
|x└──────┴────────────────────────┴──────────────┴────────────┘|n
"""
```

## Status & Boons Display

```python
# beckonmu/status/utils.py

STATUS_HIERARCHY = """
|b╔═══════════════════════════════════════════════════════════════╗
|b║  |W♛  CAMARILLA STATUS HIERARCHY  ♛                         |b║
|b╚═══════════════════════════════════════════════════════════════╝|n

|x┌──────────────────────────────────────────────────────────────┐
|x│ |WRank |x│ |WName                    |x│ |WStatus |x│ |WPosition     |x│
|x├──────┼─────────────────────────────┼────────┼──────────────┤
{status_list}
|x└──────┴─────────────────────────────┴────────┴──────────────┘|n
"""
```

## Implementation Guidelines

### Phase-by-Phase Theming

1. **Phase 0**: Create `beckonmu/world/ansi_theme.py` with color constants
2. **Phase 1**: Theme help files with borders and color coding
3. **Phase 2**: Theme BBS with gothic borders and post formatting
4. **Phase 5**: Theme dice rolls with dramatic success/failure messages
5. **Phase 6**: Add Hunger bar visualization with color gradients
6. **Phase 7**: Add clan sigils to character creation
7. **Phase 10**: Full character sheet with themed layout
8. **Phase 11-12**: Status/Boons displays with hierarchy visualization

### Testing Theming

- [ ] Test on multiple terminal emulators (MUSHclient, Mudlet, tintin++, web client)
- [ ] Verify ANSI codes render correctly
- [ ] Ensure fallback for clients without ANSI support
- [ ] Check readability (don't sacrifice clarity for aesthetics)
- [ ] Verify box-drawing characters display properly (UTF-8 support)

### Best Practices

- Use `|x` (grey) for borders and structural elements
- Use `|[R` (dark red) or `|[r` (bright red) for emphasis and headers
- Keep text `|w` (pale) or `|n` (normal) for readability
- Reserve `|[R|h` (hilite red) for critical alerts (Messy Critical, Hunger 5)
- Use box-drawing characters (`═ ║ ╔ ╗ ╚ ╝ ├ ┤ ┬ ┴ ┼`) for professional borders
- Include thematic symbols: `⚜ ♛ ⚠ ● ◆ ○ ❦ ⚡`

### Accessibility

- Provide `+config color off` option for players who prefer plain text
- Store color preference in `account.db.use_color`
- Create helper function: `colorize(text, account)` that strips ANSI if disabled

## Symbol Reference

### Box Drawing Characters

```
Single Line:  ─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
Double Line:  ═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
```

### Thematic Symbols

```
Vampire/Gothic: ⚜ ♛ ♕ ❦ ⚰ † ✝
Status/Power:   ♛ ♕ ◆ ●
Warning:        ⚠ ⛔ ⚡
Dice:           ● ○ ◆ ◇
```

---

**This guide should be referenced during all phases where user-facing output is created.**
