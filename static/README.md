# static/

Files here are copied verbatim to the site root at build time. Drop a file in,
push, and it appears at `https://misall-software.github.io/retail-localization-reference/<filename>`.

This exists for search engine ownership verification, which is what allows a
sitemap to be submitted directly. Direct submission — not an inbound link — is
what gets a new site crawled.

## What goes here

| Purpose | File | Where to get it |
| --- | --- | --- |
| Google Search Console | `google<hash>.html` | Search Console → Add property → URL prefix → HTML file |
| Bing Webmaster Tools | `BingSiteAuth.xml` | Bing Webmaster → Add site → XML file |
| IndexNow | `<key>.txt` containing the key | Generate at bing.com/indexnow |

Google Search Console also accepts a `<meta name="google-site-verification">`
tag instead of a file. That route needs a change to the page template in
`tools/build_site.py`, so the file method is simpler here.

## Note on the property type

Use a **URL prefix** property, not a Domain property. Domain verification needs
a DNS record, and the domain is `github.io`, which is not yours. URL prefix
verification against
`https://misall-software.github.io/retail-localization-reference/` works with the
file method and covers everything under that path.

## After verifying

Submit the sitemap: `sitemap.xml` (relative to the property root).

_Maintained by the MISAll team. Last updated: 2026-08_
