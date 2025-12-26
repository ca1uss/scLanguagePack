#!/usr/bin/env python3
"""
Process new Star Citizen patch global.ini file.
Preserves existing remix formatting and keeps new entries in stock format.
Updates new entries based on extracted game data using unp4k

"""
import sys
from pathlib import Path
from typing import Dict
import os
import subprocess
import shutil
import tempfile

# Configuration
SC_INSTALL_PATH = r"C:\Program Files\Roberts Space Industries\StarCitizen" # CHANGE THIS IF ITS NOT CORRECT FOR YOU
REPO_ROOT = Path.cwd()
current_version = None

def read_ini_file(file_path: Path) -> Dict[str, str]:
    """Read an ini file and return a dict of key=value pairs."""
    entries = {}
    try:
        with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith(';'):
                    key, value = line.split('=', 1)
                    entries[key] = value
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)
    return entries

def run_step(script_name: str, description: str, args: list) -> bool:
    """Run a python script as a subprocess with arguments."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    
    script_path = REPO_ROOT / "scripts" / script_name
    if not script_path.exists():
        print(f"Error: Script {script_name} not found at {script_path}!")
        return False
        
    cmd = [sys.executable, str(script_path)] + args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            check=False
        )
        
        if result.returncode != 0:
            print(f"Error: {script_name} failed with exit code {result.returncode}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def cleanup_temp(temp_dir: Path, auto_cleanup: bool):
    """Clean up the temporary directory."""
    print(f"\n{'='*60}")
    print("STEP: Cleanup")
    print(f"{'='*60}")
    
    if not temp_dir.exists():
        return

    if auto_cleanup:
        should_delete = True
    else:
        print(f"Temporary data is stored in: {temp_dir}")
        print(f"Size: {get_dir_size_mb(temp_dir):.2f} MB")
        response = input("Do you want to delete this temporary data? (y/n): ").lower()
        should_delete = response == 'y'
        
    if should_delete:
        print(f"Deleting {temp_dir}...")
        try:
            shutil.rmtree(temp_dir)
            print("Cleanup complete.")
        except Exception as e:
            print(f"Error deleting temp dir: {e}")
    else:
        print(f"Skipping cleanup. Data remains in {temp_dir}")

def get_dir_size_mb(path: Path) -> float:
    """Calculate directory size in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

def find_target_env(installPath):
    live = os.path.join(installPath, "LIVE")
    ptu  = os.path.join(installPath, "PTU")
    
    if os.path.isdir(live) and os.path.isdir(ptu):
        while True:
            response = input("patch LIVE or PTU?: ").strip().lower()
            if response == 'live':
                return live
            elif response == 'ptu':
                return ptu
            else:
                print("please input 'live' or 'ptu' :)")
    elif os.path.isdir(live):
        return live
    elif os.path.isdir(ptu):
        return ptu
    raise Exception(f"Neither LIVE nor PTU exists inside {installPath}.\nIf that is not the correct location for the game, please update SC_INSTALL_PATH on line 15")

def find_ini_versions(root, age):
    candidates = []
    for item in os.listdir(root):
        full = os.path.join(root, item)
        if os.path.isdir(full):
            version = parse_version(item)
            if version:
                candidates.append((version, full))\

    if not candidates:
        raise Exception("No valid version folders found.")
    
    if age == 'new':
        print('old: ' + max(candidates)[1])
        return max(candidates)[1]  # highest version tuple
    elif age == 'old':
        print('old: ' + sorted(candidates)[-2][1])
        return sorted(candidates)[-2][1]
    else:
        raise Exception("Version not found")

def parse_version(name):
    parts = name.split(".")
    try:
        return tuple(int(p) for p in parts)
    except:
        return None

def applyChanges():
    channel = find_target_env(SC_INSTALL_PATH)
    version = find_ini_versions(REPO_ROOT, 'new')

    print("Star Citizen Language Pack Automation")
    print("-------------------------------------")
    print(f"Target Version: {version}")
    print(f"Target Channel: {version}")
    
    # Create Temp Directory
    temp_dir = Path(tempfile.mkdtemp(prefix="ScCompLangPackRemix_"))
    print(f"Created temporary working directory: {temp_dir}")
    
    # Step 5: Cleanup
    cleanup_temp(temp_dir, True)

def updateNewIni():
    version = find_ini_versions(REPO_ROOT, 'new')
    current_remix_path = Path(find_ini_versions(REPO_ROOT, 'old')) / 'LIVE' / 'data' / 'Localization' / 'english' / 'global.ini'
    new_stock_path = Path(version) / 'LIVE' / 'stock-global.ini'
    output_path = Path(version) / 'LIVE' / 'data' / 'Localization' / 'english' / 'global.ini'
    output_dir = output_path.parent
    
    #we are currently in 4.5.0 so, should be the following
    print(f"Old Remix: {current_remix_path}") 
    print(f"New Stock: {new_stock_path}")
    print(f"Output:    {output_path}")

    if not current_remix_path.exists():
        print(f"Warning: Old remix file not found at {current_remix_path}")
    if not new_stock_path.exists():
        print(f"Warning: New stock file not found at {new_stock_path}")

    print("\nReading current remixed ini...")
    current_remix = read_ini_file(current_remix_path)
    print(f"  Loaded {len(current_remix)} entries")

    print("Reading new stock ini...")
    new_stock = read_ini_file(new_stock_path)
    print(f"  Loaded {len(new_stock)} entries")

    # Process: start with new stock, overlay remixed values where keys match
    print("Processing entries...")
    new_remix = {}
    kept_remix_count = 0
    new_entry_count = 0

    # Keys to always take from new stock (do not preserve old remix value)
    force_new_keys = {
        'Frontend_PU_Version'
    }

    for key, stock_value in new_stock.items():
        if key == 'Frontend_PU_Version':
            # Special handling for version: use stock value + branding
            new_remix[key] = f"{stock_value} - ca1usss version"
            new_entry_count += 1
            version = stock_value.split('-')[0].strip()
        elif key in current_remix and key not in force_new_keys:
            # This key exists in the old remix, use the remixed value
            new_remix[key] = current_remix[key]
            # Check if it was actually remixed (different from stock)
            if current_remix[key] != stock_value:
                kept_remix_count += 1
        else:
            # New key, keep stock value
            new_remix[key] = stock_value
            new_entry_count += 1

    print(f"  Kept {kept_remix_count} existing remixed values")
    print(f"  Added {new_entry_count} new stock entries")
    print(f"  Total entries: {len(new_remix)}")

    # Write output
    print(f"Writing new ini to {output_path}...")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8-sig') as f:
        for key in sorted(new_remix.keys()):
            f.write(f"{key}={new_remix[key]}\n")

    print("Done!")

    # Report on removed entries
    removed_keys = set(current_remix.keys()) - set(new_stock.keys())
    if removed_keys:
        print(f"\nNote: {len(removed_keys)} entries from old remix not in new stock (removed from game)")

def main():
    updateNewIni()
    applyChanges()


if __name__ == "__main__":
    main()
