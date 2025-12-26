import os
import re
from pathlib import Path
import shutil

# YOU MAY NEED TO CHANGE THIS
SC_INSTALL_PATH = r"C:\Program Files\Roberts Space Industries\StarCitizen"


def parse_version(name):
    parts = name.split(".")
    try:
        return tuple(int(p) for p in parts)
    except:
        return None

def find_latest_version(root):
    candidates = []
    for item in os.listdir(root):
        full = os.path.join(root, item)
        if os.path.isdir(full):
            version = parse_version(item)
            if version:
                candidates.append((version, full))
    if not candidates:
        raise Exception("No valid version folders found.")
    return max(candidates)[1]  # highest version tuple

def find_target_env(root, flag):
    version = None
    if flag:
        version = find_latest_version(root) 
    else: 
        version = root # script directory
    
    live = os.path.join(version, "LIVE")
    ptu  = os.path.join(version, "PTU")
   
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
    raise Exception("Neither LIVE nor PTU exists inside version folder.")

def parse_ini_lines(lines):
    data = {}
    for line in lines:
        m = re.match(r'^(.*?)=(.*)$', line)
        if m:
            key = m.group(1).strip()
            val = m.group(2)
            data[key] = val
    return data

def merge_ini(global_lines, modified_data):
    output = []
    seen = set()

    for line in global_lines:
        m = re.match(r'^(.*?)(=)(.*)$', line)
        if m:
            key = m.group(1).strip()
            prefix = line[: line.index("=") + 1]
            if key in modified_data:
                output.append(f"{prefix}{modified_data[key]}")
                seen.add(key)
            else:
                output.append(line)
        else:
            output.append(line)

    # Add new keys that didn't exist
    for key, val in modified_data.items():
        if key not in seen:
            output.append(f"{key}={val}")

    return output

def main():
    # C:\users\user\scLanguagePack
    ROOT = os.getcwd()

    target_env  = find_target_env(ROOT, True)

    loc = os.path.join(target_env, "data", "Localization", "english")

    global_ini = os.path.join(loc, "global.ini")
    modified_ini = ROOT + r"\target_strings.ini"

    if not (os.path.isfile(global_ini) and os.path.isfile(modified_ini)):
        raise Exception("global.ini or target_strings.ini not found.")

    with open(global_ini, "r", encoding="utf-8") as f:
        global_lines = [line.rstrip("\n") for line in f]

    with open(modified_ini, "r", encoding="utf-8") as f:
        modified_lines = [line.rstrip("\n") for line in f]

    modified_data = parse_ini_lines(modified_lines)

    merged = merge_ini(global_lines, modified_data)

    # Overwrite global.ini
    with open(global_ini, "w", encoding="utf-8") as f:
        f.write("\n".join(merged))

    print(f"Updated: {global_ini}")
    print(f"Source:  {modified_ini}")
    print("Pushing to game directory...")

    game_dir = find_target_env(SC_INSTALL_PATH, False)
    dest_dir = Path(game_dir) / "data" / "Localization" / "english"
    print(dest_dir)
    dest_path = dest_dir

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)  
        shutil.copy2(global_ini, dest_path)
        print(f"Success! Deployed to: {dest_path}")
    except Exception as e:
        print(f"Error deploying file: {e}")


if __name__ == "__main__":
    main()
