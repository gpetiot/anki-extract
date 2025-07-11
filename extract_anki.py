import sqlite3
import json
import re
import sys
from bs4 import BeautifulSoup
from html import unescape


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


def parse_html(html_content):
    """Parse the HTML content and extract structured data"""
    # Convert <br> to newlines for easier processing
    html_content = html_content.replace("<br>", "\n").replace("<br/>", "\n")

    # Create soup
    soup = BeautifulSoup(html_content, "html.parser")

    # Get all links
    links = extract_links(soup)

    # Get audio file
    sound_match = re.search(r"\[sound:(.*?)\]", html_content)
    audio = sound_match.group(1) if sound_match else ""

    # Split content by newlines and clean each line
    lines = [line.strip() for line in soup.get_text().split("\n") if line.strip()]

    # Process content
    content = {
        "word": "",
        "variants": [],
        "part_of_speech": "",
        "definition": "",
        "pronunciation": "",
        "conjugations": "",
        "examples": [],
    }

    # First line contains word, POS, and primary definition
    if lines:
        first_line = lines[0]
        if "[" not in first_line:
            print(
                f"DEBUG: Entry without expected [part_of_speech] format: '{first_line}'"
            )
            print("Full content:", html_content)
        else:
            # Split word part and rest
            word_part, rest = first_line.split("[", 1)

            # Process word and variants
            words = [w.strip() for w in word_part.split(",")]

            # Get initial definition if available
            definition = ""
            if "]" in rest:
                pos, definition = rest.split("]", 1)
                definition = definition.strip()
            else:
                print(f"DEBUG: Entry without closing ]: '{rest}'")
                print("Full content:", html_content)

            # Clean up any numbered markers from the word and variants
            main_word = words[0]
            if "\u001f" in main_word:  # Handle special marker
                parts = main_word.split("\u001f")
                main_word = parts[0]
                if len(parts) > 1 and parts[1] not in definition:
                    definition = parts[1] + " " + definition
            content["word"] = main_word.strip()

            # Clean variants
            variants = []
            for variant in words[1:]:
                if "\u001f" in variant:
                    variant_parts = variant.split("\u001f")
                    variant = variant_parts[0]
                    if len(variant_parts) > 1 and variant_parts[1] not in definition:
                        definition = variant_parts[1] + " " + definition
                variants.append(variant.strip())
            content["variants"] = variants

            # Set the final values
            if "]" in rest:
                content["part_of_speech"] = pos.strip()
                content["definition"] = definition.strip()

            # Process POS and definition
            if "]" in rest:
                pos, definition = rest.split("]", 1)
                content["part_of_speech"] = pos.strip()
                # If the word had a numbered marker, add it to the definition
                if "\u001f" in words[0]:
                    numbered_part = words[0].split("\u001f")[1]
                    if numbered_part and numbered_part not in definition:
                        definition = numbered_part + " " + definition.strip()
                content["definition"] = definition.strip()

    # Process remaining lines
    pronunciation_pattern = re.compile(r"[áàâãäåāăąèéêëēĕėęěìíîïðīĭ]")
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # Skip known meta lines
        if any(
            x in line
            for x in [
                "Audio",
                "Dictionary Entry",
                "Example Sentences",
                "Video Example Search",
                "Flash cards by",
            ]
        ):
            continue

        if "Conjugations:" in line:
            content["conjugations"] = line.replace("Conjugations:", "").strip()
        elif pronunciation_pattern.search(line):
            content["pronunciation"] = line
        else:
            # If not special line, treat as additional definition
            if content["definition"]:
                content["definition"] += "; " + line
            else:
                content["definition"] = line

    return {"content": content, "audio": audio, "links": links}


def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_anki.py <anki_db_file> <output_json_file>")
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
                "part_of_speech": parsed["content"]["part_of_speech"],
                "definition": parsed["content"]["definition"],
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
