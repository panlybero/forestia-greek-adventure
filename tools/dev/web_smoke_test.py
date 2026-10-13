#!/usr/bin/env python3
"""
Headless smoke test for the Forestia web player (Playwright + Chromium).

Clicks "Play", keeps tapping through the intro, and every ~15 s prints:
  * audio stats  - AudioContext state, number of ScriptProcessor callbacks,
                   how many output buffers were non-silent and the peak level
  * canvas sizes - drawing-buffer size vs on-screen CSS size x devicePixelRatio
                   (they must match or the picture is stretched)
and saves a screenshot.

Usage:
  # serve a local site directory (web/ + data/games/forestia + index.json files)
  python3 tools/dev/web_smoke_test.py --site /path/to/site
  # or test the live deployment
  python3 tools/dev/web_smoke_test.py --url https://plympe.com/forestia-greek-adventure/
  # emulate a phone in landscape
  python3 tools/dev/web_smoke_test.py --url ... --phone 844x390

Requires: pip install playwright && playwright install chromium
"""
import argparse
import asyncio
import http.server
import json
import socketserver
import threading
import time

from playwright.async_api import async_playwright

AUDIO_HOOK = """
(() => {
  window.__audio = {callbacks: 0, nonSilent: 0, peak: 0, contexts: 0};
  const Orig = window.AudioContext || window.webkitAudioContext;
  if (!Orig) return;
  const Wrapped = function(...a) {
    const ctx = new Orig(...a);
    window.__audio.contexts++;
    window.__ctx = ctx;
    const origCSP = ctx.createScriptProcessor.bind(ctx);
    ctx.createScriptProcessor = function(...b) {
      const node = origCSP(...b);
      let handler = null;
      Object.defineProperty(node, 'onaudioprocess', {
        set(h) {
          handler = h;
          node.addEventListener('audioprocess', (e) => {
            handler(e);
            const s = window.__audio; s.callbacks++;
            const d = e.outputBuffer.getChannelData(0);
            let m = 0; for (let i = 0; i < d.length; i++) { const v = Math.abs(d[i]); if (v > m) m = v; }
            if (m > 0.001) s.nonSilent++;
            if (m > s.peak) s.peak = m;
          });
        },
        get() { return handler; }
      });
      return node;
    };
    return ctx;
  };
  window.AudioContext = Wrapped;
  window.webkitAudioContext = Wrapped;
})();
"""

PROBE = """() => {
  const c = document.getElementById('canvas');
  const r = c.getBoundingClientRect();
  const d = window.devicePixelRatio || 1;
  return {
    audio: Object.assign({}, window.__audio, {state: window.__ctx && window.__ctx.state}),
    canvas: {buffer: [c.width, c.height], css_x_dpr: [Math.round(r.width * d), Math.round(r.height * d)]},
  };
}"""


def serve(directory, port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=directory, **k)

        def log_message(self, *a):
            pass

    class Server(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
        daemon_threads = True

    httpd = Server(('127.0.0.1', port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return f'http://127.0.0.1:{port}/index.html'


async def run(args):
    url = args.url or serve(args.site, args.port)
    t0 = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=['--autoplay-policy=document-user-activation-required'])
        if args.phone:
            w, h = map(int, args.phone.split('x'))
            ctx = await browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2,
                                            is_mobile=True, has_touch=True)
        else:
            ctx = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await ctx.new_page()
        await page.add_init_script(AUDIO_HOOK)
        page.on('pageerror', lambda e: print('PAGEERROR', e, flush=True))
        if args.verbose:
            page.on('console', lambda m: print('console:', m.text[:200], flush=True))
        await page.goto(url)
        vp = page.viewport_size
        if args.phone:
            await page.tap('#start-btn')
        else:
            await page.click('#start-btn')
        n = 0
        while time.time() - t0 < args.duration:
            await asyncio.sleep(10)
            if args.phone:
                await page.touchscreen.tap(vp['width'] // 2, vp['height'] // 2)
            else:
                await page.mouse.click(vp['width'] // 2, vp['height'] // 2 + 20)
            await asyncio.sleep(5)
            info = await page.evaluate(PROBE)
            print(f'{round(time.time() - t0):4d}s', json.dumps(info), flush=True)
            await page.screenshot(path=f'{args.out}_{n}.png')
            n += 1
        await browser.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument('--site', help='local site directory to serve')
    src.add_argument('--url', help='URL of a deployed player')
    ap.add_argument('--port', type=int, default=8931)
    ap.add_argument('--duration', type=int, default=90, help='seconds to run (default 90)')
    ap.add_argument('--phone', help='emulate a touch phone, e.g. 844x390 (landscape) or 390x844')
    ap.add_argument('--out', default='/tmp/forestia_shot', help='screenshot path prefix')
    ap.add_argument('--verbose', action='store_true', help='print browser console output')
    asyncio.run(run(ap.parse_args()))
