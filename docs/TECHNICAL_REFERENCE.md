# Forestia (Greek, 1998): Technical Reference

These are working notes on the game, the Macromedia Director engine it was built with, the ScummVM changes needed to run it, and the native and WebAssembly port in this repository. They are meant for whoever picks this up next, including future us.

> **Status (Oct 2026):** the game runs natively (Linux build in `bin/`) and in the browser on desktop and mobile at <https://plympe.com/forestia-greek-adventure/>. Verified so far: intro sequence, sound, correct colours, the main menu, the "new adventure" notice board, typing a player name, the welcome screen, Sam's introduction, the help screen, walking in the first forest scene, and the map. A full play-through has **not** been done yet, so expect engine bugs further in.

Contents:

1. [The game](#1-the-game)
2. [How the game is built (Director 6.5)](#2-how-the-game-is-built-director-65)
3. [ScummVM changes](#3-scummvm-changes)
4. [The web port](#4-the-web-port)
5. [Building](#5-building)
6. [Deployment](#6-deployment)
7. [Testing & debugging toolkit](#7-testing--debugging-toolkit)
8. [Known issues & TODO](#8-known-issues--todo)
9. [History of the fixes](#9-history-of-the-fixes)

---

## 1. The game

| | |
|---|---|
| Title | *Forestia: Η Μεγάλη Περιπέτεια* (*Forestia: The Great Adventure*) |
| Developer | Kaiphea (France) |
| Greek publisher | Εκδοτικός Οργανισμός Λιβάνη ("LIVANI" in `DATA.TAG`), with Laser Media and Daddy Oak logos in the intro |
| Year | 1998 (files are dated 1997–2000; `Forestia.exe` is dated Jan 2000) |
| Genre | Educational point-and-click adventure about forest wildlife, with mini-games and an animal album/encyclopedia |
| Engine | Macromedia Director 6.5 projector (Windows), files `RIFX`/`MV93`, ScummVM version 650 |
| Original requirements | Windows 95, Pentium, 16 MB RAM, 4x CD-ROM, **640×480, 256 colours** (the installer README asks for 256 colours, but the movies were authored in 16-bit; see §2.5) |
| ScummVM ids | engine `director`, game `forestia`, target used here `forestia-win-el` |

### 1.1 Disc layout (`Forestia-Greek.ISO`, 674 MB)

The disc is a Mac/PC hybrid. Only the PC side is used.

```
/                      Forestia.exe (projector, 1,529,858 bytes), SETUP.EXE + InstallShield files
                       (_sys1.cab, _user1.cab, data1.cab, setup.ins …), AUTORUN.INF (runs SETUP.EXE),
                       AAAFORES.TXT (0 bytes, the CD "fingerprint" file), README.TXT, *.BMP/ICO,
                       FORE.dat (38 MB, actually an EPS PostScript file, probably cover/manual art)
/Xtras/                FILEIO, MIX32, PMLite (+ .reg), SCRNXTRA, SMXTRA, "Sound Import Export",
                       SWADCMPR, SWASTRM (Shockwave Audio)
/DATA/                 42 *.Dxr movies + 42 *.Cxt external casts (592 MB), Fontmap.txt (stock Director 6
                       font map); SONF/ and ESON/ hold AIFF sound files
/F_DATA/               boot/logo sounds (LASERMED.AIF, DADDY.AIF, MORHURL.AIF …), SON.cxt, SAMN/ (more AIFF)
```

The main movie is `DATA/FRST.Dxr`. The other movies are scenes and mini-games (`F_111` … `F_332`, `F_SC1-3`, `F_FET1-2`), the album (`FALBUM`), the end credits (`GENEFIN`), quitting (`QUIT`), help (`AIDEG`), the starters (`STARTER` for Mac, `STARTERPC` for PC), and so on.

**Audio:** 125 uncompressed AIFF files, all 16-bit PCM, 98 mono and 27 stereo, at 22,050 Hz or 44,100 Hz. ScummVM decodes these natively, so no codec libraries are needed. Sound is played with `sound playFile <channel>, GaccesDD & "x.aif"` and `puppetSound`. The score's sound channels are not used.

### 1.2 Boot chain

1. The `Forestia.exe` projector's internal movie checks for the CD (`AAAFORES.TXT` on `D:`, then scans `C:`–`Z:` with the FileIO Xtra). It also opens `F_data\morhurl.aif` purely as an existence check. It sets these globals:
   - `GaccesCd = <drive>\DATA\`
   - `GaccesDD = the pathName & "F_DATA\"`
   - `GaccesF`
2. It then runs `go to movie "D:\DATA\FRST"`. ScummVM maps the drive path onto the game directory. In the logs this shows as `Window::setNextMovie: 'D:\DATA\FRST' -> 'data/frst.dxr'`.
3. `FRST.Dxr` plays the publisher logos (Livani, which is silent; LaserMedia, which plays `LASERMED.AIF`; and Daddy Oak), then the floating-island title screen, then the signpost main menu.
   - The Livani logo is silent; the first audible sound is `LASERMED.AIF`. (Earlier builds took ~40 s to get there because of the blocking palette fades fixed in §3.13.)
   - The same logic exists in the decompiled `STARTERPC` scripts; see `reverse_engineering_report.md`.

### 1.3 `FRST.Dxr` cast libraries

These are the logical cast libraries in the order the movie defines them. External paths are Mac-style (`FORESTIA:DATA:…`), which shows the game was authored on a Mac.

| # | Name | Source |
|---|---|---|
| 1 | Internal | inside FRST.Dxr |
| 2 | Shared.Cst | `DATA/Shared.Cxt`: **all 72 custom palettes live here** (members 500–571) |
| 3 | balades en cours | internal |
| 4 | GENERIK | internal |
| 5 | JEUX # | internal |
| 6 | SONGS | `SONGS.Cxt` |
| 7 | BAJ | `BAJ.Cxt` |
| 8 | INTER | `INTER.Cst` (ScummVM loads `INTER.Dxr`) |
| 9 | IF2 | `IF2.Cxt` |
| 10 | CFAIDE | `CFAIDE.Cxt` |
| 11 | SONforet | `SONforet.Cxt` |
| 12 | DATA | `DATA.Cxt` |
| 13 | FILM | `FILM.Cxt` |
| 14 | Curseur BAJ | internal |
| 15 | FTEXTES | `FTEXTES.Cxt`: Greek texts (MacGreek) |
| 16 | LE GENE | internal |
| 17 | FAIDE | `FAIDE.Cxt` |
| 18 | SON | `SON.CST` |
| 19 | CURS | internal |
| 20 | LOCAL | internal |

Movie config: frame rate 20, default palette = member 501 of castLib 2, and the cast config reports platform "mac". Several movies report bit depth 16 (`STUB: loadConfig(): Movie bit depth is 16`).

### 1.4 Main menu & player name

- **Signpost menu:** "Εκκίνηση περιπέτειας" (new adventure) and "Συνέχιση περιπέτειας" (continue adventure). The bottom bar has "Έξοδος" (quit), "Επιλογές" (options) and "Βοήθεια" (help).
- **New adventure** opens the **notice board** ("Οι περιπέτειες που συνεχίζονται").
  - The orange box is the editable text field cast member **`nomutilisateur`**.
  - The two black boxes pick an age group. Script `BehaviorScript 12 - OK nom`: if the clicked sprite is 38, `AGE = 1`, otherwise `AGE = 2`.
  - The script then stores `Gnomjoueur = the text of cast "nomutilisateur"` and calls `nouveaujoueur2()`. That handler was not found in the decompiled casts we have.
- Quit is bound via `the keyDownScript = "KEYQUIT"`: Cmd/Ctrl + `.` or `q` while `the exitLock = 1`.
- How save games are written has **not been investigated**. It is probably FileIO or `setPref`, which ScummVM stores in its save directory (IndexedDB in the browser).

### 1.5 Text encoding

- All Greek text, including rich text `RTE0/RTE1` chunks, field text and fonts, is stored as **MacGreek (x-mac-greek)**. The localisation was done on a Mac and the Windows build kept the Mac bytes.
- This is why Greek shows as mojibake on Windows/VMs, which expect cp1253 or cp737.
- Fonts referenced include Geneva, Monaco and UB_Lucky in the starter. Greek text uses Mac fonts that ScummVM falls back to its built-in fonts for.
- Extracted strings are in `docs/greek_strings.{txt,json}`, produced by `tools/extract_texts.py`.

### 1.6 Decompiled sources

The workspace (outside this repo) has ProjectorRays output: `decompiled_frst/FRST/casts/<castlib>/*.ls|.lasm`, `decompiled_starter*`, `decompiled_texts`, `decompiled_lingof`, `inter_dump`. Useful entry points:

- `Internal/MovieScript 145 - Masterscript`
- `BehaviorScript 12 - OK nom`, `161 - enregistrement partie en cours` (saving the current game), `28 - reprendre` (resume), `69 - delete`, `66 - clic poubelle` (trash can)
- `LE GENE/BehaviorScript 2/364/375/383` (logo sounds)

---

## 2. How the game is built (Director 6.5)

These are the Director features this game relies on, and therefore where ScummVM bugs show up.

1. **Many external casts.** Twenty cast libraries, ten of them external `.Cxt` files referenced by Mac paths.
2. **Shared palettes.** Bitmaps in *other* cast libraries reference palettes in `Shared.Cxt` using **castLib 0** (`palette: member 501 of castLib 0`). Bitmaps inside Shared itself use an explicit castLib 2. ScummVM didn't understand castLib 0; see §3.2.
3. **Score palette channel.** Some frames set "System – Mac" (`member -1`) with long fades. In 8-bit mode this swaps the whole screen to the Mac system palette and makes everything psychedelic. In 16/32-bit mode bitmaps carry their own palettes and the palette channel hardly matters. This is how the game looked on its intended 16-bit display.
4. **Bit depth.** The movies were authored at 16-bit ("thousands of colours"). The installer README still recommends 256 colours.
5. **Lingo.** Behaviour scripts, puppet sprites/sounds, `puppetTransition` (e.g. type 26 = dissolve patterns, changing area), `the keyDownScript`, `the exitLock`, and the FileIO Xtra.
6. **Xtras.** These are reported as unimplemented by ScummVM, so far with no visible effect: `swadcmpr`, `swastrm` (Shockwave Audio), `pmlite`, `MIX32`, `SCRNXTRA`, `sound import export`. FileIO is implemented by ScummVM.

---

## 3. ScummVM changes

- **Base:** upstream ScummVM `master` at commit `32f3e402` (Oct 12 2026), built with only the Director engine enabled.
- **Source tree:** the full diff is `patches/scummvm-greek-forestia.patch`. The source tree with the changes applied is in the workspace at `../scummvm`.
- **Regenerating the patch:**
  ```bash
  cd scummvm && git diff -- backends common engines > ../forestia-greek-adventure/patches/scummvm-greek-forestia.patch
  ```

### 3.1 Greek text and detection (first pass)

| File | Change |
|---|---|
| `engines/director/detection_tables.h` | Adds the Greek executable: `WINGAME1_l("forestia", "", "Forestia.exe", "t:0ee0e228692af7bfa8903e6235caac2a", 1529858, Common::EL_GRC, 650)` (tail-5000 MD5) |
| `common/encodings/singlebyte.cpp`, `common/enc-internal.h`, `common/str-enc.{h,cpp}` | New `kMacGreek` code page with the standard Apple MacGreek table for 0x80–0xFF |
| `engines/director/util.cpp` | `getEncoding()`: Greek maps to `kWindows1253` on Windows and `kMacGreek` on Mac. `detectFontEncoding()` falls back to the game language when the font's language is unknown |
| `engines/director/castmember/richtext.cpp` | RTE1 plain text is decoded with the cast's file encoding (MacGreek here) instead of the platform encoding |
| `engines/director/movie.cpp` | `getCastMember`, `getCast`, `getCastMemberInfo`, `getStxt` and `getScriptContext` map `castLib == -1` to `DEFAULT_CAST_LIB`. This fixes lookups without an explicit library, which crashed or failed |

### 3.2 Palette fix: blown-out colours

- **Symptom:** with `true_color=true`, every image was over-saturated. With 8-bit colour, images were drawn with the wrong palette and looked psychedelic.
- **Root cause:** bitmap cluts are stored as `member N of castLib 0`. The palettes are registered as `member N of castLib 2`, so lookups failed and fell back to the Mac system palette.
- **Fix:** `DirectorEngine::resolvePaletteId()` in `engines/director/graphics.cpp`.
  - Built-in palettes (negative ids) are mapped to castLib −1.
  - For `castLib == 0`, it searches the loaded palettes for the same member number and picks the lowest castLib.
  - `getPalette()` and `hasPalette()` use it, and so do `BitmapCastMember::getDitherImg()` and `isModified()` in `castmember/bitmap.cpp`.
- **Upstream:** this is a candidate. The exact semantics of castLib 0 in D5/D6 bitmap cluts are inferred, not documented.

### 3.3 16bpp screen format: stale sprites and wrong label colours

- **Symptom:** after clicking through the menu, part of the "Συνέχιση περιπέτειας" sign stayed drawn over the notice board, and the bottom labels were bright red instead of brown.
- **Where it happens:** only when Director renders at **32bpp**. The OpenGL backend, which is what the web build uses, offers ABGR8888 first. SurfaceSDL offers RGB565 and renders correctly.
  - Reproduce natively with `gfx_mode=opengl` against `gfx_mode=surfacesdl`.
  - Forcing a window resize does *not* clear the remnant, so it's in Director's own surface, not the backend.
- **Fix (workaround):** `engines/director/director.cpp`. When `true_color` is on and the game is `forestia`, Director picks the first 16bpp entry from `getSupportedFormats()`. Scripts still see `colorDepth = 32`.
- **Still unknown:** the actual 32bpp bug. It is somewhere in Director's sprite/ink compositing or dirty-rect logic.

### 3.4 Emscripten backend tweaks (first pass)

- **`backends/fs/emscripten/emscripten-fs-factory.cpp`:** always fetches `scummvm.ini` from the page (through `resolveScummUrl`, with cache-busting), overwriting the IndexedDB copy. This makes config changes deploy reliably.
- **`backends/fs/emscripten/http-fs.cpp`:** all data and index fetches go through `resolveScummUrl`, so the player works from a sub-path such as `/forestia-greek-adventure/`.

### 3.5 Things that look like bugs but aren't

- **`Clash in case for match of pattern "data"` warnings and "name clash" spam:** these come from the lower/upper-case symlinks created by `organize_iso_assets.py`. ScummVM is case-insensitive anyway, so the symlinks are unnecessary.
- **`Movie::getCastMember: member 140..143 NOT FOUND in castLib 1`:** appears during boot and seems harmless.

### 3.6 Shape sprites with BackgndTrans ink (fill skip, reverted)

- An earlier pass skipped the interior fill of filled shapes drawn with `kInkTypeBackgndTrans`, to get rid of "solid boxes" over the bottom menu labels and the age buttons.
- That was wrong. Screenshots of the original (French release) show the bottom bar as **filled coloured boxes** with the labels on top (brown-red "Quitter", green "Retour", …). The real causes of the solid boxes were the wrong box colours (§3.9) and the rich-text rendering (§3.10).
- The skip has been **removed**. Filled shapes are drawn normally again. Upstream `inkBlitShape` is unchanged.
- The boxes are member 39 of the internal cast: a filled rectangle with line size 2. The menu uses it with sprite foreColor indexes 142, 67 and 59. On the notice board, the bar behind "Επιλογές" uses index 255 (black). Without a reference screenshot of that screen, it is not confirmed that a black bar is what the original showed.

### 3.7 BitmapCastMember default palette fallback (`clutId == 0`)

- **Symptom:** Bitmaps without explicit custom palettes (`clutId == 0`), such as the main menu forest backdrop (`FORET`, member 132 of castLib 8), were decoded against `macPalette` instead of their movie's default palette (`P.MIDI`, member 501 of castLib 2), causing cyan and magenta psychedelic noise.
- **Root cause:**
  1. `BitmapCastMember` parsed `clutId <= 0` as `CastMemberID(clutId - 1, -1)`. For `clutId == 0`, this mapped to `kClutSystemMac` (`CastMemberID(-1, -1)`).
  2. In `BitmapCastMember::getDitherImg()`, when `castPaletteId` was null or `<= 0`, it fell back to `currentPaletteId`. Because previous score frames set palettes during transitions or fades, `currentPaletteId` pointed to Mac System palette instead of the movie's default palette.
- **Fix:** In `engines/director/castmember/bitmap.cpp`, map `clutId == 0` to `CastMemberID(0, 0)`. In `getDitherImg()` and `isModified()`, when `castPaletteId` is null or `member <= 0`, fall back to `_cast->_defaultPalette` (if `member > 0`) or `movie->_defaultPalette` before falling back to `currentPaletteId`.

### 3.8 Lingo builtin return value in `the result` and 2-argument `addAt()`

- **Symptom:** In the adventure setup menu (`sommaire` -> "Εκκίνηση περιπέτειας" -> Frame 71 of `FRST.dxr`), entering a player name and clicking an age option ("7/9 χρονών" or "+9 χρονών") did nothing, leaving the player stuck on the menu.
- **Root cause:**
  1. On clicking an age button, `BehaviorScript 12 - OK nom` runs `nouveaujoueur2()`, which calls `initList()` -> `initordrepartie()`.
  2. In `initordrepartie()`, the list of game scenes is populated via:
     ```lingo
     repeat with q = 1 to count(list)
       getAt(list, q)
       if the result <> 0 then
         addAt(List2, the result)
       end if
     end repeat
     getAt(List2, 1)
     ```
  3. In `engines/director/lingo/lingo-code.cpp` (`LC::call`), when a builtin was called as a statement (`!allowRetVal`), ScummVM popped the returned value from the stack and logged `warning("Builtin '%s' dropping return value...", ...)`, but **never stored it into `g_lingo->_theResult`** (unlike user-defined handlers in `Lingo::popContext()`). Because `the result` remained `VOID`, `if the result <> 0` was always false.
  4. Furthermore, `addAt(List2, the result)` was called with 2 arguments (intending to append to `List2`). ScummVM declared `addAt` with `minArgs = 3`, dropping all 2-argument calls with an argument mismatch warning.
  5. As a result, `List2` remained empty (`[]`), causing `getAt(List2, 1)` to fail with an uncaught `b_getAt: index out of bounds (1 of 0)!` error, aborting the Lingo call stack and preventing `go("film")` from ever executing.
- **Fix:**
  1. In `engines/director/lingo/lingo-code.cpp`, assign `g_lingo->_theResult = extra` when dropping a non-void builtin return value (`!allowRetVal`).
  2. In `engines/director/lingo/lingo-builtins.cpp`, allow `addAt` to accept 2 to 3 arguments (`minArgs = 2`); when called with 2 arguments (`addAt(list, val)`), append the value to the list.

### 3.9 Sprite/shape colour indices: use the movie's default palette

- **Symptom:** The bottom menu boxes had the wrong colours (maroon, magenta and orange), and they changed depending on when the frame was decoded. At times only their outlines were visible.
- **Root cause:**
  - In true colour, `DirectorEngine::transformColor()` converts a palette index to RGB using `_currentPalette` **at the time the frame is decoded**.
  - Forestia's palette channel switches to "System – Mac" for long stretches (`fading palette to member -1 … over 494 frames`).
  - So index 142 became Mac colour `#630030` instead of `#A52D18` from the movie palette P.MIDI (member 501 of castLib 2).
  - At "thousands of colours" Director doesn't apply the palette channel to colour indices. The original's screenshots match P.MIDI exactly: brown-red 142, green 67.
- **Fix:**
  - `engines/director/graphics.cpp` (`transformColor`): when `_paletteIndependentColors` is set, indices are resolved against the current movie's default palette (falling back to the cast's default palette, then to the old behaviour).
  - `director.cpp`: the flag is set together with the 16bpp preference, for `forestia` only.

### 3.10 Anti-aliased rich text: alpha blending instead of a white halo

- **Symptom:** All rich-text labels had white/grey speckles around the glyphs. This affected the notice board instructions, the bottom menu labels and the age buttons.
- **Root cause:**
  - RTE2 is an anti-aliased coverage map.
  - Earlier, `RichTextCastMember::createWidget()` had been changed to always use the version pre-blended against the member's white background. For `BackgndTrans` ink, exact white was then keyed out, but the half-blended edge pixels stayed.
  - The plain version (`_picture`) can't be used directly, because the widget surface has no alpha. Its transparent pixels become solid text colour, which caused the earlier "black boxes" over the age buttons.
- **Fix:**
  - For `BackgndTrans`/`Matte`/`Blend`/`Transparent` inks in true colour (`Blend` is used by the intro title "Η μεγάλη περιπέτεια", which showed in a white box), the widget is built from the plain glyph colours, and an 8-bit coverage mask is kept (`RichTextCastMember::_alphaMask`, scaled like the widget).
  - `Channel::getPlotData()` passes it as `DirectorPlotData::srfAlpha`.
  - The new `DirectorPlotData::inkBlitAlpha()` blends source over destination per pixel. It also respects a sprite blend amount.
  - 8-bit mode and `Copy` ink keep the old path.

### 3.11 RTE2 decoder: end-of-line marker after a full line

- **Symptom:** Some rich-text images were striped and cut off. The clearest case is "χρονών" under "+9" on the notice board: every other line was empty and the bottom of the text was missing.
- **Root cause:**
  - In `RTE2::createSurface()` (`engines/director/rte.cpp`), lines are terminated by `0x00 0x00`.
  - When a line's runs fill the whole width, the encoder still writes that marker. ScummVM read it as an empty *next* line, so everything after it moved down by one line.
  - An offline re-decode of every RTE2 chunk on the disc found **~60 affected images**: 16 in FTEXTES, 20 in FALB_3, 4 in FALB_2, 2 in BAJ and 2 in GENEFIN, among others. With the fix, every chunk decodes to exactly its byte length.
- **Fix:** after a line has been filled without an explicit end-of-line, consume a directly following `0x00 0x00`. A zero-length run of 0 never occurs otherwise, so this is unambiguous.
- **Upstream:** this one is a clean candidate.

### 3.12 Film loop members with castLib −1 (the hand cursor)

- **Symptom:** The game's animated hand cursor never appeared. This is film loop member 66 of castLib 19 (CURS), puppeted to follow the mouse. The log showed `No source surface … castType: 11 (script), castId: member 11 of castLib -1`.
- **Root cause:**
  - The film loop's score stores castLib −1 for members that live in the film loop's own cast library.
  - Together with the §3.1 mapping of −1 to `DEFAULT_CAST_LIB`, those members resolved to unrelated script members of the internal cast.
- **Fix:** `FilmLoopCastMember::getSubChannels()` (`castmember/filmloop.cpp`) rewrites castLib −1 to the film loop's own `_castLibID` before resolving the member.

---

### 3.13 Palette fades froze the game (help screen after Sam's introduction)

- **Symptom:** after Sam's introduction the game seemed frozen when it should hand over control. It was actually showing the help screen at about **one frame every 10 seconds**, so clicks were almost never handled. The intro also took far longer than needed.
- **Root cause:**
  - `Score::renderPrePaletteCycle()` performs a "normal" palette transition as a **blocking loop** (draw, delay, repeat) of up to several seconds.
  - Most of the game runs with a second movie in a window (`CRTL.Dxr`) next to the stage. The two scores use different palettes (System Mac from the frame vs. the cached System Win), and `DirectorEngine::_lastPalette` is shared, so each score sees a palette change on **every frame** and starts the fade again.
  - A gdb sample showed all the time spent in `renderPrePaletteCycle → DirectorEngine::draw`.
- **Fix:** in `score.cpp`, when `_paletteIndependentColors` is set (Forestia, true colour), a normal palette transition switches immediately instead of fading. At thousands of colours Director doesn't animate palette switches anyway. Fades to black/white are unchanged.
- **Follow-up:** making `_lastPalette` per window would be the proper upstream fix.

### 3.14 Paletted bitmaps in true colour: puppet palette is global, no re-dither churn

- **Symptom:** the map (`plan`, member 5 of the `MEC` cast, tagged with palette P.MATIN, member 509) showed with a pink parchment instead of beige.
- **Root cause:**
  - The game shows the map with `puppetPalette "P.PLAN"` (member 519). Upstream already renders paletted bitmaps through the puppet palette in true colour, but only if the **current movie's** score has the puppet flag. The flag is per score, so whether it applies depends on which window's context the handler ran in.
  - `BitmapCastMember::isModified()` compared the dithering key with the score palette. Because of §3.13 that changes every frame, so every bitmap was re-dithered every frame (a large CPU cost, especially in the browser).
- **Fix (`castmember/bitmap.cpp`, Forestia/true colour only):**
  - New `getTrueColorPuppetPalette()` returns the global `_lastPuppetPalette` while the stage's or the current movie's score has a puppet palette set.
  - The dithering key (`_ditheredTargetClut`) is the puppet palette if one is active, otherwise the bitmap's own palette, in both `getDitherImg()` and `isModified()`.
- Verified by showing `F_231` frame `PLAN` with and without `puppetPalette "P.PLAN"` (debugger REPL).

### 3.15 Known gap: speech cue points (`isPastCuePoint`, `sound(n)`)

- Sam's and Papychêne's lip-sync uses the Shared handler `wait`, which loops on a labelled frame until `IsPastCuePoint(sound(4), label)` while `soundBusy(4)`.
- ScummVM has no `sound(n)` function form (the call fails with "Call to undefined handler 'sound'"), and `isPastCuePoint` is a stub. The failing call aborts the handler, so the animation simply plays on without waiting for the speech. The game progresses, but lip-sync may drift.
- Implementing this needs AIFF `MARK` chunk parsing and cue tracking for `sound playFile` channels. It must be done carefully: a stub that returns 0 would turn the handler into an endless loop.

## 4. The web port

The live site is `web/` served from GitHub Pages, with the game data added at deploy time.

| File | Role |
|---|---|
| `web/index.html` | Custom player page. Details in §4.1 |
| `web/scummvm.js` | Emscripten glue, **post-processed** by `tools/patch_scummvm_js.py` (§4.2) |
| `web/scummvm.wasm` | The ScummVM build (Director engine only, about 15 MB) |
| `web/scummvm.ini` | Pre-seeded config: target `forestia-win-el`, `true_color=true`, `language=el`, `path=/data/games/forestia`, warnings off |
| `web/data/` | ScummVM support files (themes, `encoding.dat`, `macgui.dat`, `classicmacfonts.dat` …) plus `index.json`. `data/games/forestia/` is added by CI and git-ignored |
| `web/manifest.json` | PWA manifest: fullscreen, landscape, `start_url=index.html`. Used by "Add to Home Screen" |
| `web/scummvm.html` | Stock ScummVM shell, unused but harmless |

### 4.1 `index.html` features

**Boot and caching:**
- The splash screen has a Play button. The engine script is only loaded on click.
- `Module.arguments = ['forestia-win-el']` boots straight into the game, skipping the launcher.
- `resolveScummUrl()` resolves every URL relative to the page. `scummvm.ini` gets `?v=BUILD` appended.
- `const BUILD = '2026…'` is appended to the wasm/js/ini URLs. **Bump it on every engine or config change**, otherwise browsers keep stale builds. It is also shown in the footer.

**Audio unlock:**
- `unlockAudio()` creates the `AudioContext` *synchronously inside the Play click*, plays a 1-sample silent buffer, and assigns it to `Module.SDL3.audioContext`. SDL3 reuses an existing context.
- It keeps resuming on later pointer/touch/key events, and also when the tab becomes visible again (`visibilitychange`, `focus`, `pageshow`) or the mouse moves.
- Why this matters: browsers suspend the context in background tabs. The game waits on its sound channels, so until audio runs again the score doesn't advance. The in-game hand cursor then stopped following the mouse after a tab switch until the next click.
- Without this, Safari/iOS keeps the context suspended. SDL3 only auto-resumes on browsers without `navigator.userActivation`.

**Canvas size sync:**
- SDL only re-measures the canvas on a window `resize` event.
- The page compares `canvas.width/height` with the on-screen size × `devicePixelRatio` whenever the canvas resizes (ResizeObserver), its attributes change (MutationObserver) or the device rotates. On a mismatch it dispatches a synthetic `resize`.
- Without this, the picture was stretched on phones; for example a 1560×1080 drawing buffer shown in a 385×289 box.

**Mobile layout:**
- Triggered by `@media (pointer: coarse), (max-width: 820px), (max-height: 560px)`.
- Header and footer are hidden, and `#game-container` is `position: fixed; inset: 0; height: 100dvh` with notch safe-area padding.
- ScummVM letterboxes the 4:3 picture itself, so it is never stretched.
- `touch-action: none`, no pinch-zoom, `overscroll-behavior: none`.
- The `visualViewport` resize handler keeps the game above the iOS keyboard.

**Controls (touch devices only):** buttons at the top right.
- **⌨ keyboard:** focuses a hidden `<input id="kbd-input">` so the phone keyboard opens. Typed text is forwarded to the game as synthetic `keydown`/`keypress`/`keyup` events dispatched on the canvas.
  - Real key events from the field are stopped from reaching SDL directly.
  - Android IMEs report keyCode 229 and no key name, so typed text is diffed on `input` events instead.
  - A 4-space sentinel in the field makes Backspace detectable when the field looks empty.
  - Upper-case letters get explicit Shift down/up events, because SDL tracks Shift itself.
  - Supported characters: Latin letters, digits, space and `- . , ' = ; /`, plus Backspace, Enter and arrow keys. Shifted symbols and non-Latin characters are dropped.
- **⛶ fullscreen:** element fullscreen plus `screen.orientation.lock('landscape')`. Android only; iPhone Safari has no element fullscreen.

### 4.2 `tools/patch_scummvm_js.py`

Run this on **every freshly built `scummvm.js`**. It is idempotent, and its output is byte-identical to the deployed file.

1. Prepends a `globalThis.resolveScummUrl` helper.
2. Keeps the `Module.arguments` set by the page instead of resetting them. The URL `#hash` still overrides.
3. **Key-handler de-duplication.**
   - SDL3's Emscripten backend registered its `keydown`/`keyup`/`keypress` listeners on `window` **6 times** without removing the old ones.
   - Every key press therefore reached the game 6 times ("pppppaaaaaa").
   - The patch removes existing handlers for the same target and event type inside `registerKeyEventCallback` before adding a new one.
   - Verify with the CDP `DOMDebugger.getEventListeners` check in §7. Expect exactly 1 `keydown` listener on `window`.

---

## 5. Building

The Linux workspace layout:

```
game-archeology/Forestia/
├── Forestia-Greek.ISO, iso_contents/    original disc + extracted tree
├── scummvm/                             ScummVM source with the patch applied (in-tree = emscripten config)
├── forestia-greek-adventure/            THIS repo
├── ProjectorRays/, decompiled_*/        decompiler + outputs
└── scratch/                             old experiments, logs, screenshots
```

### 5.1 Native (Linux)

Use an out-of-tree build, so it doesn't clash with the in-tree Emscripten configuration:

```bash
mkdir -p /tmp/native && cd /tmp/native
../path/to/scummvm/configure --disable-all-engines --enable-engine=director --disable-debug --enable-release-mode
make -j$(nproc)           # a few minutes on 4 cores
strip -o forestia-greek-adventure/bin/scummvm scummvm     # bin/ is git-ignored
./run_forestia.sh /path/to/iso_contents
```

### 5.2 WebAssembly

- **Toolchain:** emsdk **4.0.10**, at `scummvm/dists/emscripten/emsdk-4.0.10/`. ScummVM's `dists/emscripten/build.sh` downloads it.
- **Backend:** SDL3 from Emscripten ports, OpenGL ES2/WebGL1, Asyncify.
- **Configure** (once, in-tree):
  ```bash
  cd scummvm
  source dists/emscripten/emsdk-4.0.10/emsdk_env.sh
  ./configure --host=wasm32-unknown-emscripten --build=wasm32-unknown-emscripten --disable-all-engines --enable-engine=director
  ```
- **Build** (incremental builds take about 1.5 minutes):
  ```bash
  emmake make -j4 scummvm.html
  ```
- **Install into the repo:**
  ```bash
  cp scummvm.wasm ../forestia-greek-adventure/web/
  cp scummvm.js   ../forestia-greek-adventure/web/
  python3 ../forestia-greek-adventure/tools/patch_scummvm_js.py ../forestia-greek-adventure/web/scummvm.js
  ```
- **Then:** bump `BUILD` in `web/index.html`.

**Codec libraries:** none are compiled in (no zlib, mad, vorbis, flac, png, jpeg, freetype). Forestia doesn't need them: its audio is plain AIFF and its movies are protected, not Afterburner-compressed. A different Director game may need them; use `dists/emscripten/build.sh` in that case.

### 5.3 Local web test site

```bash
S=/tmp/site; mkdir -p $S/data/games/forestia
cp -r forestia-greek-adventure/web/* $S/
# hard-link the real files (no case symlinks needed)
(cd iso_contents && find . -type d -not -type l -exec mkdir -p "$S/data/games/forestia/{}" \; \
   && find . -type f -exec ln {} "$S/data/games/forestia/{}" \;)
python3 forestia-greek-adventure/tools/build-make_http_index.py $S/data
python3 -m http.server -d $S 8000
```

---

## 6. Deployment

The workflow is `.github/workflows/deploy-pages.yml` ("Deploy Web Player to GitHub Pages"). It runs on every push to `master`, or manually.

1. Checks out the repo.
2. Downloads `forestia_game_data.zip` from the GitHub release **`v1.0.0-preservation`**. Copyrighted game data is kept out of git.
3. Unzips it into `web/data/games/forestia`.
4. Runs `organize_iso_assets.py`, which creates case symlinks. These are not needed by ScummVM; see §8.
5. Runs `build-make_http_index.py web/data` to write the `index.json` files that ScummVM's HTTP filesystem reads.
6. Uploads `web/` as the Pages artifact and deploys. It takes about 5 minutes.

- **Live site:** <https://plympe.com/forestia-greek-adventure/>, mirror <https://panlybero.github.io/forestia-greek-adventure/>.
- **Check the deploy:** `curl -s https://plympe.com/forestia-greek-adventure/index.html | grep -o 'build [0-9a-z]*'`.
- The release also contains `scummvm-forestia-linux-x86_64.tar.gz` and the patch from the first pass. **These predate the palette, 16bpp and keyboard fixes** (§8).

---

## 7. Testing & debugging toolkit

### 7.1 Scripts in `tools/dev/`

- **`web_smoke_test.py`:** headless Chromium (Playwright) test against `--site <dir>` or `--url <live>`, optionally with `--phone 844x390`. It taps through the intro and prints audio statistics (AudioContext state, callbacks, non-silent buffers, peak level) and canvas size checks. Screenshots go to `/tmp/forestia_shot_N.png`.
  - **Expect:** `state: running` and `contexts: 1`. `nonSilent > 0` from about 45 s.
  - **Expect:** `buffer == css_x_dpr`.
- **`native_xvfb_run.sh <bin> <gamedir> [scummvm args]`:** runs the native build under Xvfb, clicks through to the menu, opens the notice board and types `Panos7`, taking screenshots along the way.
  - `GFX=opengl|surfacesdl` and `TRUE_COLOR=true|false` let you compare renderers.
  - Needs `Xvfb`, `xdotool` and ImageMagick.

### 7.2 Useful ScummVM debug flags

Use `--debugflags=<list> -d <level>`; on the web, add them to `Module.arguments`.

| Flag | What you get |
|---|---|
| `images` (2–5) | Palette switches (`setLastPalette`, fades), `BitmapCastMember` info including `palette: member X of castLib Y`, transitions, the chosen pixel format |
| `loading` (3–5) | Cast libraries, registered palettes (`addPalette`), CASt parsing |
| `events` (1) | `Movie::processEvent(): … keycode` once per key event (this is how the 6x key bug was found) |
| `sound` (5) | Channel start/stop, `playSoundChannel` per frame |
| `lingoexec` | Lingo execution trace (very verbose) |

### 7.3 Techniques that paid off

- **Native A/B tests:** run the same flow with `true_color` on/off and `gfx_mode` opengl/surfacesdl, then diff the logs with `grep -v` for timing noise. This is how the 16bpp-vs-32bpp difference was found.
- **Audio in the browser:** wrap `AudioContext.createScriptProcessor` to measure the output peak (see `web_smoke_test.py`). This tells you objectively whether sound is produced.
- **Duplicate listeners:** open a CDP session, call `Runtime.evaluate('window')`, then `DOMDebugger.getEventListeners(objectId)` and count by type.
- **Headless screenshots:** use Playwright's default Chromium launch flags. Forcing `--use-gl=swiftshader` gave stale WebGL screenshots that showed the launcher.
- **Shell pitfall:** `pkill -f "<pattern>"` also kills the shell running it if the pattern appears in its own command line.

---

## 8. Known issues & TODO

**Engine:**
- [ ] Find the real **32bpp rendering bug** (stale sprites and wrong ink colours). The 16bpp preference is a workaround. Once fixed, the upstream patch can drop the `forestia` special case.
- [ ] Confirm what castLib 0 means for D5/D6 bitmap cluts, then upstream §3.2.
- [ ] Check against a reference capture of the original whether the notice board's "Επιλογές" bar really is black (§3.6).
- [ ] Upstream the RTE2 end-of-line fix (§3.11) and the film loop castLib −1 fix (§3.12). Both are game-independent.
- [ ] Implement speech cue points (§3.15) for proper lip-sync.
- [ ] Make `_lastPalette` per window instead of the §3.13 workaround.
- [ ] Upstream the MacGreek code page, the Greek detection entry and the castLib −1 fix.
- [ ] Do a full play-through: mini-games, album, saving and loading, quitting, end credits. Check the unimplemented Xtras (`swastrm`/`swadcmpr` Shockwave Audio, `MIX32`, `SCRNXTRA`) along the way.
- [ ] Find out how save games are stored and whether they persist in the browser across sessions (IndexedDB).
- [ ] The soft keyboard can't produce **Greek characters** or shifted symbols. That's acceptable for names, but it needs engine work for Unicode-to-MacGreek key input.

**Web:**
- [ ] On iPhone/iOS the keyboard and audio fixes are untested on a real device; only emulated Chromium was used. iPhone has no element fullscreen, so "Add to Home Screen" is the alternative.
- [ ] The desktop mouse cursor is drawn on touch devices. Consider hiding it on `pointer: coarse` (ScummVM option or CSS).
- [ ] Report the SDL3 Emscripten duplicate keyboard handler upstream, to SDL or ScummVM.

**Repo / deploy:**
- [ ] Drop the case symlinks from `organize_iso_assets.py` in the Pages pipeline. They cause "name clash" warnings, and the artifact may contain duplicated data.
- [ ] Refresh the release `v1.0.0-preservation` binaries and patch, which predate the fixes in §3.2–3.3.
- [ ] `docs/reverse_engineering_report.md` has slightly different counts (866 vs 658 strings) and says the movies need 8-bit; treat this document as the more recent source.

---

## 9. History of the fixes

| Date | Commit | What |
|---|---|---|
| 2026-10-13 | `91aa7e4`…`c6373b8` | Initial preservation: MacGreek, detection, castLib −1 fix, CD-check bypass, string extraction; WebAssembly player, Pages workflow, splash screen, auto-boot, cache-busting |
| 2026-10-13 | `eb42670` | Palette castLib 0 resolution (fixes blown-out colours); audio unlocked in the Play click; new screenshots |
| 2026-10-13 | `cd5b51a` | Mobile layout (fullscreen 4:3, canvas size sync), ⌨ on-screen keyboard, ⛶ fullscreen, SDL3 key-handler de-dupe (6x typing), 16bpp screen format (stale signpost, label colours), PWA manifest |
| 2026-10-14 | `b31e50b` | Shape sprite BackgndTrans fill skip (fixes solid button overlays and black bars), bitmap clutId == 0 default palette resolution (fixes forest backdrop palette) |
| 2026-10-14 | `b3ad106` | Lingo builtin `the result` preservation and 2-argument `addAt()` support (fixes starting new adventure from age selection menu) |
| 2026-10-14 | `e155c70` | Text/visual pass: reverted the §3.6 fill skip; colour indices resolved against the movie palette (§3.9); alpha-blended rich text (§3.10); RTE2 end-of-line decode fix (§3.11); film loop castLib −1 (§3.12, hand cursor). Web `BUILD` 20261014d |
| 2026-10-14 | | Freeze after Sam's introduction (blocking palette fades, §3.13); map colours / bitmap re-dither churn (§3.14); intro title in a white box (Blend ink, §3.10); audio resumed on tab return (§4.1). Web `BUILD` 20261014e |
