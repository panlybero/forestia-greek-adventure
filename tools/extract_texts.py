#!/usr/bin/env python3
"""
Forestia Greek String Extractor
Extracts all rich text dialogs, UI labels, encyclopedia entries,
and mini-game instructions from DATA/FTEXTES.Cxt.
Decodes from native MacGreek into UTF-8 JSON and formatted text.
"""

import os
import sys
import re
import json

def extract_strings(cxt_path, json_out, txt_out):
    if not os.path.exists(cxt_path):
        print(f"Error: {cxt_path} not found.")
        return False

    with open(cxt_path, 'rb') as f:
        data = f.read()

    entries = []
    seen = set()
    pos = 0

    while True:
        idx = data.find(b'RTE0', pos)
        if idx == -1:
            break
        length = int.from_bytes(data[idx+4:idx+8], 'big')
        chunk = data[idx+8:idx+8+length]

        # Extract textual sequences from chunk
        for raw in re.findall(b'[\x20-\xff]{4,}', chunk):
            try:
                decoded = raw.decode('mac_greek', errors='ignore')
                greek_count = sum(1 for c in decoded if '\u0370' <= c <= '\u03ff')
                if greek_count >= 3:
                    # Strip control characters, formatting tags, and length prefixes
                    clean = decoded.strip(' \t\r\n\x00\x01\x02\x03\x04\x05\x06\x07\x08')
                    clean = re.sub(r'^[0-9A-Fa-f]+,', '', clean).strip()
                    if len(clean) >= 2 and clean not in seen:
                        seen.add(clean)
                        entries.append({
                            "id": len(entries) + 1,
                            "offset": idx,
                            "text": clean
                        })
            except Exception:
                pass

        pos = idx + 8 + length

    os.makedirs(os.path.dirname(os.path.abspath(json_out)), exist_ok=True)
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    with open(txt_out, 'w', encoding='utf-8') as f:
        f.write(f"# Forestia (1998 Greek Edition) - Extracted Dialogue & Text\n")
        f.write(f"# Total extracted strings: {len(entries)}\n\n")
        for e in entries:
            f.write(f"[{e['id']:04d}] {e['text']}\n")

    print(f"Extracted {len(entries)} strings to {json_out} and {txt_out}")
    return True

if __name__ == "__main__":
    cxt = sys.argv[1] if len(sys.argv) > 1 else "../iso_contents/DATA/FTEXTES.Cxt"
    j_out = sys.argv[2] if len(sys.argv) > 2 else "docs/greek_strings.json"
    t_out = sys.argv[3] if len(sys.argv) > 3 else "docs/greek_strings.txt"
    extract_strings(cxt, j_out, t_out)
