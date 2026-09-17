# Why the cheap path fails, and what the fallback costs

Status: first-hand observation, 2026-09-17, plus two numbers quoted from
official documentation. Where a sentence is inference rather than measurement it
says so.

## 1. The watch page answers, but the player refuses

`GET https://www.youtube.com/watch?v=<id>` from a Cloudflare Worker returned one
of two things across the 20-video sample:

- **HTTP 200 with `LOGIN_REQUIRED` inside the player response** — the HTML is
  served, but the player object says the viewer must sign in. 12 of 20 videos.
- **HTTP 429** — no page at all. 8 of 20 videos.

`LOGIN_REQUIRED` from a datacentre egress IP is what YouTube returns when it
does not want to serve that IP a playable player. The 429s look like rate
limiting of the same egress range, which is shared across many Workers customers.

## 2. The InnerTube clients do not rescue it

Three clients were tried per video — `TVHTML5_SIMPLY_EMBEDDED_PLAYER`,
`ANDROID_VR` and `WEB`. Across all 20 videos and all 60 calls, **zero** caption
tracks came back. The answers were `LOGIN_REQUIRED`, `ERROR`, `403` or
`UNPLAYABLE`. Full grid in
[`../data/edge-vs-browser-sample-2026-09-17.csv`](../data/edge-vs-browser-sample-2026-09-17.csv).

## 3. Even with a signed caption URL, the text itself needs a browser-minted token

This is the part that surprises people. Getting the *list* of caption tracks is
one problem; fetching the *text* is a second one.

The signed caption URL can be obtained server-side. Requesting it from the edge
returns **HTTP 200 with a zero-byte body**. The same URL fetched from a real
browser, with a `pot=` parameter (proof-of-origin token) minted in that browser,
returns the expected ~683 bytes.

Observed directly:

| Who fetches it | URL | Result |
|---|---|---|
| Edge fetch | plain caption URL | 200, 0 bytes |
| Edge fetch | signed URL + a token minted elsewhere | 200, 0 bytes |
| Visitor's browser | signed URL + token minted in that browser | 200, 683 bytes |

*Inference, with the reasoning:* the token is bound to the specific signed URL
and to the browser instance that minted it, so a server cannot mint one on a
visitor's behalf and reuse it. That conclusion comes from the three rows above,
not from documentation — YouTube does not publish this.

## 4. What the fallback costs, on the free tier

The fallback used here is a headless-browser REST call. Numbers below are quoted
from Cloudflare's official documentation, read on 2026-09-17:

| Figure | Value | Source |
|---|---|---|
| Free plan browser time | **10 minutes per day** (per day, not per month) | <https://developers.cloudflare.com/browser-run/limits/> |
| Browser session timeout | **60 s** idle, extendable to 10 min with keep-alive | same page |
| Quick Actions rate limit, Free | **1 request / 10 seconds** | same page |
| Concurrent browsers, Free | 3 per account | same page |
| Paid plan | US$5/month, includes 10 browser hours, then **US$0.09 per browser hour** | <https://developers.cloudflare.com/browser-run/pricing/> |
| Overage behaviour on Free | **HTTP 429, stops for the day, no charge** — a Free plan has no payment method | limits page, troubleshooting section |

Two derived figures, with the arithmetic shown:

- **Measured cost per call:** 79.9 s ÷ 20 videos = **4.0 s per video**
  (79.9 s is the sum of the `browser_seconds` column in the sample CSV).
- **Daily capacity on Free:** 600 s ÷ 4.0 s = **about 150 new videos per day**.
  600 s is the documented free allowance; 4.0 s is the measured mean above.
  This assumes no cache hits — caching a result removes the cost entirely.

## 5. One trap worth writing down

A 429 from the browser API is **not always** the daily limit. In testing, two
calls in quick succession returned 429 and a single call 12 seconds later
returned 200 — that was the 1-request-per-10-seconds rate limit, not an
exhausted day. Treating every 429 as "out of quota for the day" will take a
working service down for hours over a transient throttle.

## 6. What none of this proves

It does not prove that every server is blocked. A residential IP, a different
egress region, or a full visitor-data and cookie flow may behave differently, and
none of those were tested here. What is shown is what one Cloudflare Free
account saw on one day across 20 videos.
