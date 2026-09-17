#!/usr/bin/env python3
"""Measure what YouTube's own transcript panel puts on the clipboard.

Opens a video, expands the description, opens the transcript panel, selects the
whole segment list and reports the character count -- once with timestamps on and
once with them off (via the panel's own "Toggle timestamps" item).

This is the script that produced transcript-panel-copy-size.csv.

Requirements:
    pip install playwright && playwright install chromium

Usage:
    python measure_panel_copy.py VIDEO_ID [--chrome PATH] [--port 9333]

Notes:
  * Run against a logged-out browser profile; sign-in state changes what the
    panel shows.
  * The panel does not always open on the same caption track between visits.
    If you need a fixed track, re-run until the footer shows the one you want.
"""

import argparse
import os
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

OPEN_PANEL = """async () => {
  let btn = null;
  document.querySelectorAll('*').forEach(el => {
    if (!btn && el.children.length === 0) {
      const t = (el.textContent || '').trim();
      if (/^show transcript$/i.test(t)) btn = el;
    }
  });
  if (!btn) return 'not found';
  (btn.closest('button') || btn.closest('yt-button-shape') || btn).click();
  return 'clicked';
}"""

EXPAND_DESCRIPTION = """() => {
  const ex = document.querySelector('ytd-text-inline-expander #expand, #description-inline-expander #expand');
  if (ex) ex.click();
  return !!ex;
}"""

FOOTER = """() => {
  const tr = document.querySelector('ytd-transcript-renderer');
  if (!tr) return null;
  const foot = tr.querySelector('#footer') || tr;
  return foot.innerText.replace(/\\s+/g, ' ').slice(0, 120);
}"""

SELECT_ALL = """() => {
  const list = document.querySelector('ytd-transcript-segment-list-renderer');
  if (!list) return null;
  const range = document.createRange();
  range.selectNodeContents(list);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
  const txt = sel.toString();
  return {length: txt.length, head: txt.slice(0, 120).replace(/\\n/g, ' | ')};
}"""

TOGGLE_TIMESTAMPS = """async () => {
  const tr = document.querySelector('ytd-transcript-renderer');
  if (!tr) return 'no panel';
  const panel = tr.closest('ytd-engagement-panel-section-list-renderer') || tr;
  const more = Array.from(panel.querySelectorAll('button'))
    .find(b => /more actions/i.test(b.getAttribute('aria-label') || ''));
  if (!more) return 'no more-actions button';
  more.click();
  await new Promise(r => setTimeout(r, 3500));
  const pop = document.querySelector('ytd-menu-popup-renderer');
  if (!pop) return 'no popup';
  const item = Array.from(pop.querySelectorAll('tp-yt-paper-item, ytd-menu-service-item-renderer'))
    .find(e => /toggle timestamps/i.test(e.innerText || ''));
  if (!item) return 'no toggle item; menu said: ' + pop.innerText.replace(/\\s+/g, ' ').slice(0, 120);
  item.click();
  await new Promise(r => setTimeout(r, 3000));
  return 'toggled';
}"""


def wait_for_cdp(port, seconds=45):
    for _ in range(seconds):
        time.sleep(1)
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/json/version" % port, timeout=3).read()
            return True
        except Exception:
            pass
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("--chrome", default=os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"))
    ap.add_argument("--port", type=int, default=9333)
    ap.add_argument("--profile", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".chrome-profile"))
    args = ap.parse_args()

    env = dict(os.environ)
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "all_proxy", "ALL_PROXY"):
        env.pop(k, None)  # a local proxy breaks the CDP connection to 127.0.0.1

    proc = subprocess.Popen(
        [args.chrome, "--remote-debugging-port=%d" % args.port, "--user-data-dir=" + args.profile,
         "--no-first-run", "--no-default-browser-check", "--window-size=1400,1000", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
    )
    try:
        if not wait_for_cdp(args.port):
            sys.exit("chrome never came up on port %d" % args.port)

        with sync_playwright() as pw:
            b = pw.chromium.connect_over_cdp("http://127.0.0.1:%d" % args.port)
            p = b.contexts[0].new_page()
            url = "https://www.youtube.com/watch?v=%s&hl=en&gl=US" % args.video_id
            p.goto(url, wait_until="domcontentloaded", timeout=120000)
            time.sleep(8)
            p.evaluate("() => window.scrollTo(0, 400)")
            time.sleep(2)
            print("expanded description:", p.evaluate(EXPAND_DESCRIPTION), flush=True)
            time.sleep(3)
            print("open panel:", p.evaluate(OPEN_PANEL), flush=True)
            time.sleep(8)
            print("footer:", p.evaluate(FOOTER), flush=True)
            print("timestamps ON :", p.evaluate(SELECT_ALL), flush=True)
            print("toggle:", p.evaluate(TOGGLE_TIMESTAMPS), flush=True)
            time.sleep(3)
            print("timestamps OFF:", p.evaluate(SELECT_ALL), flush=True)
            p.close()
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
