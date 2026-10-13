#!/usr/bin/env bash
# Run the native ScummVM build headlessly under Xvfb, click through the intro,
# open the "new adventure" notice board, type a name and take screenshots.
#
# Usage: tools/dev/native_xvfb_run.sh <scummvm-binary> <game-dir> [extra scummvm args...]
#   e.g. tools/dev/native_xvfb_run.sh bin/scummvm ~/forestia/iso_contents --debugflags=images -d 2
#
# Env: GFX=opengl|surfacesdl (default opengl - same renderer as the web build)
#      TRUE_COLOR=true|false (default true), DISP=:77, OUT=/tmp/forestia_native
# Needs: Xvfb, xdotool, ImageMagick (import).
set -u
BIN=${1:?scummvm binary}; GAME=${2:?game dir}; shift 2
D=${DISP:-:77}; OUT=${OUT:-/tmp/forestia_native}
INI=$(mktemp /tmp/forestia-XXXX.ini)
cat > "$INI" <<INI
[scummvm]
gfx_mode=${GFX:-opengl}
enable_unsupported_game_warning=false

[forestia-win-el]
gameid=forestia
engineid=director
platform=windows
language=el
true_color=${TRUE_COLOR:-true}
path=$GAME
guioptions=noAspect lang_Greek plat_windows gameOption2
enable_unsupported_game_warning=false
INI

Xvfb "$D" -screen 0 1024x768x24 >/dev/null 2>&1 & XV=$!
sleep 1
DISPLAY=$D SDL_AUDIODRIVER=dummy timeout 300 "$BIN" -c "$INI" "$@" forestia-win-el > "$OUT.log" 2>&1 < /dev/null &
SP=$!
sleep 6
WID=$(DISPLAY=$D xdotool search --name "Forestia" | head -1)
shot() { DISPLAY=$D import -window "$WID" "$OUT-$1.png"; echo "screenshot: $OUT-$1.png"; }
# Intro (logos, island) - click through for ~2 minutes until the signpost menu
for i in $(seq 1 18); do DISPLAY=$D xdotool mousemove --window "$WID" 320 400 click 1; sleep 6; done
shot menu
# "Εκκίνηση περιπέτειας" (top sign) -> notice board with the name field
DISPLAY=$D xdotool mousemove --window "$WID" 150 65 click 1; sleep 8
shot board
# Click the orange name field and type
DISPLAY=$D xdotool mousemove --window "$WID" 320 210 click 1; sleep 2
DISPLAY=$D xdotool type --delay 250 Panos7; sleep 3
shot typed
kill $SP 2>/dev/null; sleep 1; kill $XV 2>/dev/null; rm -f "$INI"
echo "log: $OUT.log"
