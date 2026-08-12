# Retail & POS Localization Reference

Field notes on what a point-of-sale system has to get right in a specific country
or a specific language: currency formatting, tax display, receipt content
requirements, script direction, and printer behaviour.

Each country file follows the same section order, so the same question
("what goes on a receipt in X?") lands in the same place in every file.

**This repository is published in two editions.** They are written separately,
not translated from one another.

| Edition | Directory | Written for |
| --- | --- | --- |
| English | [`en/`](en/) | Implementers. Facts, specifications, and the requirements a system has to satisfy. |
| Chinese | [`zh/`](zh/README.md) | Shop owners opening a store abroad. What to watch out for when choosing and running a till system in that country. |

The Chinese edition covers material the English edition does not — bilingual
staffing setups, local connectivity in practice, payment habits at the counter —
and is not a translation of these files. This README describes the English
edition; the Chinese edition has its own index at [`zh/README.md`](zh/README.md).

---

## What this repository is

- A working reference for people implementing or localizing retail software
  (POS, inventory, e-invoicing integration) in markets outside their own.
- Organised for lookup, not for reading front to back.
- Explicit about what has been confirmed and what has not.

## What this repository is not

- Not tax advice, legal advice, or a compliance certification.
- Not a substitute for the primary source. Tax rates, invoice thresholds and
  mandatory receipt fields change, and they change without notice to software
  vendors. Every such value here points at the authority that governs it so you
  can check it yourself.
- Not a product manual.

---

## How to read the source-type tags

Every factual field in a table carries one of three tags. The tag tells you
**what class of source governs the fact**, which is also where you go to confirm it.

| Tag | Meaning | What to do with it |
| --- | --- | --- |
| `official-authority` | The fact is published or administered by a named government body (tax authority, central bank, standards body). The body is named in the file. | Confirm against that body's own publication. |
| `public-regulation` | The fact derives from published law, decree, or regulation. | Confirm against the current text of that instrument, including amendments. |
| `unverified` | Not attributable to either of the above as written here. Treat as unknown. | Confirm before relying on it. Always paired with a `TODO: verify` entry. |

**Repo-wide verification state: unverified draft.** No entry has yet been
re-checked against a primary source. The tags mark *where the fact belongs*, not
that it has been certified. Every file opens with its own list of open
`TODO: verify` items; the same list is available as structured data in
[`data/verification-queue.json`](data/verification-queue.json).

Engineering conventions — thermal paper widths, character-per-line counts,
ESC/POS code pages — are stated in the implementer sections rather than tagged,
because they are hardware behaviour rather than statutory fact. They still carry
inline `TODO: verify` notes where firmware varies between vendors.

---

## Country index

| Country | ISO | Currency | Headline consumption tax | Fiscal / e-invoice system | Open items | File |
| --- | --- | --- | --- | --- | --- | --- |
| Australia | AU | AUD — `$` | GST 10%, flat | None for retail; ATO, tax invoice on request | 5 | [en/countries/australia.md](en/countries/australia.md) |
| Indonesia | ID | IDR — `Rp` | PPN 12% statutory, **11% effective** via base adjustment | e-Faktur (Directorate General of Taxes) | 8 | [en/countries/indonesia.md](en/countries/indonesia.md) |
| Kenya | KE | KES — `KSh` | VAT 16% | eTIMS (Kenya Revenue Authority) | 11 | [en/countries/kenya.md](en/countries/kenya.md) |
| Malaysia | MY | MYR — `RM` | **SST**, not VAT | MyInvois (LHDN), phase 4 live 2026-01 | 8 | [en/countries/malaysia.md](en/countries/malaysia.md) |
| Nigeria | NG | NGN — `₦` | VAT 7.5% | FIRSMBS clearance model (FIRS), phased | 7 | [en/countries/nigeria.md](en/countries/nigeria.md) |
| Peru | PE | PEN — `S/` | IGV 18%; 10% for small food service | CPE electronic vouchers (SUNAT) | 11 | [en/countries/peru.md](en/countries/peru.md) |
| Philippines | PH | PHP — `₱` | VAT 12% | BIR — **device accreditation required**; EIS | 8 | [en/countries/philippines.md](en/countries/philippines.md) |
| South Africa | ZA | ZAR — `R` | VAT 15% | SARS; no retail clearance mandate identified | 7 | [en/countries/south-africa.md](en/countries/south-africa.md) |
| Thailand | TH | THB — `฿` | VAT 7% — **expires 2026-09-30** | Voluntary e-Tax Invoice (Revenue Department) | 6 | [en/countries/thailand.md](en/countries/thailand.md) |
| Vietnam | VN | VND — `₫` | VAT 8% — **expires 2026-12-31** | Cash-register e-invoice (Ministry of Finance) | 10 | [en/countries/vietnam.md](en/countries/vietnam.md) |

### Rates with an expiry date

Three of these are temporary reductions that lapse on a known date. A system with
the rate compiled in produces silently wrong tax the day after, so they are worth
tracking separately:

| Country | Rate | Lapses | Reverts to | Scope |
| --- | --- | --- | --- | --- |
| Thailand | 7% | 2026-09-30 | 10% statutory, unless extended | All supplies |
| Vietnam | 8% | 2026-12-31 | 10% standard, unless extended | All supplies, minus excluded sectors |
| Peru | 10% | 2026-12-31 | 18%, unless extended | **Food service only** — micro and small restaurants, hotels and tourist lodging, subject to income and activity-mix conditions. See [Peru → Food service](en/countries/peru.md#food-service). |

Peru's is the one on this list that is a segment rate rather than a general one:
it depends on what kind of business is operating, not on what is being sold, so
it cannot be configured by attaching a rate to menu items.

## Language index

| Language | Code | Script | Direction | Primary engineering concern | File |
| --- | --- | --- | --- | --- | --- |
| Arabic | `ar` | Arabic | Right-to-left | Bidirectional layout, contextual shaping, printer code pages | [en/languages/arabic.md](en/languages/arabic.md) |

---

## Repository layout

```
retail-localization-reference/
├── README.md           this file — English edition index
├── en/
│   ├── countries/      one file per country, fixed section order
│   └── languages/      one file per language, script and rendering concerns
├── zh/                 Chinese edition, written separately for shop owners
│   ├── README.md
│   ├── countries/
│   └── languages/
└── data/               the same facts as JSON, shared by both editions
```

One file, one language. No file mixes the two.

### Structured data

| File | Contents |
| --- | --- |
| [`data/countries.json`](data/countries.json) | Country records. Each factual field is an object carrying `value` and `source`, plus `todo_verify` where the value is still open. Records link to both editions. |
| [`data/languages.json`](data/languages.json) | Language and script records: direction, digit systems, shaping requirements, printer encoding candidates. |
| [`data/verification-queue.json`](data/verification-queue.json) | Every open `TODO: verify` item across the repository, with the authority or instrument to check it against. |

The JSON deliberately mirrors the Markdown rather than extending it. If the two
disagree, the Markdown file is the one that was edited by a human most recently —
treat the disagreement itself as a bug.

---

## Corrections

Corrections are welcome, and corrections with a citation are welcome most.
When reporting one, include the country or language, the field, the corrected
value, and the primary source — the authority's own page, or the instrument and
article number. A correction that moves a field from `unverified` to
`public-regulation` is as useful as one that changes a number.

## Reuse

Dual-licensed — see [LICENSE](LICENSE):

- **Documentation** (all Markdown, including `en/` and `zh/`) — CC BY 4.0.
  Share and adapt, including commercially, with attribution.
- **Data** (everything under `data/`) — CC0 1.0. Public domain; no attribution
  required, though it is appreciated.

The split is deliberate: the prose is written work, the data is facts. Facts
should not be encumbered.

---

## Who maintains this

Maintained by Guangzhou Miao Software Technology Co., Ltd.
(广州秘奥软件科技有限公司), headquartered in Guangzhou, China.

- **MISAll**, since 2007 — a multi-language POS and inventory system for
  retailers operating outside their home market, localized for 100+ countries,
  23 interface languages and 20+ settlement currencies.
- **MiYaDine**, launched 2024 — a multilingual restaurant POS and ordering
  system for operators abroad.

These notes come out of deployment work: the things that had to be changed
before a till could be handed to a cashier, or an ordering terminal to a
waiter, in that country. Retail notes come from MISAll deployments, food
service notes from MiYaDine.

Product sites:
- MISAll (retail POS) — https://www.misall.com
- MiYaDine (restaurant POS) — https://www.yunw8.com

Last updated: 2026-08
