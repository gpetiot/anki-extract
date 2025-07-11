import os
import shutil
import subprocess
import filecmp
import sys


def usage():
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


# Step 2: Run extract_anki.py on the specified Anki collection
echo = f"Running extract_anki.py on {ANKI_DB}..."
print(echo)
# Use subprocess to run the script with arguments
result = subprocess.run(
    ["python3", "extract_anki.py", ANKI_DB, JSON_FILE], capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("extract_anki.py failed:")
    print(result.stderr)
    exit(1)

# Step 3: Compare new and previous JSON if backup exists
if os.path.exists(BACKUP_FILE):
    print(f"Comparing {JSON_FILE} with {BACKUP_FILE}...")
    if filecmp.cmp(JSON_FILE, BACKUP_FILE, shallow=False):
        print("No differences detected in JSON output.")
    else:
        print(f"Differences detected between {JSON_FILE} and {BACKUP_FILE}.")
        print("You may want to review the diff manually.")
else:
    print(f"No previous {BACKUP_FILE} to compare against.")

print("Done.")
