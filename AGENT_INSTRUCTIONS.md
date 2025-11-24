# Agent Instructions: Star Citizen Language Pack Automation

**Objective**: Update the language pack for a new Star Citizen patch.

## 1. Prerequisites
*   **Python 3.9+** installed.
*   **Star Citizen** installed at default location.
*   **Dependencies**: `pip install -r requirements.txt`

## 2. Execution
Run the master automation script located in `scripts/automate_patch.py`.

### Command Syntax
```bash
python scripts/automate_patch.py --version [VERSION] --channel [CHANNEL] [OPTIONS]
```

### Arguments
*   `--version`: The game version (e.g., `4.5.0`).
*   `--channel`: The game channel (e.g., `LIVE` or `PTU`).
*   `--deploy`: Automatically copy the fixed `global.ini` to the game directory.
*   `--auto-cleanup`: Automatically delete temporary extracted files without prompting.

### Example: Full Automation (Run this for the user)
```bash
python scripts/automate_patch.py --version 4.5.0 --channel LIVE --deploy --auto-cleanup
```

## 3. What This Does
1.  **Extracts** game data to a temporary folder (auto-cleaned up).
2.  **Audits** the current `global.ini` against the game data.
3.  **Fixes** naming conventions in `global.ini`.
4.  **Deploys** the result to the game folder.

## 4. Troubleshooting
*   If extraction fails, ensure `tools/unp4k.exe` exists.
*   If the script cannot find the INI, ensure the folder structure `[VERSION]/[CHANNEL]/data/Localization/english/global.ini` exists in the repo.
