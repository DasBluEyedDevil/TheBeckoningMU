#!/usr/bin/env python3
"""
Update all help file borders to use Unicode box drawing characters.

This script replaces plain text borders (===, +++, ---) with Unicode box
drawing characters (═══, ╔╗, ║, etc.) for a more polished appearance.
"""

import os
import re
from pathlib import Path

# Base directory for help files
HELP_DIR = Path(__file__).parent / "world" / "help"

def update_borders(content):
    """
    Replace text borders with Unicode box drawing.

    Args:
        content (str): File content

    Returns:
        str: Updated content with Unicode borders
    """
    # Pattern 1: Top border with + and =
    # Example: |[R+===================================================================+
    # Replace with: |[R╔═══════════════════════════════════════════════════════════════════╗
    content = re.sub(
        r'(\|\[?[RrWwYyCcBbGgMmXx]?)\+={60,}\+',
        lambda m: m.group(1) + '╔' + '═' * 67 + '╗',
        content
    )

    # Pattern 2: Vertical bars in headers (middle line)
    # Example: |W|                      TITLE HERE                                   |
    # Keep as is (already using |)

    # Pattern 3: Bottom border with + and =
    # Example: |[R+===================================================================+
    # This is same as pattern 1, already handled

    # Pattern 4: Replace | with ║ for header lines only (between top and bottom borders)
    # This is tricky - we need context. Let's do a multi-line approach.
    lines = content.split('\n')
    new_lines = []
    in_header = False

    for i, line in enumerate(lines):
        # Detect top border
        if '╔' in line and '═' in line:
            in_header = True
            new_lines.append(line)
            continue

        # Detect bottom border
        if in_header and re.search(r'\|\[?[RrWwYyCcBbGgMmXx]?\+={60,}\+', line):
            # Replace with bottom border
            line = re.sub(
                r'(\|\[?[RrWwYyCcBbGgMmXx]?)\+={60,}\+',
                lambda m: m.group(1) + '╚' + '═' * 67 + '╝',
                line
            )
            in_header = False
            new_lines.append(line)
            continue

        # If we're in a header section, replace | with ║ (but keep ANSI codes)
        if in_header:
            # Replace standalone | at start of line with ║
            # Example: |W|  becomes |W║
            line = re.sub(
                r'^(\|\[?[RrWwYyCcBbGgMmXx]?)\|',
                r'\1║',
                line
            )
            # Replace standalone | at end of line with ║
            # Example: |  becomes ║
            line = re.sub(
                r'\|(\|\[?n]?)$',
                r'║\1',
                line
            )

        new_lines.append(line)

    content = '\n'.join(new_lines)

    # Pattern 5: Section dividers (plain dashes)
    # Example: |x------------------------------------------------------------------------
    # Replace with: |x────────────────────────────────────────────────────────────────────────
    content = re.sub(
        r'(\|\[?[RrWwYyCcBbGgMmXx]?)-{60,}',
        lambda m: m.group(1) + '─' * 70,
        content
    )

    return content


def process_help_files():
    """Process all help files in directory tree."""

    if not HELP_DIR.exists():
        print(f"ERROR: Help directory not found: {HELP_DIR}")
        return

    print(f"Processing help files in: {HELP_DIR}")
    print("=" * 80)

    files_processed = 0
    files_updated = 0

    # Find all .txt files recursively
    for filepath in HELP_DIR.rglob("*.txt"):
        files_processed += 1
        print(f"\n[{files_processed}] Processing: {filepath.relative_to(HELP_DIR.parent)}")

        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Update borders
            updated_content = update_borders(original_content)

            # Check if anything changed
            if updated_content != original_content:
                # Write updated content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"  ✓ Updated (borders converted to Unicode)")
                files_updated += 1
            else:
                print(f"  - No changes needed")

        except Exception as e:
            print(f"  ✗ ERROR: {e}")

    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Files processed: {files_processed}")
    print(f"  Files updated:   {files_updated}")
    print(f"  Files unchanged: {files_processed - files_updated}")
    print("\nDone!")


if __name__ == "__main__":
    print("=" * 80)
    print("Help File Border Update Script")
    print("=" * 80)
    print()
    process_help_files()
