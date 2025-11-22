# Audit Agent Walkthrough

## Overview
This agent audits the local Star Citizen language pack (`global.ini`) against live component data from `erkul.games`. It verifies that component names follow the compact naming convention: `[Type][Size][Grade] [Name]`.

## Prerequisites
- Python 3.x
- Playwright

## Installation
1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   python -m playwright install
   ```

## Usage
Run the audit script from the repository root:
```powershell
python audit_lang_pack.py
```

The script will:
1. **Update the Repository**: Automatically runs `git pull` to ensure the local language packs are up-to-date.
2. **Detect Erkul Version**: Launches a browser to scrape the current live version from `erkul.games` (e.g., "4.4.0").
3. **Select Local File**: Dynamically locates the corresponding `global.ini` file in the repository based on the detected version.
4. **Scrape & Audit**: Scrapes component data and compares it with the local language pack.
5. **Report Results**: Prints a summary of correct, mismatched, and missing entries.

## Sample Output
```text
Updating repository...
Already up to date.
Navigating to Erkul to check version...
Detected Erkul version: 4.4.0
Parsing c:\Github\ScCompLangPackRemix\4.4.0\PTU\data\Localization\english\global.ini...
...
Audit Complete for version 4.4.0.
Total Checked: 13
Correct: 7
Mismatch: 2
Missing: 4
```

## Known Issues
- **Scraping Completeness**: The scraper currently detects a subset of components due to the dynamic nature of the Erkul table structure. It uses a heuristic stride detection which may skip some rows.
- **Popup Handling**: While robust, popups may occasionally interfere if they load slower than expected. The script attempts to close them multiple times.
