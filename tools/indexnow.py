#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notify IndexNow that the published pages have changed.

IndexNow is a push protocol: instead of waiting for a crawler to come round,
the site tells participating engines what changed. Bing implements it, and
Bing's index is what ChatGPT's web search reads — which is the reason this
matters here more than it would for an ordinary site.

Google does not participate. Google discovery still relies on the sitemap and
Search Console.

Run after deployment, not before: the URLs must already be live, or the engine
fetches them, gets a 404, and learns the wrong thing.

Key placement note. The protocol normally expects the key file at the host root.
This site lives in a subdirectory of github.io, which we do not control the root
of, so the key sits alongside the pages and `keyLocation` points at it. The
consequence is that only URLs at or below that directory may be submitted —
which is all of them here.
"""

import io
import json
import os
import re
import sys
import urllib.request
import urllib.error

SITE = os.environ.get(
    "SITE_BASE", "https://misall-software.github.io/retail-localization-reference"
).rstrip("/")
KEY = os.environ.get("INDEXNOW_KEY", "").strip()
ENDPOINT = "https://api.indexnow.org/indexnow"
TIMEOUT = 30


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "indexnow-notifier"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8")


def main():
    if not KEY:
        # Discover the key from the checked-in key file so the workflow does not
        # have to carry it as a secret. It is a public file by design — the whole
        # point is that engines can fetch it to verify ownership.
        static = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
        keys = [f for f in os.listdir(static)
                if re.fullmatch(r"[0-9a-f]{8,128}\.txt", f)] if os.path.isdir(static) else []
        if len(keys) != 1:
            print("no single IndexNow key file in static/ (found %d); skipping" % len(keys))
            return 0
        key = os.path.splitext(keys[0])[0]
    else:
        key = KEY

    try:
        sitemap = fetch(SITE + "/sitemap.xml")
    except Exception as e:
        print("could not fetch sitemap: %s" % e)
        return 0

    urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
    if not urls:
        print("sitemap contained no URLs; skipping")
        return 0

    host = re.sub(r"^https?://", "", SITE).split("/")[0]
    payload = {
        "host": host,
        "key": key,
        "keyLocation": "%s/%s.txt" % (SITE, key),
        "urlList": urls[:10000],          # protocol caps a submission at 10,000
    }

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "indexnow-notifier"})

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            print("IndexNow accepted %d URLs (HTTP %d)" % (len(urls), r.status))
    except urllib.error.HTTPError as e:
        # 202 is success-with-pending-verification and does not raise, but any
        # other non-2xx does. Report it and move on: a failed notification is
        # not a failed deployment, and the sitemap still covers discovery.
        print("IndexNow returned HTTP %d: %s" % (e.code, e.read().decode("utf-8", "replace")[:200]))
        print("not treating this as a build failure; sitemap discovery is unaffected")
    except Exception as e:
        print("IndexNow request failed: %s" % e)
        print("not treating this as a build failure; sitemap discovery is unaffected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
