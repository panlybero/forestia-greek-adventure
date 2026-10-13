#!/usr/bin/env python3
"""
Post-process the Emscripten-generated scummvm.js for the Forestia web player.

Usage: python3 tools/patch_scummvm_js.py path/to/scummvm.js

Applies (idempotently):
  1. resolveScummUrl()  - resolve data/ini URLs relative to the page, so the
                          player works from a sub-path (GitHub Pages project site).
  2. Module.arguments   - keep the arguments set by index.html (auto-boot the game)
                          instead of always resetting them.
  3. Key handler dedupe - SDL3's Emscripten backend registers its keydown/keyup/
                          keypress handlers on `window` several times without
                          removing the old ones, so every key press reached the
                          game ~6 times ("aaaaaa"). Remove previous handlers for
                          the same target/event before registering a new one.
"""
import sys

URL_HELPER = """globalThis.resolveScummUrl = globalThis.resolveScummUrl || function(url) {
  var clean = url.startsWith('/') ? url.substring(1) : url;
  var base = window.location.href;
  if (!base.endsWith('/')) {
    if (base.endsWith('.html') || base.endsWith('.htm')) {
      base = base.substring(0, base.lastIndexOf('/') + 1);
    } else {
      base = base + '/';
    }
  }
  return new URL(clean, base).href;
};
"""

ARGS_ORIG = ('Module["arguments"]=[];if(window.location.hash.length>0){params=decodeURI(window.location.hash.substring(1)).split(" ");'
             'params.forEach(param=>{Module["arguments"].push(param)})}')
ARGS_NEW = ('Module["arguments"]=(Module["arguments"]&&Module["arguments"].length)?Module["arguments"].filter(p=>p&&p.trim().length>0):[];'
            'if(window.location.hash.length>1){Module["arguments"]=decodeURI(window.location.hash.substring(1)).split(" ").filter(p=>p&&p.trim().length>0)}')

KEY_ORIG = 'registerKeyEventCallback=(target,userData,useCapture,callbackfunc,eventTypeId,eventTypeString,targetThread)=>{'
KEY_MARK = '/*forestia-key-dedupe*/'
KEY_NEW = (KEY_ORIG + KEY_MARK +
           '{var __t=findEventTarget(target);for(var __i=0;__i<JSEvents.eventHandlers.length;++__i){'
           'var __h=JSEvents.eventHandlers[__i];if(__h.target==__t&&__h.eventTypeString==eventTypeString){JSEvents._removeHandler(__i--)}}}')


def main(path):
    s = open(path, encoding='utf-8').read()
    changed = []

    if 'globalThis.resolveScummUrl' not in s:
        s = URL_HELPER + s
        changed.append('resolveScummUrl')

    if ARGS_NEW not in s:
        if ARGS_ORIG not in s:
            sys.exit('error: could not find Module["arguments"] initialisation to patch')
        s = s.replace(ARGS_ORIG, ARGS_NEW, 1)
        changed.append('arguments')

    if KEY_MARK not in s:
        if KEY_ORIG not in s:
            sys.exit('error: could not find registerKeyEventCallback to patch')
        s = s.replace(KEY_ORIG, KEY_NEW, 1)
        changed.append('key-dedupe')

    open(path, 'w', encoding='utf-8').write(s)
    print('patched: ' + (', '.join(changed) if changed else 'nothing (already patched)'))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
