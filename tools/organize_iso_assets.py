#!/usr/bin/env python3
"""
Forestia ISO Asset Organizer
Extracts and normalizes Forestia CD-ROM assets from an ISO or folder,
creating case-insensitive symlinks required by Macromedia Director on POSIX systems.
"""

import os
import sys
import subprocess
import shutil

def organize_assets(source_dir, target_dir):
    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)

    print(f"Organizing assets from: {source_dir}")
    print(f"Target directory: {target_dir}")

    os.makedirs(target_dir, exist_ok=True)

    # Walk all files and directories
    for root, dirs, files in os.walk(source_dir):
        rel = os.path.relpath(root, source_dir)
        dest_parent = target_dir if rel == '.' else os.path.join(target_dir, rel)
        os.makedirs(dest_parent, exist_ok=True)

        for d in dirs:
            orig = os.path.join(dest_parent, d)
            lower = os.path.join(dest_parent, d.lower())
            upper = os.path.join(dest_parent, d.upper())
            if lower != orig and not os.path.exists(lower):
                try:
                    os.symlink(d, lower)
                except OSError:
                    pass
            if upper != orig and not os.path.exists(upper):
                try:
                    os.symlink(d, upper)
                except OSError:
                    pass

        for f in files:
            src_file = os.path.join(root, f)
            dest_file = os.path.join(dest_parent, f)
            if not os.path.exists(dest_file):
                try:
                    os.link(src_file, dest_file)
                except OSError:
                    shutil.copy2(src_file, dest_file)

            lower = os.path.join(dest_parent, f.lower())
            upper = os.path.join(dest_parent, f.upper())
            if lower != dest_file and not os.path.exists(lower):
                try:
                    os.symlink(f, lower)
                except OSError:
                    pass
            if upper != dest_file and not os.path.exists(upper):
                try:
                    os.symlink(f, upper)
                except OSError:
                    pass

    # Ensure CD check dummy file exists
    cd_check_lower = os.path.join(target_dir, "aaafores.txt")
    cd_check_upper = os.path.join(target_dir, "AAAFORES.TXT")
    if not os.path.exists(cd_check_lower) and not os.path.exists(cd_check_upper):
        with open(cd_check_upper, 'w') as f:
            f.write("")
        try:
            os.symlink("AAAFORES.TXT", cd_check_lower)
        except OSError:
            pass

    print("Asset organization and case-sensitivity normalization complete.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 organize_iso_assets.py <source_path> <target_path>")
        sys.exit(1)
    organize_assets(sys.argv[1], sys.argv[2])
