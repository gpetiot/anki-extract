"""
Driver script for anki-extract.

- Backs up previous JSON output
- Runs extract.py to generate a new extract from an Anki database
- Compares new and previous JSON files
- Validates the output using check.py
"""

import os
import shutil
import subprocess
import filecmp
import sys


def usage():
    """Prints usage information and exits."""
    print("Usage: python driver.py <anki_db_file> <output_json_file>")
    sys.exit(1)


if len(sys.argv) != 3:
    usage()

ANKI_DB = sys.argv[1]
JSON_FILE = sys.argv[2]
BACKUP_FILE = JSON_FILE + ".prev"

# Step 1: Backup previous JSON if it exists
if os.path.exists(JSON_FILE):
    print(f"Backing up {JSON_FILE} to {BACKUP_FILE}")
    shutil.copyfile(JSON_FILE, BACKUP_FILE)
else:
    print(f"No previous {JSON_FILE} found, skipping backup.")


# Step 2: Run extract.py on the specified Anki collection
ECHO = f"Running extract.py on {ANKI_DB}..."
print(ECHO)
# Use subprocess to run the script with arguments
result = subprocess.run(
    ["python3", "extract.py", ANKI_DB, JSON_FILE],
    capture_output=True,
    text=True,
    check=True,
)
print(result.stdout)
if result.returncode != 0:
    print("extract.py failed:")
    print(result.stderr)
    sys.exit(1)

# Step 3: Compare new and previous JSON if backup exists
if os.path.exists(BACKUP_FILE):
    print(f"Comparing {JSON_FILE} with {BACKUP_FILE}...")
    if filecmp.cmp(JSON_FILE, BACKUP_FILE, shallow=False):
        print("No differences detected in JSON output.")
    else:
        print(f"Differences detected between {JSON_FILE} and {BACKUP_FILE}.")
        print("Showing unified diff (press q to quit):")
        try:
            subprocess.run(
                f"diff -u {BACKUP_FILE} {JSON_FILE} | less", shell=True, check=True
            )
        except TimeoutError as e:
            print(f"Error running diff: {e}")
else:
    print(f"No previous {BACKUP_FILE} to compare against.")

# Step 4: Run check.py on the produced output file
print(f"Running check.py on {JSON_FILE}...")
result = subprocess.run(
    ["python3", "check.py", JSON_FILE], capture_output=True, text=True, check=True
)
print(result.stdout)
if result.returncode != 0:
    print("check.py failed:")
    print(result.stderr)
    sys.exit(1)

print("Done.")
