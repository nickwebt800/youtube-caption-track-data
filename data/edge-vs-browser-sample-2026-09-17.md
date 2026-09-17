# Edge fetch vs headless browser — 20 video sample, 2026-09-17

Every row is one real request against a live endpoint
(`GET /api/youtube-transcript?v=<id>`), with the cache bypassed, allowing at most
one headless-browser session per video.

- Edge fetch obtained the caption track: **0 of 20**
- Needed the browser fallback: **20 of 20**
  - 15 came back with one or more caption tracks
  - 5 came back with none (the video genuinely has no caption track)
- Browser time this sample consumed: **79.9 s**, of the 600 s the Cloudflare
  Free plan allows per day (limit quoted from official documentation in
  [`notes/why-edge-fetch-fails.md`](../notes/why-edge-fetch-fails.md))

Machine-readable: [`edge-vs-browser-sample-2026-09-17.csv`](edge-vs-browser-sample-2026-09-17.csv)

## One row per video

| # | video id | result | path used | tracks | watch page | innertube (TVHTML5_SIMPLY_EMBEDDED / ANDROID_VR / WEB) | browser s |
|---|---|---|---|---|---|---|---|
| 1 | jNQXAC9IVRw | tracks found | browser | 2 | 200 LOGIN_REQUIRED | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 3.5 |
| 2 | dQw4w9WgXcQ | tracks found | browser | 6 | 429 | ERROR / 403 / UNPLAYABLE | 3.6 |
| 3 | 9bZkp7q19f0 | tracks found | browser | 1 | 200 LOGIN_REQUIRED | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 3.2 |
| 4 | kJQP7kiw5Fk | tracks found | browser | 6 | 429 | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 3.3 |
| 5 | Ks-_Mh1QhMc | tracks found | browser | 53 | 200 LOGIN_REQUIRED | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 4.0 |
| 6 | d95J8yzvjbQ | tracks found | browser | 10 | 429 | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 2.9 |
| 7 | oOReBkMrTew | tracks found | browser | 1 | 429 | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 4.7 |
| 8 | SG0zIsTtJ7I | tracks found | browser | 1 | 200 LOGIN_REQUIRED | ERROR / LOGIN_REQUIRED / 403 | 5.6 |
| 9 | ZcFF-DMV0pg | tracks found | browser | 2 | 429 | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 7.0 |
| 10 | C9NrfCS6CSc | tracks found | browser | 1 | 429 | ERROR / 403 / 403 | 2.6 |
| 11 | XoUqwa090-M | no caption track | browser | 0 | 429 | 403 / LOGIN_REQUIRED / 403 | 2.5 |
| 12 | SpVkEIgS8iE | no caption track | browser | 0 | 200 LOGIN_REQUIRED | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 4.2 |
| 13 | EgcQspYI4N4 | tracks found | browser | 1 | 200 LOGIN_REQUIRED | 403 / LOGIN_REQUIRED / LOGIN_REQUIRED | 2.8 |
| 14 | KFfpHxZbqbA | no caption track | browser | 0 | 200 LOGIN_REQUIRED | ERROR / 403 / 403 | 3.8 |
| 15 | gP7qSArG_kg | tracks found | browser | 1 | 200 LOGIN_REQUIRED | ERROR / 403 / LOGIN_REQUIRED | 3.1 |
| 16 | NdNNkRehBYI | tracks found | browser | 1 | 200 LOGIN_REQUIRED | 403 / LOGIN_REQUIRED / LOGIN_REQUIRED | 5.9 |
| 17 | -4NUjd6S_fo | tracks found | browser | 1 | 429 | ERROR / LOGIN_REQUIRED / 403 | 4.1 |
| 18 | QehCSIJhkdM | tracks found | browser | 1 | 429 | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 4.7 |
| 19 | SF1ZOrZ2Zxg | no caption track | browser | 0 | 429 | ERROR / LOGIN_REQUIRED / LOGIN_REQUIRED | 5.7 |
| 20 | pbXPqWGGQ5U | no caption track | browser | 0 | 200 LOGIN_REQUIRED | 403 / LOGIN_REQUIRED / LOGIN_REQUIRED | 2.9 |

An empty cell means the request returned nothing usable to parse.

## How the sample was drawn

- 5 videos already measured on the site earlier: lengths 0:19, 4:42 (music),
  4:42 (music), a non-English one, and 21:03.
- 15 video ids pulled live from two YouTube search pages (`full documentary`
  and `tutorial completo`), one headless-browser call per page. None invented.

## What this does and does not show

It shows that, for this account on this day, the cheap path never worked. It
does **not** show that YouTube blocks every server everywhere — the failure is
tied to the egress IP and to whether the request carries a valid proof-of-origin
token. See the notes file for the mechanism.
