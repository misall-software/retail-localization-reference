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
| Peru | PE | PEN — `S/` | IGV 18%; **10.5%** for small food service, stepping to 15% in 2027 | CPE electronic vouchers (SUNAT) | 11 | [en/countries/peru.md](en/countries/peru.md) |
| Philippines | PH | PHP — `₱` | VAT 12% | BIR — **device accreditation required**; EIS | 8 | [en/countries/philippines.md](en/countries/philippines.md) |
| South Africa | ZA | ZAR — `R` | VAT 15% | SARS; no retail clearance mandate identified | 7 | [en/countries/south-africa.md](en/countries/south-africa.md) |
| Thailand | TH | THB — `฿` | VAT 7% — **decree expires 2026-09-30**, extension approved but not confirmed gazetted | Voluntary e-Tax Invoice (Revenue Department) | 6 | [en/countries/thailand.md](en/countries/thailand.md) |
| Vietnam | VN | VND — `₫` | VAT 8% — **expires 2026-12-31** | Cash-register e-invoice (Ministry of Finance) | 10 | [en/countries/vietnam.md](en/countries/vietnam.md) |

### Rates with an expiry date

Three of these are temporary rates with a known change date. A system with the
rate compiled in produces silently wrong tax the day after, so they are worth
tracking separately.

**Last re-checked: 2026-08-20.** No change to any of the three rates below.
Thailand's decree is still unenacted, Vietnam's resolution still ends on
2026-12-31 with no successor reported, and Peru's food service figures are
unchanged and were confirmed against SUNAT's own pages. The same pass did find
that Peru's **standard** 18% is now composed differently — 15.5% IGV + 2.5% IPM
rather than 16% + 2%, under Ley N.º 32387 — with the 18% total unaffected. See
[Peru → Correction](en/countries/peru.md#correction-the-18-is-right-its-components-are-not).

| Country | Rate | Changes on | Becomes | Scope |
| --- | --- | --- | --- | --- |
| Thailand | 7% | 2026-09-30 | **7% to 2027-09-30 if the decree is gazetted; otherwise 10% statutory** | All supplies |
| Vietnam | 8% | 2026-12-31 | 10% standard, unless extended | All supplies, minus excluded sectors |
| Peru | 10.5% | 2026-12-31 | **15%** — a scheduled step, *not* a return to 18% | **Food service only** — micro and small restaurants, hotels and tourist lodging. See [Peru → Food service](en/countries/peru.md#food-service). |

Two cautions this table exists to carry:

**Thailand's extension is approved but not enacted.** Cabinet approved a further
year on 2026-07-27 and the Revenue Department issued a confirming notice on
2026-08-02, but the operative instrument is a royal decree and no gazetted decree
covering 2026-10-01 onward has been confirmed here. The two preceding decrees
were gazetted on 2024-09-20 and 2025-09-14, so the answer should exist by
mid-September 2026. Treat the extension as expected, not as in force.

**Peru's rate steps rather than lapses.** The common failure is to treat 2027 as
a return to the standard 18%. It is not — the scheduled 2027 value is 15%
(12% IGV + 3% IPM). Peru's is also the only segment rate on this list: it depends
on what kind of business is operating, not on what is being sold, so it cannot be
configured by attaching a rate to menu items.

## Language index

Organised by rendering problem rather than by language, because most of the 23
interface languages share one of a small number of engineering problems and only
a few have one of their own.

| File | Covers | Primary engineering concern |
| --- | --- | --- |
| [Arabic](en/languages/arabic.md) | `ar` | Right-to-left layout, bidirectional algorithm, contextual shaping, printer code pages |
| [Hebrew](en/languages/hebrew.md) | `he` | Right-to-left **without** shaping; **legacy encodings disagree on visual versus logical byte order**, so text prints reversed rather than garbled |
| [CJK](en/languages/cjk.md) | `zh` `ja` `ko` | **Full-width characters occupy two columns**; multi-byte character mode; ROM font coverage |
| [Thai](en/languages/thai.md) | `th` | **No spaces between words**, so wrapping needs a dictionary; marks stack up to four levels; collation is not codepoint order |
| [Vietnamese](en/languages/vietnamese.md) | `vi` | Two diacritics on one vowel; **no single-byte code page covers it fully**, including CP1258 |
| [Cyrillic](en/languages/cyrillic.md) | `ru` `uk` `be` `bg` `sr` `mk` `kk` `ky` `tg` `uz` `mn` | **Two live code page traditions and no default**; a dozen letters **visually identical to Latin ones**, so correct-looking data compares unequal |
| [Accented Latin](en/languages/latin-accented.md) | `es` `pt` `fr` `de` `it` `tr` and Nordic | Code page selection and Unicode normalisation — fails **silently**, unlike the others |
| [Indic scripts](en/languages/indic.md) | `hi` `mr` `ne` `bn` `ta` `te` `kn` `ml` `gu` `pa` `or` `si` | **Stored order is not printed order** — a vowel stored after a consonant prints before it, and several codepoints fuse into one glyph. **No code page can express this**, so raster rendering is the only route |

`id` and `ms` use Latin script with no diacritics in normal commercial use and
need no code page work at all.

Four of these files sort the same way on the underlying problem: **measure
display width, not character count**. Arabic, Hebrew, Thai and CJK each break
column alignment for a different reason and are fixed by the same change.

**Arabic and Hebrew are the pair worth reading together.** Both are right-to-left
and share the whole bidirectional-algorithm section, but Hebrew is non-cursive —
no shaping, no positional forms, no mandatory ligature — which makes plain
code-page printing viable where Arabic effectively requires raster rendering. A
team porting from an Arabic deployment reliably carries over machinery Hebrew
does not need, and misses the one problem Arabic does not have: Hebrew's legacy
encodings disagree about whether bytes are stored in reading order or printing
order, so the failure mode is text that is *reversed* rather than garbled, and
reversed Hebrew still looks like Hebrew to a reviewer who cannot read it.

**Cyrillic is the one whose failures are not in the print path.** Two of the three
problems in that file — letters that are homoglyphs of Latin ones, and a codepoint
order that files `Ё` first and `ё` last in a Russian product list — happen in the
database and in the back office, and a sample receipt looks perfect while both are
present. It is also the only file here where the printer can be *encoding*
correctly and still be wrong: UAX #11 classes exactly the 33 Russian letters as
Ambiguous width, so a CJK-derived ROM font may print them double-width while the
Ukrainian and Kazakh letters beside them stay single-width.

**Planned:** Indic scripts.

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
