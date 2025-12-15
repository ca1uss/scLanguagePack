import sys
import re
from pathlib import Path
from typing import Dict, List

# Import from audit script
import audit_sc_native

def load_ini_lines(ini_path: Path) -> List[str]:
    """Load INI file as a list of lines."""
    with open(ini_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def save_ini_lines(ini_path: Path, lines: List[str]):
    """Save lines back to INI file."""
    with open(ini_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def map_ini_keys_to_lines(lines: List[str]) -> Dict[str, int]:
    """Map INI keys to their line numbers for in-place updates."""
    key_map = {}
    for i, line in enumerate(lines):
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith(';') or line.startswith('#') or '=' not in line:
            continue
        
        # Split on first '='
        key = line.split('=', 1)[0].strip()
        key_map[key] = i
    return key_map

def apply_fixes(libs_dir: Path, name_dict: Dict[str, str], ini_path: Path, lines: List[str]):
    print("=" * 60)
    print("Star Citizen Language Pack Fixer")
    print("=" * 60)
    
    # Generate key map
    print("Mapping INI keys...")
    key_map = map_ini_keys_to_lines(lines)
    
    print("Scanning components...")
    # Pass name_dict although it might not be used by the walker itself, it's required by signature
    components = audit_sc_native.walk_component_xmls(libs_dir, name_dict)
    print(f"Found {len(components)} components.")
    
    # 4. Apply Fixes
    updates_count = 0
    skipped_placeholders = 0
    
    class_prefix_map = {
        'Military': 'M',
        'Civilian': 'C',
        'Industrial': 'I',
        'Stealth': 'S',
        'Competition': 'R', 
    }
    
    print("\nApplying fixes...")
    
    for comp in components:
        # Resolve Description to find Class
        desc_token = comp.description_token.lstrip('@')
        description_text = name_dict.get(desc_token, "")
        
        class_match = re.search(r"Class:\s*(\w+)", description_text, re.IGNORECASE)
        item_class = class_match.group(1).capitalize() if class_match else "Unknown"
        
        type_prefix = class_prefix_map.get(item_class, 'C') # Default to C
        
        # Construct Expected Prefix Code
        expected_code = f"{type_prefix}{comp.size}{comp.grade}"
        
        # Get Current Name
        comp_token = comp.token.lstrip('@')
        if comp_token not in key_map:
            # Component not in INI?
            continue
            
        current_line_idx = key_map[comp_token]
        current_line = lines[current_line_idx]
        
        # Parse key=value
        parts = current_line.split('=', 1)
        key = parts[0]
        current_value = parts[1].strip()
        
        # Ignore Placeholders
        if "PLACEHOLDER" in current_value:
            skipped_placeholders += 1
            continue
            
        # Parse Base Name
        # Regex to find existing prefix: ^[A-Z][0-9][A-Z]\s+
        # Example: "C1A PowerBolt" -> Prefix="C1A", Base="PowerBolt"
        match = re.match(r"^([A-Z][0-9][A-Z])\s+(.*)", current_value)
        if match:
            existing_prefix = match.group(1)
            base_name = match.group(2)
        else:
            existing_prefix = None
            base_name = current_value
            
        # Construct New Value
        new_value = f"{expected_code} {base_name}"
        
        if new_value != current_value:
            print(f"Updating {comp_token}:")
            print(f"  Old: '{current_value}'")
            print(f"  New: '{new_value}'")
            lines[current_line_idx] = f"{key}={new_value}\n"
            updates_count += 1
            
    # 5. Save
    print("\n" + "-" * 60)
    print(f"Summary:")
    print(f"  Updates Applied: {updates_count}")
    print(f"  Placeholders Skipped: {skipped_placeholders}")
    
    if updates_count > 0:
        print(f"Saving updates to {ini_path}...")
        save_ini_lines(ini_path, lines)
        print("Done.")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Star Citizen Language Pack Fixer')
    parser.add_argument('--version', default='4.4.0', help='Game version (e.g., 4.4.0)')
    parser.add_argument('--channel', default='LIVE', help='Game channel (e.g., PTU, LIVE)')
    parser.add_argument('--extract-dir', default=None, help='Temporary directory where game data is extracted')
    args = parser.parse_args()

    # Setup paths
    REPO_ROOT = Path(__file__).resolve().parent.parent
    
    if args.extract_dir:
        EXTRACT_DIR = Path(args.extract_dir)
    else:
        EXTRACT_DIR = REPO_ROOT / "extracted"
    
    # Check for extracted data
    libs_dir = EXTRACT_DIR / "dcb" / "Data" / "libs"
    if not libs_dir.exists():
        # Try alternate path
        libs_dir = EXTRACT_DIR / "dcb" / "Data" / "Libs"
    
    if not libs_dir.exists():
        print(f"ERROR: Component data not found at {libs_dir}")
        print("Please run audit_sc_native.py first to extract data.")
        sys.exit(1)

    # Find Language Pack global.ini
    lang_pack_path = REPO_ROOT / args.version / args.channel / "data" / "Localization" / "english" / "global.ini"
    
    if not lang_pack_path.exists():
        print(f"ERROR: Language pack not found at {lang_pack_path}")
        sys.exit(1)
        
    print(f"Target Language Pack: {lang_pack_path}")
    
    # Load data
    print("Loading INI lines...")
    lines = load_ini_lines(lang_pack_path)
    
    print("Parsing INI for name dictionary...")
    name_dict = audit_sc_native.parse_global_ini(lang_pack_path)
    
    if not name_dict:
        print("ERROR: Failed to parse language pack")
        sys.exit(1)

    apply_fixes(libs_dir, name_dict, lang_pack_path, lines)
