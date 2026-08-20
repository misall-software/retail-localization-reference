# Indic Scripts — Where the Order You Store Is Not the Order That Prints

Every other script in this collection can, at a push, be printed by mapping bytes
to glyphs in a printer's ROM font. Arabic needs shaping, but the shaping is of
one letter at a time. CJK needs two columns per character, but each character is
one glyph. Cyrillic needs the right code page and then behaves.

The Brahmic family — Devanagari, Bengali, Tamil, Telugu, Kannada, Malayalam,
Gujarati, Gurmukhi, Odia, Sinhala — breaks the assumption those approaches rest
on. Here the sequence of codepoints and the sequence of glyphs on the paper are
**different sequences**. A vowel stored after a consonant prints to the left of
it. Three codepoints collapse into one glyph. One vowel sign splits into two
glyphs that land on opposite sides of the letter they belong to.

No code page fixes this, and no printer setting fixes this. Text in these scripts
has to be shaped by software that knows the script's rules and then sent to the
printer **as an image**. A project that budgeted for "add a code page, like we
did for Russian" has budgeted for the wrong thing.

> ### Verification status — unverified draft
>
> The Unicode behaviour described here was checked against the Unicode Character
> Database rather than against a description of it: the general category and
> canonical combining class of every vowel sign and virama named below, the
> canonical decompositions of the nukta letters and the two-part vowels, and the
> composition-exclusion behaviour in section 5. The check used the UCD as
> distributed with CPython, **version 13.0.0**, which is the Unicode Consortium's
> own data rather than a secondary account of it. Codepoint and byte counts were
> measured, not estimated.
>
> The printer behaviour, the market conventions and everything with a legal
> character are **not** verified.
>
> **Open items — `TODO: verify`**
>
> 1. Whether the target printer has a ROM font for the target script at all. The
>    expected answer is no. Confirm it rather than assume it, because a vendor
>    data sheet listing "multilingual support" is not an answer. See section 6.
> 2. Whether any code page on the target printer claims to reach a Brahmic
>    script, what it actually contains, and whether it can form conjuncts.
>    Section 6 argues from the nature of a code page that it cannot; that
>    argument is not a substitute for reading the specific command reference.
> 3. The printer's raster image command, its maximum image width in dots, and
>    whether it can print an image the full width of the paper. This becomes the
>    critical path once section 6 is accepted.
> 4. Which shaping engine the target platform provides, and whether it is present
>    on the specific POS hardware rather than on the development machine.
> 5. Whether the fonts on the target device cover the target script. Absence
>    produces a row of empty boxes, which at least is visible; partial coverage
>    produces a correct-looking line with two wrong syllables, which is not.
> 6. Conventional decimal separator, group separator and symbol position on
>    retail documents in each target market, read from CLDR and confirmed against
>    sample receipts.
> 7. **Whether the target market's digit grouping is the Indian 2-2-3 system or
>    the Western 3-3-3 system**, per market and per document type. See section 8.
> 8. Whether the rupee sign is required, permitted or conventionally replaced by
>    a Latin abbreviation on printed documents in the target market. See
>    section 7.
> 9. Whether the target market imposes any legal requirement on the language or
>    script of a receipt, or on the script in which tax figures appear.
> 10. **Everything about tax.** This collection has no country file for India,
>     Nepal, Sri Lanka or Bangladesh. Nothing here has been checked against GST
>     rules, invoice content rules, or any e-invoicing mandate. See section 11.
> 11. Whether product data arriving from local suppliers contains native-script
>     digits, and whether it is normalised on import. See section 8.
> 12. Whether `ZWJ` and `ZWNJ` survive the path from the supplier's file through
>     the import routine to the database. See section 3.

---

## 1. What this family does not need

Worth stating first, because it narrows the problem.

These scripts are **left to right**. There is no bidirectional algorithm to
implement, none of the Arabic file's questions about which end of the line a
price lands on, and none of the Hebrew file's visual-versus-logical byte order
disaster.

They are **whitespace-separated**. Words are divided by spaces, so line wrapping
can break at spaces the way it does for English. The Thai file's problem — no
spaces, so wrapping needs a dictionary — does not arise here.

They are **single width**. The CJK file's arithmetic, where every character costs
two columns of a 48-column line, does not apply. `TODO: verify` — a printer with
a font derived from a CJK ROM may still render them double-width, the way the
Cyrillic file warns for Russian letters. Confirm by printing.

They have **no case**. No uppercasing, no case-insensitive comparison, none of
the Turkish dotted-i class of bug.

What is left is the hard part, and it is entirely about the relationship between
stored codepoints and printed glyphs.

---

## 2. The vowel that prints to the left of the letter it follows

This is the fact to lead with, because it breaks the mental model rather than
just the output.

Devanagari U+093F DEVANAGARI VOWEL SIGN I is stored **after** the consonant it
modifies and rendered **before** it. Write a consonant followed by U+093F and the
printed result is the vowel sign, then the consonant, in that visual order.

Checked against the UCD, U+093F is:

| Property | Value | What it means here |
| --- | --- | --- |
| General category | `Mc` | Spacing combining mark — it occupies width of its own |
| Canonical combining class | `0` | **Normalisation will not reorder it** |

Both halves matter. Because it is a *spacing* mark it takes horizontal room, so
it is not a diacritic hovering over something else. Because its combining class
is `0`, Unicode normalisation leaves it exactly where it is — the visual
reordering is performed by the **shaping engine**, at render time, and is not
recorded in the stored string at all.

The same behaviour, confirmed at the same two properties:

| Script | Codepoint | Name |
| --- | --- | --- |
| Devanagari | U+093F | DEVANAGARI VOWEL SIGN I |
| Bengali | U+09BF | BENGALI VOWEL SIGN I |
| Tamil | U+0BBF | TAMIL VOWEL SIGN I |
| Sinhala | U+0DD9 | SINHALA VOWEL SIGN KOMBUVA |

The consequence for a POS system: **you cannot determine what will appear at the
start of a printed line by looking at the start of the string.** Any code that
truncates, centres, right-aligns or measures by walking codepoints from one end
is working on a sequence that does not correspond to the paper.

### The two-part vowel

Worse, and also verified against the UCD: some vowel signs decompose into two
marks that render on **opposite sides** of the base consonant.

| Codepoint | Name | Canonical decomposition |
| --- | --- | --- |
| U+09CB | BENGALI VOWEL SIGN O | U+09C7 + U+09BE |
| U+09CC | BENGALI VOWEL SIGN AU | U+09C7 + U+09D7 |
| U+0B4B | ORIYA VOWEL SIGN O | U+0B47 + U+0B3E |
| U+0B4C | ORIYA VOWEL SIGN AU | U+0B47 + U+0B57 |

U+09C7 renders to the left of the base consonant; U+09BE renders to the right.
So one logical vowel becomes two glyphs bracketing the letter. There is no
position in the visual line that "is" that vowel.

---

## 3. Conjuncts: several codepoints, one glyph

A consonant followed by U+094D DEVANAGARI SIGN VIRAMA followed by another
consonant is not three letters. It is one **conjunct** — a single fused glyph,
often bearing no visual resemblance to either of its parts.

The virama is the trigger, and it behaves consistently across the family.
Checked against the UCD, every one of these carries canonical combining class
**9**:

| Script | Codepoint | Name |
| --- | --- | --- |
| Devanagari | U+094D | DEVANAGARI SIGN VIRAMA |
| Bengali | U+09CD | BENGALI SIGN VIRAMA |
| Tamil | U+0BCD | TAMIL SIGN VIRAMA |
| Telugu | U+0C4D | TELUGU SIGN VIRAMA |
| Kannada | U+0CCD | KANNADA SIGN VIRAMA |
| Malayalam | U+0D4D | MALAYALAM SIGN VIRAMA |
| Gurmukhi | U+0A4D | GURMUKHI SIGN VIRAMA |
| Gujarati | U+0ACD | GUJARATI SIGN VIRAMA |
| Odia | U+0B4D | ORIYA SIGN VIRAMA |
| Sinhala | U+0DCA | SINHALA SIGN AL-LAKUNA |

Measured, not estimated:

| Written form | Codepoints | UTF-8 bytes | Glyphs on paper | What a customer calls it |
| --- | --- | --- | --- | --- |
| Devanagari *ksha* | 3 | 9 | 1 | one letter |
| Devanagari *kshmee* | 6 | 18 | 1 | one letter |
| Bengali *bo* | 2 | 6 | parts on both sides | one letter |
| Tamil *ni* | 2 | 6 | 2, vowel first | one letter |

Four different numbers for the same piece of text. A database column sized in
bytes, a display field sized in characters, a receipt line sized in columns and a
shop assistant counting letters will all disagree, and all four are internally
consistent.

**Truncation is where this becomes a defect rather than a curiosity.** Cutting a
product name at codepoint 20 can land between a consonant and its virama. The
result is not a truncated word — it is a *different* word, or a dotted circle
where the renderer signals an incomplete cluster. Truncate on **grapheme cluster
boundaries** (UAX #29), never on codepoints and never on bytes.

### The invisible characters that change the glyph

`ZWNJ` (U+200C) and `ZWJ` (U+200D) control whether a conjunct forms. Inserted
between a virama and the following consonant, `ZWNJ` suppresses the fused form
and leaves the consonants separate with a visible virama; `ZWJ` requests a
half-form. They render as nothing at all.

They are therefore invisible to anyone reviewing a data file, and a sanitiser
that strips "non-printing characters" will remove them and silently change the
printed word. `TODO: verify` — whether they survive the import path from
supplier file to database.

---

## 4. Counting, and what to count

Consolidating sections 2 and 3, because this is the single most common source of
bugs:

- **Bytes** are for storage sizing and for the wire. Nothing else.
- **Codepoints** are for nothing a user sees. `len()` in most languages returns
  this and it is almost always the wrong number.
- **Grapheme clusters** (UAX #29) are what a reader calls characters. Use these
  for truncation, cursor movement and character limits.
- **Rendered width** is what fits on the paper, and for these scripts it is only
  knowable after shaping. It is not a function of any of the three counts above.

A 32-column receipt line has 32 columns. How many codepoints fit in it is not a
constant, not per-script, and not computable without laying out the actual text.

---

## 5. Normalisation makes these strings longer, not shorter

A group of letters can be stored two ways: as one precomposed codepoint, or as a
base consonant plus a nukta mark. Devanagari QA is either U+0958, or U+0915
followed by U+093C. They render identically and compare unequal.

That much is the familiar problem from the Accented Latin file. The twist,
verified against the UCD, is what `NFC` does about it.

These codepoints are on Unicode's **composition exclusion** list. `NFC` therefore
**decomposes** them and does not put them back:

| Precomposed | Name | `NFC` produces |
| --- | --- | --- |
| U+0958 | DEVANAGARI LETTER QA | U+0915 U+093C |
| U+0959 | DEVANAGARI LETTER KHHA | U+0916 U+093C |
| U+095F | DEVANAGARI LETTER YYA | U+092F U+093C |
| U+09DC | BENGALI LETTER RRA | U+09A1 U+09BC |
| U+09DF | BENGALI LETTER YYA | U+09AF U+09BC |
| U+0A33 | GURMUKHI LETTER LLA | U+0A32 U+0A3C |
| U+0A36 | GURMUKHI LETTER SHA | U+0A38 U+0A3C |
| U+0B5C | ORIYA LETTER RRA | U+0B21 U+0B3C |

Two practical consequences.

**`NFC` is still the right answer.** Both spellings converge on the same
two-codepoint form, so normalising everything on the way in makes search and
comparison work. This was confirmed by normalising both spellings and comparing
the results.

**`NFC` is not "the composed form" here.** Anyone who sized a column, a fixed
field or a protocol frame on the assumption that `NFC` never lengthens a string
has an off-by-one waiting for the first supplier who types a nukta letter. For
this family, normalising *adds* codepoints.

---

## 6. Printing: there is no code page route

The argument, stated plainly because it determines the shape of the project.

A code page is a map from a byte value to a glyph in the printer's ROM. That
mechanism can express a script where each character is one glyph, independent of
its neighbours. It is why Cyrillic works over Windows-1251, and why the CJK file
can discuss multi-byte character modes.

Conjunct formation is **context-dependent by definition**: which glyph to print
for a consonant depends on what follows it. Two consonants joined by a virama
produce a glyph that is neither of them and that has no byte value of its own.
So even a printer that shipped with a complete Devanagari ROM font could only be
addressed for the isolated letters — the conjuncts, the reordered vowels and the
two-part vowels are outside what the mechanism can say.

This is an argument from the nature of a code page rather than a survey of
printers, and it is offered as such. `TODO: verify` against the target printer's
own command reference; the expected finding is that no code page on it claims a
Brahmic script at all.

**What follows is that the text must be rendered to a bitmap on the host and
sent as a raster image.** The relevant open questions become items 4 and 5 of the
verification list — which shaping engine, and which fonts are on the *device*
rather than on the development machine — plus the printer's raster command and
its maximum image width.

The Arabic and CJK files treat raster rendering as the fallback when the ROM
font is inadequate. For this family it is the only path, and it belongs in the
plan from the start rather than in the acceptance test.

---

## 7. The rupee sign

Three distinct codepoints, and they are not interchangeable:

| Codepoint | Name | Note |
| --- | --- | --- |
| U+20B9 | INDIAN RUPEE SIGN | Adopted for the Indian rupee |
| U+20A8 | RUPEE SIGN | The older ligature form |
| U+0BF9 | TAMIL RUPEE SIGN | In the Tamil block |

U+20B9 is a comparatively recent addition to Unicode and is absent from older
fonts and from essentially every thermal printer ROM font. Since section 6
concludes that this family prints as a raster image anyway, the question moves
from the printer to the font: whether the font being rasterised contains the
glyph.

`TODO: verify` — whether the target market expects the symbol, the ISO code
`INR`, or a Latin abbreviation on a printed document, and whether any rule
constrains the choice. Note also that Nepal, Sri Lanka, Pakistan, Mauritius and
several other markets have currencies called rupee with their own conventions;
sharing a name is not sharing a symbol.

---

## 8. Digit grouping: not three at a time

The Indian numbering system groups the integer part **2-2-3** rather than 3-3-3,
reflecting the units *lakh* and *crore*:

| Value | Western grouping | Indian grouping |
| --- | --- | --- |
| 100000 | 100,000 | 1,00,000 |
| 1000000 | 1,000,000 | 10,00,000 |
| 12345678 | 12,345,678 | 1,23,45,678 |

CLDR records this pattern for the relevant locales. Nearly every number
formatting library defaults to 3-3-3 and will produce a correct-looking, wrong
figure unless the locale is set — and set on the *server* that renders the
receipt, not only in the browser.

`TODO: verify`, per market and per document type: whether the Indian grouping is
expected on retail documents, and whether it applies to tax figures and totals as
well as to display prices. Grouping conventions do not necessarily follow the
script — a market using Devanagari does not automatically use lakh grouping, and
a tax authority may specify a format that differs from shop-floor convention.

### Native-script digits

Each script has its own digit forms, and ASCII digits dominate price display in
practice. The exposure is on the **input** side: product data arriving from a
local supplier may contain native-script digits inside names, codes or pack
sizes. These are not `0`–`9` and will not match a numeric search or parse.
`TODO: verify` whether the import path normalises them.

---

## 9. Which script, which market

The family is not uniform, and "Indic support" is not a single feature.

- **Tamil** forms far fewer conjuncts than Devanagari, preferring an explicit
  visible virama. It is the easiest member of the family to render and the one
  most likely to look acceptable in a naive implementation — which makes it a
  poor choice of test case for the others.
- **Malayalam** has both traditional and reformed orthographies, which differ in
  how freely they use conjuncts. Two fonts can render the same codepoints
  differently and both be defensible.
- **Sinhala** is grouped here for its rendering behaviour, which matches the
  family, rather than for its linguistic affiliation.
- **Gurmukhi**, **Gujarati**, **Odia**, **Telugu** and **Kannada** each have
  their own conjunct inventories.

A device configured and tested for one of these is not thereby working for
another. The rendering path is shared; the fonts, the conjunct sets and the
acceptance criteria are not.

---

## 10. Test matrix

Every row needs a **native reader** to judge it. Unlike a missing code page,
which produces obvious mojibake, a shaping failure produces text that looks like
writing and is wrong. An implementer who does not read the script cannot tell the
two apart.

| # | Test | Pass condition |
| --- | --- | --- |
| 1 | Print a word beginning with a consonant plus U+093F | The vowel sign appears **to the left** of the consonant |
| 2 | Print a Bengali word containing U+09CB | The vowel appears as two marks, one each side of the base |
| 3 | Print a two-consonant conjunct | One fused glyph, not two letters with a visible virama between them |
| 4 | Print a three-consonant conjunct | One glyph; no dotted circles |
| 5 | Truncate a name mid-cluster, print it | Cluster is dropped whole; no dotted circle, no changed word |
| 6 | Store the same word with U+0958 and with U+0915 U+093C, then search for one | Both records are returned |
| 7 | Print a full-width line of native text | Reaches the paper edge; not clipped by a raster width limit |
| 8 | Print a price with the rupee sign | Symbol renders; not a box, not blank |
| 9 | Print a six- and an eight-digit amount | Grouping matches the market convention agreed in section 8 |
| 10 | Print a name containing `ZWNJ` | The conjunct is **suppressed**, matching the supplier's intent |
| 11 | Import a supplier file with native-script digits | Digits are normalised or the record is flagged; not silently stored |
| 12 | Print a mixed native and Latin line, such as a name and a SKU | No reordering across the boundary; the SKU reads left to right |
| 13 | Repeat the whole matrix on the actual POS terminal, not the dev machine | Identical output; no font substitution |

Row 13 is the one most often skipped and most often the one that fails.

---

## 11. Where this applies

Primary markets: **India**, **Nepal**, **Bangladesh**, **Sri Lanka**.

Also relevant wherever a diaspora retail population reads one of these scripts.
Two markets already covered in this collection have Tamil-reading populations
and a Tamil-language public presence:

- [Malaysia](../countries/malaysia.md)
- [South Africa](../countries/south-africa.md)

In both, the deployment pattern is likely to be the one described in the Arabic
and Cyrillic files: **a back office operated in one language and a
customer-facing receipt in another.** The staff-facing screens may never need the
script at all while every printed receipt does, or the reverse. Establish which
before choosing where to put the effort.

> **This collection has no country file for any market where these scripts are
> primary.** Nothing here has been checked against India's GST rules, its
> e-invoicing mandate, invoice content requirements, or the equivalent in Nepal,
> Bangladesh or Sri Lanka. Everything above is about rendering text. The tax and
> document-content side is **entirely unresearched** and must come from a local
> accountant. See open item 10.

---

## Notes for POS implementers

**Budget for raster printing from the first sprint.** Section 6 is the
load-bearing conclusion of this file. A plan that assumes a code page will be
found is a plan that discovers otherwise during acceptance testing, when the
printer is already bought.

**Verify the font on the device, not on the laptop.** Development machines have
comprehensive font coverage. Low-cost Android POS terminals frequently do not.
This is open item 5 and it is the most common late failure.

**Never truncate on codepoints.** Use grapheme cluster boundaries. This applies
to product names, customer names, addresses and anything else with a length
limit — and it applies in the database layer, not only in the UI.

**Normalise to `NFC` on input, and allow for the string getting longer.**
Section 5. Sizing a column at exactly the pre-normalisation length is an
off-by-one waiting for the first nukta letter.

**Do not use Tamil as the acceptance test for the family.** Section 9. It is the
most forgiving member and will pass on an implementation that fails Devanagari.

**Get a native reader onto the test matrix.** Section 10. Every other script in
this collection fails visibly when it fails. This one fails legibly.

**Treat digit grouping as a separate decision from script.** Section 8. The two
do not travel together, and the tax authority may not agree with the shop floor.

---

_Maintained by the MISAll team. Last updated: 2026-08_
