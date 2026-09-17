# YouTube caption track data (2026)

First-hand measurements of what it actually takes to read a YouTube video's
caption track from outside YouTube, taken in September 2026.

Most writing about this topic describes the API surface. This repository
measures it: how often a plain server-side fetch works, what YouTube's own
transcript panel hands you when you copy out of it, and how big the resulting
files are. Every number here is a measurement with a date and a method, or it
is quoted from official documentation with a link. Nothing is estimated.

Measured on [instascript.app](https://instascript.app), a browser-based
transcript tool that reads the caption track a video already has.

## Headline numbers

| Question | Answer | Source |
|---|---|---|
| How often does a plain edge (server-side) fetch get the caption track? | **0 of 20** videos sampled | [`data/edge-vs-browser-sample-2026-09-17.csv`](data/edge-vs-browser-sample-2026-09-17.csv) |
| How many needed a real headless browser as a fallback? | **20 of 20** | same file |
| What does YouTube's own panel give you when you copy a 21:03 talk? | **22,478 characters** with timestamps on, **20,100** with them off | [`data/transcript-panel-copy-size.csv`](data/transcript-panel-copy-size.csv) |
| How big is that 21:03 track as a file? | **23,528 bytes** TXT, **34,976 bytes** SRT | [`data/caption-file-sizes.csv`](data/caption-file-sizes.csv) |

## What is in here

```
data/
  edge-vs-browser-sample-2026-09-17.csv   20 videos, per-video fetch outcome
  edge-vs-browser-sample-2026-09-17.md    same sample, readable, with method
  transcript-panel-copy-size.csv          clipboard size with timestamps on/off
  caption-file-sizes.csv                  TXT vs SRT byte sizes per video
notes/
  why-edge-fetch-fails.md                 what the servers answered, and why
scripts/
  measure_panel_copy.py                   the script that produced the copy sizes
```

## Why this exists

If you are building anything that reads YouTube captions — a transcript tool, a
subtitle downloader, a research scraper — the interesting question is not
"which endpoint", it is "how often does the cheap path work". In this sample the
cheap path worked zero times out of twenty, and the fallback cost about four
seconds of headless-browser time per video.

That is the kind of number you want before you design around an assumption.

## Caveats, stated up front

- **One sample, one day, one account.** 20 videos on 2026-09-17, from one
  Cloudflare Free account, from one region. Not a global measurement.
- **Single run per data point.** No repeats, so no variance is reported.
- **YouTube changes this surface without announcing it.** Re-measure before you
  rely on any of it.
- The 0:19 row in `caption-file-sizes.csv` carries a video id that could not be
  re-confirmed through the API on 2026-09-18 (the lookup answered 503). It is
  the id used in the test runs that produced those bytes.

## Licence

CC0 1.0 Universal (public domain dedication) — see [`LICENSE`](LICENSE).
