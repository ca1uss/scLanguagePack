import json
import requests
import re
import os

def set_commodity_price():
    try:
        # Safe fallback when __file__ doesn't exist
        script_dir = (
            os.path.dirname(os.path.realpath(__file__))
            if "__file__" in globals()
            else os.getcwd()
        )
        ini_path = os.path.join(script_dir, "target_strings.ini")

        if not os.path.exists(ini_path):
            print("INI file not found.")
            return

        response = requests.get("https://api.uexcorp.space/2.0/commodities/")
        data = response.json()
        print("Fetched commodities.")

        lst = (
            data if isinstance(data, list)
            else data.get("data") or data.get("commodities") or []
        )

        values = [
            {
                "name": item["name"],
                "price": item.get("price_sell"),
                "illegal": bool(item.get("is_illegal"))
            }
            for item in lst
        ]

        with open(ini_path, "r", encoding="utf8") as f:
            modified = f.read()

        start_marker = ";commodities start"
        end_marker = ";commodities end"
        start = modified.find(start_marker)
        end = modified.find(end_marker)

        if start == -1 or end == -1:
            print("No commodities section found.")
            return

        before = modified[: start + len(start_marker)]
        section = modified[start + len(start_marker) : end].strip()
        after = modified[end :]

        def format_price(num):
            if num >= 100_000:
                return f"{float(f'{num/1000:.4g}')}k"
            if num >= 10_000:
                return f"{float(f'{num/1000:.3g}')}k"
            if num >= 1_000:
                return f"{float(f'{num/1000:.2g}')}k"
            return str(num)

        updated_lines = []
        for line in section.split("\n"):
            if not line.strip() or "=" not in line:
                updated_lines.append(line)
                continue

            key, value = line.split("=", 1)
            commodity_name = value.strip()
            commodity_name = re.sub(r"^\[\?\]", "", commodity_name)
            commodity_name = re.sub(r"\s+\d+(\.\d+)?.?/SCU$", "", commodity_name).strip()

            match = next(
                (c for c in values if c["name"].lower() == commodity_name.lower()),
                None
            )

            if match:
                formatted = f"{match['name']} {format_price(match['price'])}/SCU"
                if match["illegal"]:
                    formatted = "[!] " + formatted
                updated_lines.append(f"{key}={formatted}")
            else:
                updated_lines.append(f"{key}={commodity_name}")

        new_file = before + "\n" + "\n".join(updated_lines) + "\n" + after

        with open(ini_path, "w", encoding="utf8") as f:
            f.write(new_file)

        print("Update complete.")

    except Exception as err:
        print("Error:", err)

set_commodity_price()
