import json
import re
import sys

JSON_FILE = "tagalog_dictionary.json"


# Load JSON
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        sys.exit(1)


def check_definitions(entries):
    """Check for definition field issues."""
    issues = []
    for i, entry in enumerate(entries):
        definition = entry.get("definition", "")
        # Check for double semicolons (;;) which may indicate bad joining
        if ";;" in definition:
            issues.append((i, entry["word"], "Double semicolons in definition"))
        # Check for numbered definitions that are not split
        if re.search(r"1\.\)[^;]+2\.\)", definition):
            issues.append((i, entry["word"], "Multiple numbered definitions not split"))
        # Check for empty definition
        if not definition.strip():
            issues.append((i, entry["word"], "Empty definition"))
    return issues


def check_fields(entries):
    """Check for missing or empty required fields."""
    required = ["word", "part_of_speech", "definition"]
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
        pos = entry.get("part_of_speech", "").strip().lower()
        pron = entry.get("pronunciation", "").strip().lower()
        key = (word, pos, pron)
        if key in seen:
            dups.append(
                (i, word, f"Duplicate word/pos/pron: pos='{pos}', pron='{pron}'")
            )
        else:
            seen.add(key)
    return dups


def main():
    data = load_json(JSON_FILE)
    entries = data.get("entries", [])
    print(f"Loaded {len(entries)} entries from {JSON_FILE}")

    issues = []
    issues += check_definitions(entries)
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
