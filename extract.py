"""
Extracts entries from an Anki database and writes them to a structured JSON file.
"""

import sqlite3
import json
import re
import sys
from bs4 import BeautifulSoup


def extract_links(soup):
    """Extract all relevant links from the HTML soup"""
    links = {"dictionary": [], "examples": [], "video": []}

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "dictionary" in href:
            links["dictionary"].append(href)
        elif "example-sentences" in href:
            links["examples"].append(href)
        elif "videos" in href:
            links["video"].append(href)

    return links


def extract_definitions(def_string):
    """Extract definitions as a list of dicts from a string."""
    definitions = []
    # Find all [part_of_speech] markers and their positions
    matches = list(re.finditer(r"\[([^\]]+)\]", def_string))
    if not matches:
        return []
    for idx, match in enumerate(matches):
        part_of_speech = match.group(1)
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(def_string)
        definition = def_string[start:end].strip()
        # Remove leading/trailing semicolons and whitespace
        definition = definition.strip(";").strip()
        if definition:
            definitions.append(
                {"part_of_speech": part_of_speech, "definition": definition}
            )
    return definitions


# pylint: disable=locally-disabled, too-many-locals
def parse_html(html_content):
    """Parse the HTML content and extract structured data"""
    html_content = html_content.replace("<br>", "\n").replace("<br/>", "\n")
    soup = BeautifulSoup(html_content, "html.parser")
    links = extract_links(soup)
    sound_match = re.search(r"\[sound:(.*?)\]", html_content)
    audio = sound_match.group(1) if sound_match else ""
    lines = [line.strip() for line in soup.get_text().split("\n") if line.strip()]
    content = {
        "word": "",
        "variants": [],
        "definitions": [],
        "pronunciation": "",
        "conjugations": "",
        "examples": [],
    }
    if lines:
        # Extract main word and definitions from lines[0]
        first_line = lines[0]
        # Try to split on '[' (preferred) or '\u001f' (fallback)
        if "[" in first_line:
            word_part, def_part = first_line.split("[", 1)
            words = [w.strip() for w in word_part.split(",")]
            main_word = words[0]
            if "\u001f" in main_word:
                main_word = main_word.split("\u001f")[0]
            content["word"] = main_word.strip()
            variants = []
            for variant in words[1:]:
                if "\u001f" in variant:
                    variant = variant.split("\u001f")[0]
                variants.append(variant.strip())
            content["variants"] = variants
            # Definitions are everything after the first '['
            def_string = "[" + def_part
            content["definitions"] = extract_definitions(def_string)
        elif "\u001f" in first_line:
            # Fallback for entries with '\u001f' separator
            word_part, def_part = first_line.split("\u001f", 1)
            content["word"] = word_part.strip()
            def_string = def_part.strip()
            content["definitions"] = extract_definitions(def_string)
        else:
            # If no separator, treat whole line as word (edge case)
            content["word"] = first_line.strip()
            content["definitions"] = []

    # Process remaining lines for pronunciation and conjugations
    pronunciation_pattern = re.compile(r"[áàâãäåāăąèéêëēĕėęěìíîïðīĭ]")
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        if "Conjugations:" in line:
            content["conjugations"] = line.replace("Conjugations:", "").strip()
        elif pronunciation_pattern.search(line):
            content["pronunciation"] = line

    return {"content": content, "audio": audio, "links": links}


def main():
    """Main entry point for extracting Anki entries to JSON."""
    if len(sys.argv) != 3:
        print("Usage: python extract.py <anki_db_file> <output_json_file>")
        sys.exit(1)

    anki_db = sys.argv[1]
    output_json = sys.argv[2]

    conn = sqlite3.connect(anki_db)
    cursor = conn.cursor()

    entries = []
    entry_counter = 0  # Initialize counter
    cursor.execute("SELECT flds FROM notes ORDER BY sfld")
    for (flds,) in cursor.fetchall():
        parsed = parse_html(flds)
        if parsed["content"]["word"]:  # Only include entries that have a word
            entry = {
                "word": parsed["content"]["word"],
                "variants": "; ".join(parsed["content"]["variants"]),
                "definitions": parsed["content"]["definitions"],
                "pronunciation": parsed["content"]["pronunciation"],
                "conjugations": parsed["content"]["conjugations"],
                "audio": parsed["audio"],
                "dictionary_url": (
                    parsed["links"]["dictionary"][0]
                    if parsed["links"]["dictionary"]
                    else ""
                ),
                "examples_url": (
                    parsed["links"]["examples"][0]
                    if parsed["links"]["examples"]
                    else ""
                ),
                "video_url": (
                    parsed["links"]["video"][0] if parsed["links"]["video"] else ""
                ),
            }
            entries.append(entry)
            entry_counter += 1  # Increment counter

    # Write to JSON file with proper formatting
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": "1.0",
                "source": "Tagalog.com 2k Deck",
                "count": len(entries),
                "entries": entries,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
        print(f"Successfully wrote {entry_counter} entries to {output_json}")

    conn.close()


if __name__ == "__main__":
    main()
