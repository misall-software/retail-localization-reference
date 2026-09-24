# Khmer, Lao and Burmese — Receipt Layout and Printing

**None of these three scripts has a legacy code page. Not one, on any platform,
in any of the code page families.** Thai has three entries in Microsoft's code
page list, Vietnamese has one and the Indic scripts have ten ISCII pages between
them; Khmer, Lao and Burmese have none. There is no byte encoding to select, no
wrong one to diagnose, and no fallback if the Unicode path is not finished.
Unicode plus raster rendering is the route, and it is the whole route.

Burmese adds a second problem that has no equivalent anywhere else in this
repository: **a widely deployed alternative use of the same code points**, called
Zawgyi, which produces well-formed UTF-8 that a Unicode renderer draws as
something else. Nothing in the byte stream says which convention applies.

The three are grouped here because Unicode groups them:
[UAX #14](https://www.unicode.org/reports/tr14/) assigns Khmer, Lao and Myanmar
the same line break class as Thai — `SA`, complex-context dependent, meaning
break opportunities cannot be found from character properties and require
dictionary lookup. Everything the [Thai file](thai.md) says about wrapping
applies unchanged to all three, and is not repeated here.

They are **not** interchangeable below that. The most useful finding in this file
is that they split two ways on how text is stored, and the split is not
geographic: Lao behaves like Thai, while Khmer and Burmese behave like
Devanagari.

> ### Verification status
>
> The code point behaviour below was checked against the Unicode Character
> Database rather than against a description of it, using the UCD as distributed
> with CPython (version 13.0.0). Line break classes are read from UAX #14
> (revision 55, 2025-09-05). The absence of code pages is read from Microsoft's
> published code page list. Cluster code point and byte counts were measured.
>
> Everything about printers, fonts on target devices, market conventions and
> anything with a legal character is unverified.
>
> **Open items — `TODO: verify`**
>
> 1. Whether the target printer has a ROM font for any of these three scripts.
>    The expectation is that it does not, but the file does not assert it.
> 2. Whether any code page on the target printer claims to reach these scripts,
>    and what it actually contains.
> 3. The printer's raster image command and its maximum image width in dots.
> 4. Which shaping engine the POS hardware provides, and whether the shaping
>    tables for these scripts are present on the till rather than only on the
>    development machine.
> 5. Whether supplier and staff-entered Burmese data is Zawgyi, Unicode, or both
>    mixed in one column.
> 6. Whether native digits or Western digits are expected on a printed receipt in
>    each market, and whether that is convention or requirement.
> 7. How the Myanmar kyat is written on a printed price, given that Unicode
>    encodes no sign for it.
> 8. Every tax, invoicing and receipt-content rule in all three countries. **This
>    collection has no country file for Cambodia, Laos or Myanmar**, so none of
>    it has been researched. See section 9.

---

## 1. There is no code page, for any of the three

A code page maps a byte value to a glyph in printer ROM. For a script where that
mechanism can work, one exists: Thai has `windows-874`, `x-mac-thai` and an IBM
EBCDIC Thai page; Vietnamese has `windows-1258`; the Indic scripts have ten ISCII
pages at 57002–57011, covering nine scripts between them. Microsoft's published
list of code page identifiers contains **no entry for Khmer, Lao or Burmese** —
not a Windows ANSI page, not an OEM page, not a Macintosh page, not an EBCDIC
page. Neither does ISO/IEC 8859, which has no part for any of them.

Two consequences worth separating.

**For Khmer and Burmese this is expected**, for the reason the
[Indic file](indic.md) sets out at length: a code page cannot express a script
whose glyphs are formed from context. The mechanism could not reach these scripts
even if a page had been assigned to them.

**For Lao it is not expected, and it is the more useful fact.** Lao is
structurally close to Thai — a base consonant, marks above and below, pre-posed
vowels stored in visual order, no conjunct formation. A single-byte code page
would work for Lao about as well as `windows-874` works for Thai. None was ever
standardised. So Lao is the case where the engineering is straightforward, the
legacy route is absent anyway, and a plan that assumes "we did Thai, Lao is the
same job" is half right in a way that costs the wrong half.

**What this means in practice.** The receipt path is Unicode text, shaped and
rendered to a bitmap on the till, then sent to the printer as an image. This is a
decision to make at the start of a project, because it is answered by the
printer's raster capability and speed rather than by its font list, and because
the printer is usually already bought by the time anyone prints a real product
name.

It also removes a diagnosis. Elsewhere in this repository, text that prints as
the wrong letters usually means the wrong code page was selected. Here there is
no code page to select, so the same symptom means something else — a missing
font, a shaping engine that is not present on the device, or, in Burmese, the
subject of the next section.

## 2. Burmese: two conventions, one set of code points

Zawgyi is a font-and-input convention that uses code points from the Myanmar
block (U+1000–U+109F) with meanings that differ from the Unicode standard's. It
was in wide use before Unicode-conformant Burmese support was generally
available, and text created under it is still in circulation.

The properties that make this an operational problem rather than a historical
note:

**Both are valid UTF-8, and both decode without error.** There is no invalid byte
sequence, no decoder exception, no replacement character. A string can be stored,
indexed, transmitted and re-read with perfect fidelity and still render as the
wrong words.

**Nothing in the data declares which convention applies.** Not the encoding
label, not the character set header, not the database column type — all of them
correctly say UTF-8 for both. The distinction lives in the reader's font, which
is not part of the data.

**Detection is statistical, not deterministic.** Google's
[myanmar-tools](https://github.com/google/myanmar-tools) uses a trained model
rather than hand-written rules, and states the reason: rule-based detectors flag
genuine Unicode text in Shan and Mon as Zawgyi, because those languages
legitimately use code points that Zawgyi reuses. The Myanmar block does carry
letters for those languages — U+1050 to U+105F alone holds Pali, Sanskrit and Mon
letters, verified against the UCD — so a shop with Shan-speaking staff is exactly
the case a naive detector gets wrong. Detection returns a probability. Treat it
as one.

**Conversion rules have a standards home.** The Zawgyi–Unicode transliteration
rules are published in CLDR, and myanmar-tools states that its conversion follows
them. myanmar-tools itself states that it is not an official Google product;
CLDR is the Unicode Consortium's own publication. Cite each at its own level.

**The failure is silent in both directions.** Zawgyi bytes rendered by a Unicode
font, or Unicode bytes rendered by a Zawgyi font, both produce Burmese-looking
output with wrong letters — not boxes, not question marks. A reviewer who does
not read Burmese sees a normal receipt. This is the same trap the
[Hebrew file](hebrew.md) documents for reversed text and the
[Thai file](thai.md) documents for clipped tone marks, and it is worse here,
because the wrong text is stored rather than only displayed.

**Where it enters a POS system.** Not usually through the software. Through the
product catalogue: a spreadsheet from a supplier, a list typed by a member of
staff on their own phone, a menu carried over from a previous system. Decide at
import time — detect, convert, record which convention the source used — rather
than at print time, when the same column holds both and no single answer is
right.

`TODO: verify` which convention the specific data in a specific deployment uses.
That is a question about one shop's data, not about Myanmar.

## 3. Stored order versus printed order: the split that matters

A pre-posed vowel is written to the left of the consonant it follows
phonetically. All four scripts in this group have them. **They do not store them
the same way**, and the difference decides whether the first character of a
string is the first thing printed.

Checked against the UCD, the general category is the tell:

| Script | Pre-posed vowel | Category | Stored | Renderer reorders? |
| --- | --- | --- | --- | --- |
| Thai | U+0E40–U+0E44 | `Lo` | Before the consonant, as written | No |
| Lao | U+0EC0–U+0EC4 | `Lo` | Before the consonant, as written | No |
| Khmer | U+17C1–U+17C3 | `Mc` | After the consonant | **Yes** |
| Burmese | U+1031 | `Mc` | After the consonant | **Yes** |

`Lo` is a letter: an independent character that stands on its own. `Mc` is a
spacing combining mark: it attaches to a base and has no meaning without one.

**Lao and Thai store what you see.** The vowel is a letter, it comes first in the
string, it prints first. No reordering happens at render time.

**Khmer and Burmese store the logical order and reorder at render time**, exactly
as the Brahmic scripts in the [Indic file](indic.md) do. Measured: Burmese
`U+1000 U+1031` is two code points and six UTF-8 bytes, and prints with the
second code point to the left of the first.

Four practical consequences, all of which follow from the table rather than from
the language:

- **Truncating a Khmer or Burmese product name at a code point boundary can
  remove the base and leave the mark**, which then attaches to whatever follows
  or renders on a dotted circle. Truncate on grapheme cluster boundaries
  ([UAX #29](https://www.unicode.org/reports/tr29/)).
- **Cursor movement and backspace** in a name-entry field move through stored
  order, which for Khmer and Burmese is not the order on screen.
- **Sorting by code point is wrong for all four**, but for different reasons — in
  Lao and Thai because the pre-posed vowel sorts first when it should sort under
  the consonant, in Khmer and Burmese because of the mark ordering within the
  cluster. Use an ICU collation for the locale. This never appears on a receipt
  and costs staff time at the counter every shift.
- **A team porting from a working Thai deployment gets Lao's rendering for free
  and none of Khmer's or Burmese's.** A team porting from a working Devanagari
  deployment gets the reordering machinery for Khmer and Burmese and still has
  Zawgyi ahead of it. Neither port is the small job it looks like.

Normalisation is not a lever here. NFC and NFD were applied to sample clusters in
all four scripts and changed nothing: these are not composed forms with
alternative spellings. The "normalise and compare" fix that resolves the accented
Latin and Indic search problems has nothing to act on.

## 4. Khmer stacks downward, and the stacking character is invisible

Khmer builds a cluster by placing subscript consonants **below** the base. The
character that requests this is U+17D2 KHMER SIGN COENG — category `Mn`,
canonical combining class 9, the same class as the viramas in the Indic file. It
has no glyph of its own: it is an instruction, and the shaping engine consumes
it.

Measured:

| Cluster | Code points | UTF-8 bytes | Prints as |
| --- | --- | --- | --- |
| `U+179F U+17D2 U+178F` | 3 | 9 | one base with one consonant beneath it |
| `U+179F U+17D2 U+178F U+17D2 U+179A` | 5 | 15 | one base with two beneath it |
| `U+1781 U+17D2 U+1789 U+17BB U+17C6` | 5 | 15 | one stack, one column wide |

The rules that follow are ones the rest of this repository states for other
reasons, arriving here by a different route:

**Column arithmetic on string length over-counts badly.** Five code points, one
column. Padding computed from string length drifts on real Khmer product names
while looking correct on ASCII test data.

**Line height must accommodate a downward stack as well as an upward one.** The
[Thai file](thai.md) warns about clipping tone marks at the top; Khmer clips
subscript consonants at the bottom, and a clipped subscript is a different word
rather than a cosmetic defect.

**A sanitiser that strips non-printing characters destroys Khmer text.** U+17D2
looks like a format character and is load-bearing. The same warning applies to
U+200B ZERO WIDTH SPACE, which Khmer text uses to mark word boundaries for line
breaking precisely because ordinary spaces are not used between words — strip it
and the wrapping information goes with it. Both survive a visual review of the
string, because neither was ever visible.

Khmer also has two-part vowels, verified as `Mc`: U+17C4 and U+17C5 render
material on both sides of the base consonant, so no single position in the
printed line corresponds to the vowel. Unlike the Bengali and Odia two-part
vowels in the Indic file, these have **no canonical decomposition** — NFD leaves
them unchanged — so there is no normalisation step that exposes the two halves.

## 5. Digits, punctuation and currency

**Each script has its own digits**, and the Myanmar script has two sets:

| Script | Digits | Range |
| --- | --- | --- |
| Khmer | ០១២៣៤៥៦៧៨៩ | U+17E0–U+17E9 |
| Lao | ໐໑໒໓໔໕໖໗໘໙ | U+0ED0–U+0ED9 |
| Myanmar | ၀၁၂၃၄၅၆၇၈၉ | U+1040–U+1049 |
| Shan | ႐႑႒႓႔႕႖႗႘႙ | U+1090–U+1099 |

All are category `Nd`. The Shan set exists because the Myanmar script is written
by more than one language, and a Shan-speaking area is a plausible deployment.
Whether native or Western digits belong on a printed receipt is a market question
rather than a code question: make it a template setting, never mix forms on one
document, and `TODO: verify` the local expectation.

**One homoglyph is worth naming.** U+1040 MYANMAR DIGIT ZERO and U+101D MYANMAR
LETTER WA are distinct code points — one `Nd`, one `Lo`, verified — and are
conventionally described as looking alike, closely enough that the letter gets
substituted for the digit in typed data. A numeric field that validates by
character class rejects it; a field that does not, stores a letter where a digit
belongs and produces a quantity or a phone number that will not match anything.
Whether a given font actually renders the two identically is a font question:
`TODO: verify` on the target device.

**Currency signs exist for two of the three, and not for the third.** A search of
every currency symbol in the UCD returns U+17DB KHMER CURRENCY SYMBOL RIEL and
U+20AD KIP SIGN, alongside U+0E3F for the baht and U+20AB for the dong. **There
is no sign for the Myanmar kyat** — no code point in Unicode carries that name. A
price template that expects a symbol per currency has nothing to put in the
Myanmar slot, and the decision — a Latin abbreviation, the Burmese word, or the
ISO code — is a market convention this file has not verified.

Cambodia is also commonly described as circulating US dollars alongside riel in
retail. That would have direct consequences for a till — two currencies at one
counter, change given in a different currency from the price, a rate somebody has
to maintain — but it is a country-file question about money handling and tax, and
**there is no Cambodia country file here**. Recorded as an open item, not
answered.

## 6. Line breaking

All four scripts are line break class `SA` in UAX #14, defined there as
complex-context dependent: runs of these characters require morphological
analysis to determine break opportunities, and where such analysis is unavailable
the report recommends treating them as alphabetic. Treating them as alphabetic
means the only breaks found are the emergency ones — which on a 32- or 42-column
receipt means breaking mid-word on every long name.

ICU provides dictionaries for exactly this, and its documentation names the
languages: "ICU provides dictionary support for word boundaries in Chinese,
Japanese, Thai, Lao, Khmer and Burmese", with use "automatic when text in one of
the dictionary languages is encountered". All three scripts in this file are on
that list.

Two things this does not resolve:

**Raster rendering does not fix wrapping.** Wrapping happens before rendering. A
raster path with no dictionary breaks in the wrong places and then renders the
wrong breaks perfectly. The [Thai file](thai.md) makes the same point; it is the
one place where the raster answer is incomplete for all four scripts.

**Verify the dictionaries are on the till.** The dictionary is data that ships
with the ICU build, and a trimmed-down ICU on an embedded Android device is a
normal way to save space. `TODO: verify` on the target hardware, not on the
development machine.

## 7. Test matrix

Print on the target hardware. Have the output read by someone who reads the
language — not by someone who recognises the script.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | A Khmer word with two subscript consonants | Both stack beneath the base, neither clipped at the bottom |
| 2 | A Burmese word with a pre-posed vowel (U+1031) | The vowel prints to the **left** of its consonant |
| 3 | A Khmer word with U+17C4 | Vowel material appears on both sides of the base |
| 4 | A Burmese syllable with stacked medials | One cluster, no dotted circles |
| 5 | A product name truncated to fit a column | A whole cluster disappears; no orphaned mark, no dotted circle |
| 6 | A product name long enough to wrap | The break falls between words, not inside one |
| 7 | Three item lines of differing name lengths | Amount decimal points align vertically |
| 8 | A full-paper-width line of local text | Reaches the paper edge, right side not cut |
| 9 | ៛ (U+17DB) and ₭ (U+20AD) in a price | A glyph, not a box |
| 10 | A Myanmar price using the local kyat convention | Matches whatever open item 7 resolved to |
| 11 | Known-Zawgyi text imported into the catalogue | Detected and converted, or rejected — never stored unmarked |
| 12 | A Burmese quantity field containing U+101D | Rejected as non-numeric, not stored as a zero |
| 13 | A product list sorted alphabetically | Order matches what a local speaker expects |
| 14 | A Shan-language product name | Not misdetected as Zawgyi and "corrected" |
| 15 | Reprint of a stored transaction | Identical to the original |
| 16 | **Every test above, on the till that will be sold** | Same result as the demonstration machine |

Tests 2, 5, 11, 12 and 14 fail in ways that look correct to a reviewer who does
not read the language. Test 14 exists because the fix for Zawgyi is itself
capable of corrupting good data.

## 8. Which markets this covers

Cambodia (`km`), Laos (`lo`) and Myanmar (`my`), plus Shan and Mon within
Myanmar, which share the Myanmar script and are the reason Zawgyi detection needs
care.

The usual deployment shape for these markets is the one the Arabic, Cyrillic and
Indic files also describe: **the back office runs in one language and the
customer-facing receipt prints in another.** An owner-operator may run the
management screens in Chinese or English while every printed receipt is in the
local script, and the two paths have different failure modes. A screen with a
missing font shows boxes and gets reported the same day; a receipt with a missing
font is looked at by the customer and thrown away.

## 9. What this file does not cover

**There is no country file for Cambodia, Laos or Myanmar in this collection.**
Nothing here has been checked against any of their tax rules, invoice content
requirements, fiscal device rules or e-invoicing mandates, because none of it has
been researched. Specifically unresearched: consumption tax rates and whether
prices are displayed inclusive of tax; mandatory receipt fields; taxpayer
identifier formats; whether any authority accredits or registers POS devices;
cash rounding; and Cambodia's dual-currency handling at the counter.

This file covers text rendering. Anything with a legal character needs a local
accountant, and this file is not a substitute for one.

## Notes for POS implementers

**Budget for raster rendering from the start.** There is no code page for any of
these three, so this is not a fallback chosen after a font search fails. Size the
project on the printer's image throughput.

**Treat Burmese text as being of unknown convention until proven otherwise.**
Detect and normalise at import, record what the source was, and do not assume a
column holds one convention throughout.

**Do not let the Thai deployment set the estimate.** Lao inherits Thai's
rendering solution and none of its code page; Khmer and Burmese inherit neither.

**Truncate on grapheme clusters, and measure display width rather than code point
count.** The same rule as Arabic, CJK, Thai and the Indic scripts, arrived at here
through subscript stacking and mark reordering.

**Never strip invisible characters from product names.** U+17D2 carries Khmer
stacking and U+200B carries Khmer word boundaries. Both look like noise.

**Check the till, not the laptop.** Fonts and ICU dictionaries are the two things
routinely absent from cheap Android POS hardware and present on every development
machine.

---

## Update, 2026-09-24 — Cambodia now has a country file

Sections 5 and 9 above say there is no Cambodia country file. There is one now:
[Cambodia](../countries/cambodia.md). Those sections are left as written, and
this note records what changed.

Two things it establishes bear directly on this file, both from secondary
sources and `TODO: verify` there:

- **Khmer is required on invoices, with any foreign language below it** — GDT
  Instruction No. 1127 (2016), restated in Notification No. 3218 (2020). Combined
  with section 1 of this file — no code page for Khmer on any platform — this
  makes raster rendering a legal requirement in practice, not an engineering
  preference, for any invoice a Cambodian POS prints.
- **Dual-currency handling at the counter** (item SEA-11) is now addressed in the
  country file, including the NBC-rate riel disclosure on the invoice total.

Laos and Myanmar still have no country file, and nothing in section 9 has changed
for them.

_Last updated: 2026-09_

---

_Maintained by the MISAll team. Last updated: 2026-08_
