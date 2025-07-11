# Anki Extract

Extract data from Anki decks.

## Getting Started

Clone the repository:
```bash
git clone https://github.com/gpetiot/anki-extract.git
cd anki-extract
```

## Dependencies

- Python 3.8+
- beautifulsoup4

## Installation

You can install the package locally:
```bash
pip install .
```
Or use it directly from the source directory.

## Usage

### Extract data from Anki decks
Run:
```bash
python extract.py <anki_db_file> <output_json_file>
```
This will parse the specified Anki database and write the extracted entries to the given JSON file.

### Driver script (recommended workflow)
Run:
```bash
python driver.py <anki_db_file> <output_json_file>
```
This script will:
- Back up the previous JSON output (if it exists)
- Call `extract.py` to generate a new extract
- Compare the new and previous JSON files
- Run `check.py` to validate the output

### Validate JSON output
Run:
```bash
python check.py <json_file>
```
This will check for missing fields and duplicates in the specified JSON file.

Output files (e.g., JSON) will be generated in the project directory.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or new features.

- Fork the repository
- Create a new branch
- Make your changes
- Submit a pull request
