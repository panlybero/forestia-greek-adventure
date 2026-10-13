#!/usr/bin/env bash
# Forestia (Greek Edition) - Desktop Launcher
# Launches the preserved 1998 Greek edutainment adventure with patched ScummVM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="$SCRIPT_DIR/bin/scummvm"
GAME_DIR="${1:-$SCRIPT_DIR/game_data}"

if [ ! -f "$BIN_PATH" ]; then
    echo "Error: ScummVM executable not found at $BIN_PATH"
    echo "Please build ScummVM using the patches in patches/ or download the release binary."
    exit 1
fi

if [ ! -d "$GAME_DIR" ]; then
    echo "Error: Game data directory not found at $GAME_DIR"
    echo "Usage: ./run_forestia.sh [path/to/extracted/iso_contents]"
    exit 1
fi

echo "Launching Forestia: Η Μεγάλη Περιπέτεια (Greek Edition)..."
"$BIN_PATH" \
    --path="$GAME_DIR" \
    --language=el \
    director:forestia
