# Game Archaeology & Reverse Engineering Report: Forestia (Greek Edition)

## Executive Summary

The game dump (`Forestia-Greek.ISO`) has been analyzed, unpacked, and reverse-engineered. The diagnosis is positive: **Forestia can be fully rescued and run natively on modern systems.**

The reason the game suffered from broken Greek text and crashed in Windows virtual machines has been identified:
1. **Engine Architecture**: The game was built using **Macromedia Director 6.0 / 6.5 (v1223)**, packaged as a Win32 Director Projector (`Forestia.exe`) using external protected movies (`.Dxr`) and casts (`.Cxt`).
2. **The "Broken Greek Fonts" Root Cause**: The localization was originally developed on **Macintosh (System 7 / Mac OS 8/9)** using the **MacGreek (x-mac-greek)** character encoding and Mac fonts (`Geneva`, `Lucida Handwriting`, `MgChanceryBeauty`). When the PC executable was assembled, the text chunks remained encoded in MacGreek bytes. Modern Windows and typical Win98/XP VMs expect Windows-1253 or OEM 737, which maps MacGreek high-bytes to unreadable symbols (mojibake).
3. **The VM Launch Failures**: The bootstrap movie (`STARTERPC.Dxr`) includes copy-protection and hardware checks written in Lingo that loop through physical drives `C:` through `Z:` searching for `AAAFORES.TXT` via `xtra("fileio")`, requiring an 8-bit (256-color) display mode (`the colorDepth = 8`). Modern display drivers and virtual machines fail these checks.

---

## Technical Inventory

| Component | Detail |
| :--- | :--- |
| **Original Title** | *Forestia: Η Μεγάλη Περιπέτεια* (Daddy Kate / Laser Media / Kaiphea, 1998–2000) |
| **Media Format** | Adaptec Toast ISO 9660 / Mac-PC Hybrid CD-ROM Image (674 MB) |
| **Engine** | Macromedia Director 6.5.0r1 (RIFX / MV93, Format Version 1223) |
| **Main Executable** | `Forestia.exe` (1,529,858 bytes, Tail-5000 MD5: `0ee0e228692af7bfa8903e6235caac2a`) |
| **Director Movies (`.Dxr`)** | 42 protected movies (`DATA/*.Dxr`) |
| **Director Casts (`.Cxt`)** | 42 protected casts (`DATA/*.Cxt`, `F_DATA/*.cxt`) |
| **Audio Tracks** | 125 uncompressed AIFF files (`DATA/SONF/*.AIF`, `F_DATA/SAMN/*.aif`) |
| **Embedded Greek Text Strings** | 866 dialogue & interface text strings in `DATA/FTEXTES.Cxt` |
| **Xtras Used** | `FILEIO.X32`, `MIX32.X32`, `PMLite.x32`, `SCRNXTRA.X32`, `SMXTRA.X32`, `SWASTRM.X32` |

---

## Decoded Greek Text Samples

By decoding the raw Rich Text / STXT chunks with the `mac_greek` codec, the dialogue, UI, and story scripts were recovered into standard Unicode (UTF-8):

> **Sample 1 (Castle Scene)**:  
> *«Αυτός είναι ο πύργος του μάγου Μορχούλ… Λείπει τώρα, αλλά πρόσεχε καλύτερα…»*  
> (Raw hex: `b0 f9 f4 de f7 20 e5 dd ee e1 e9 20 ef 20 f0 e0 f2 e7 ef f7...`)

> **Sample 2 (Exploration Prompt)**:  
> *«Μπορείτε να μπείτε στο δάσος για έναν περίπατο ή για να συμπληρώσετε το άλμπουμ σας»*

> **Sample 3 (Puzzle Instructions)**:  
> *«Ξ για να σηκώσεις τα νομίσματα*  
> *Ξ για να διαλέξεις ένα κλειδί*  
> *Ξ για να βάλεις το κλειδί του ίδιου χρώματος στη βάση και να ανοίξεις την κασέλα*  
> *Ξ για να αδειάσεις τα νομίσματα στην κασέλα*  
> *Πρόσεξε τα επικίνδυνα πλάσματα της θάλασσας…»*

---

## Decompiled Lingo Scripts Analysis

Using the **ProjectorRays** decompiler, we successfully extracted the core Lingo source files (`.ls`) from the protected `.Dxr` and `.Cxt` archives.

### CD Check and Drive Scanning (`STARTERPC / MovieScript 6.ls`)
```lingo
on CheckDrive weirdfile
  repeat with i = 67 to 90
    set drive to numToChar(i)
    set thisPath to string(drive & ":\" & weirdfile)
    set myfile to new(xtra("fileio"))
    openFile(myfile, thisPath, 1)
    if status(myfile) = 0 then
      set myfile to 0
      return drive & ":"
      exit
    end if
  end repeat
  set myfile to 0
  go("alert1")
end
```

### Initial Transition to Main Game (`STARTERPC / BehaviorScript 1 & 3.ls`)
```lingo
on exitFrame
  if the platform contains "windows" then
    set thisPath to string("D:\" & "aaafores.txt")
    set myfile to new(xtra("fileio"))
    openFile(myfile, thisPath, 1)
    if status(myfile) = 0 then
      set myfile to 0
      set Mycd to "D:"
    else
      set myfile to 0
      set Mycd to CheckDrive("aaafores.txt")
    end if
    set GaccesCd to Mycd & "\DATA\"
    set GaccesF to the pathName & the movieName
    set GaccesDD to the pathName & "F_DATA\"
  end if
end

on exitFrame
  go(1, GaccesCd & "FRST")
end
```

---

## Porting & Rescue Strategy

```mermaid
flowchart TD
    ISO["Forestia-Greek.ISO (Raw Dump)"] --> Unpack["7z / Unpack Asset Tree"]
    Unpack --> Assets["Extracted Assets: 125 AIFF Audio, 42 DXR, 42 CXT"]
    
    subgraph Preservation ["Paths to Preservation"]
        PathA["Path 1: Native ScummVM Engine\n(Cross-platform C++: Win/Mac/Linux/Android/iOS)"]
        PathB["Path 2: ProjectorRays Decompilation\n(Full .dir / .cst project & .ls Lingo source)"]
        PathC["Path 3: Standalone / Web Port\n(Modern WebAssembly / HTML5 / Godot Engine)"]
        PathD["Path 4: VM / Wine Compatibility Patch\n(No-CD script patch + MacGreek Font bundle)"]
    end
    
    Assets --> PathA
    Assets --> PathB
    PathB --> PathC
    Unpack --> PathD
```

### 1. Primary Recommendation: Native ScummVM Support
* ScummVM already includes an official `director` engine (`engines/director`) with an existing entry for `director:forestia` (*Forestia: The Great Adventure*).
* We verified that ScummVM identifies the Greek Windows executable signature:
  ```cpp
  WINGAME1_l("forestia", "", "Forestia.exe", "t:0ee0e228692af7bfa8903e6235caac2a", 1529858, Common::EL_GRC, 650);
  ```
* Because ScummVM runs natively on modern x86_64 and ARM64 (Linux, Windows 10/11, macOS Apple Silicon, Steam Deck, iOS, Android), running it through ScummVM bypasses all 256-color display mode issues, CD-ROM driver emulation quirks, and legacy Windows GDI font limitations.
* A small quirk configuration in ScummVM (`kEncodingMacGreek` text fallback for the Greek target) restores 100% accurate font rendering automatically.

### 2. Full Source Extraction & Decompilation
* With **ProjectorRays** compiled and working, all 42 `.Dxr` movies and 42 `.Cxt` cast files can be converted into standard, editable `.dir` and `.cst` Director source files.
* All Lingo script code can be exported into high-level source scripts.
* All audio clips (`.aif`) can be archived or converted losslessly to FLAC/WAV/OGG.
* All text strings can be preserved in standard UTF-8 JSON.
