import json
import re
import sys


def usage():
    print("Usage: python check.py <json_file>")
    sys.exit(1)


if len(sys.argv) != 2:
    usage()

JSON_FILE = sys.argv[1]


# Load JSON
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        sys.exit(1)


def check_fields(entries):
    """Check for missing or empty required fields."""
    required = ["word", "definitions"]
    issues = []
    for i, entry in enumerate(entries):
        for field in required:
            if field not in entry or not str(entry[field]).strip():
                issues.append(
                    (i, entry.get("word", ""), f"Missing or empty field: {field}")
                )
    return issues


def check_duplicates(entries):
    """Check for duplicate words."""
    seen = set()
    dups = []
    for i, entry in enumerate(entries):
        word = entry.get("word", "").strip().lower()
        pron = entry.get("pronunciation", "").strip().lower()
        key = (word, pron)
        if key in seen:
            dups.append((i, word, f"Duplicate word/pron: pron='{pron}'"))
        else:
            seen.add(key)
    return dups


def main():
    data = load_json(JSON_FILE)
    entries = data.get("entries", [])
    print(f"Loaded {len(entries)} entries from {JSON_FILE}")

    issues = []
    issues += check_fields(entries)
    issues += check_duplicates(entries)

    if not issues:
        print("No issues found. JSON looks good!")
    else:
        print(f"Found {len(issues)} issues:")
        for idx, word, msg in issues:
            print(f"Entry #{idx+1} ('{word}'): {msg}")


if __name__ == "__main__":
    main()
