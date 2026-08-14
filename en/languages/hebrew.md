# Hebrew — RTL Without Shaping, and the Visual-Order Trap

**Hebrew is right-to-left, and that is roughly where the resemblance to Arabic
ends.** Hebrew letters do not join. There is no shaping engine, no initial or
medial forms, no presentation-forms block, no mandatory ligature. Every letter has
one glyph, and the glyph you store is the glyph that prints. Half the Arabic file
does not apply here.

What remains is the bidirectional algorithm, which applies in full, and one
problem Arabic does not have in the same form: **Hebrew's legacy encodings
disagree about whether the bytes are in reading order or in printing order.** Two
files can hold the same Hebrew string, both validly encoded, byte-reversed
relative to one another. Choosing the wrong one produces text that is not garbled
— it is backwards, which is a harder failure to notice and a much harder one to
undo after it has been stored.

This file covers the engineering problems. It is not an introduction to the
language.

> ### Verification status — unverified draft
>
> The Unicode and encoding behaviour described here is specified and stable. The
> printer-specific values are not, and neither are the market conventions.
>
> **Open items — `TODO: verify`**
>
> 1. Every `ESC t` code page number, against the specific printer's own command
>    reference. Vendors renumber these, as noted in the Arabic file.
> 2. Whether the target printer has a Hebrew ROM font at all, and which code page
>    it is reached through.
> 3. Whether that font's byte order is visual or logical — see §4. This is the
>    single most important thing to establish about a Hebrew printer.
> 4. Whether the shekel sign `₪` (U+20AA) is present in the ROM font, or whether
>    the ISO code must be printed instead.
> 5. Conventional position of the currency symbol relative to the amount on Israeli
>    retail documents.
> 6. Whether any legal requirement governs receipt language, or the script in which
>    tax figures must appear, in the target market.

---

## 1. What Hebrew does not need

Worth stating explicitly, because a team arriving from an Arabic deployment will
carry machinery it can now delete:

| Arabic requires | Hebrew |
| --- | --- |
| Contextual shaping — four positional forms per letter | **Not applicable.** One form per letter. |
| A shaping engine in firmware or application | **Not needed.** |
| Presentation-forms codepoints in the print path | **Not needed.** Never appear. |
| A mandatory ligature (lam-alef) | **None.** |
| Deciding whether firmware or application shapes | **Does not arise.** |
| Never truncating mid-word, because cutting changes letter forms | Truncation is still ugly, but it does not change any glyph. |

The consequence is that **plain code-page printing is a genuinely viable path for
Hebrew**, where for Arabic it is a compromise. If the printer has a Hebrew font
and you have established its byte order, you can send bytes and get correct
output. That is not true of Arabic, and it is why this file recommends raster
rendering less emphatically than the Arabic and Thai files do.

## 2. Final forms are codepoints, not shapes

Five Hebrew letters take a different form at the end of a word:

| Regular | Final (sofit) | Letter |
| --- | --- | --- |
| `כ` U+05DB | `ך` U+05DA | kaf |
| `מ` U+05DE | `ם` U+05DD | mem |
| `נ` U+05E0 | `ן` U+05DF | nun |
| `פ` U+05E4 | `ף` U+05E3 | pe |
| `צ` U+05E6 | `ץ` U+05E5 | tsadi |

**These are separate characters, chosen when the word is spelled, not selected by
a rendering engine at print time.** This is the opposite of Arabic, and it matters
for two reasons.

First, nothing in the print path needs to know about them. They arrive correct.

Second — and this is where it bites — **they are the fastest way to detect that
something has reversed a string**. A naive "RTL fix" that reverses the character
order leaves the final form sitting at what is now the *start* of the word. To a
Hebrew reader that is not subtly wrong, it is nonsense, and it is visible at a
glance even in a screenshot. Test 2 in §8 exists for this.

They also affect search and comparison: `שלום` ends in a final mem, and a
substring search for the regular-mem spelling will not match it. Normalise search
input rather than the stored data.

## 3. Bidirectional layout

Everything in the Arabic file's §1–§4 applies to Hebrew unchanged, and is not
repeated here:

- Set the base direction to RTL **explicitly per line**, rather than letting the
  first-strong heuristic infer it from an item name that begins with a Latin brand.
- Treat each receipt line as its own paragraph.
- Store logical order; reorder only in the print pipeline.
- Wrap numeric runs and Latin product codes in isolates (`LRI … PDI`, U+2066 …
  U+2069) so their direction cannot leak.
- Pad **outside** the isolate, not inside it.
- Parentheses and brackets mirror in an RTL context. Do not mirror twice.

Two differences from Arabic are worth naming:

**Digits are simpler.** Hebrew commercial documents use Western ASCII digits
(U+0030–U+0039). There is no Hebrew equivalent of the Arabic-Indic digit choice,
so the per-market digit-form setting the Arabic file calls for is not needed here.
Hebrew letter-numerals exist and are used for Hebrew-calendar dates and
enumeration in traditional contexts; they do not appear in prices, and treating
them as a number format would be a mistake.

**Mixed Hebrew–Latin lines are the normal case, not the edge case.** Israeli
retail catalogues carry imported brand names in Latin script routinely, and
English appears alongside Hebrew on many commercial documents. Every
mixed-direction failure mode is therefore an everyday one rather than something
that surfaces on unusual data.

## 4. Visual order versus logical order

This is the Hebrew-specific trap, and it is an encoding problem rather than a
rendering one.

**Logical order** stores characters in the order they are read — first letter of
the word first. The renderer applies the bidirectional algorithm to decide where
they appear. **Visual order** stores characters in the order they are *printed*,
left to right, with the reordering already baked in. A visually-ordered Hebrew
string looks reversed to anything that expects logical order, and vice versa.

Both conventions exist in Hebrew encodings, and the encoding name is what tells
them apart:

| Encoding | Order | Notes |
| --- | --- | --- |
| **Windows-1255** (CP1255) | **Logical** | Near-superset of ISO-8859-8. Carries the shekel sign `₪` at 0xA4 and supports vowel points. The usual modern choice. |
| **ISO-8859-8** | **Visual** | Position 0xA4 is the generic currency sign, **not** the shekel. |
| **ISO-8859-8-I** | **Logical** | Same byte values as ISO-8859-8; the `-I` suffix declares logical order and nothing else. |
| **CP862** | **Visual**, in practice | DOS Hebrew. Text was normally stored visually because DOS had no bidi support. Still present in thermal printer firmware. |

Three consequences for a POS:

**The order is not detectable from the bytes.** ISO-8859-8 and ISO-8859-8-I are
byte-identical. Nothing in the data says which one you have. It is declared, or it
is assumed, and an assumption that is wrong reverses every Hebrew string.

**A printer that expects visual order makes the application responsible for
reordering.** If the firmware's Hebrew mode is CP862-derived, sending
logically-ordered bytes prints the words backwards. The application has to run the
bidi algorithm and emit the visual sequence itself. If the firmware expects
logical order and the application reorders anyway, the result is backwards for the
same reason, in the opposite direction. `TODO: verify` which one the target model
does; this is item 3 in the verification list and it is not discoverable at
runtime.

**Never store visual order.** The Arabic file's rule applies with more force here,
because Hebrew has a legacy encoding that actively invites the violation. Visually
ordered text corrupts search, sorting, export, and any later attempt to render the
same string on a screen. If historical data has been stored visually — which
happens when a system was ported from a DOS-era predecessor — that is a migration
problem to solve deliberately, not something to compensate for at render time.

## 5. Nikud and width

Hebrew vowel points (nikud, U+05B0–U+05BC and neighbours) and cantillation marks
are combining characters. They occupy no column.

They are absent from ordinary commercial text — Israeli receipts, catalogues and
signage are written without them — so the practical risk is not that you must
render them, but that they **arrive unexpectedly in copied supplier data** and
break a padding calculation based on character count. Same failure as Arabic
harakat: the column drifts on real data after aligning perfectly on test data.

Measure display width, not codepoint count. This is the same fix that the Arabic,
Thai and CJK files all arrive at from different directions:

```python
import unicodedata

def width(s):
    return sum(0 if unicodedata.combining(c) else 1 for c in s)
```

Hebrew has no wide characters, so unlike CJK the mapping is one column per
non-combining character — the correction is only for the marks.

## 6. Encoding on the wire, and whether raster is needed

Most ESC/POS printers do not accept UTF-8. Text is sent as single-byte values
through a code page selected with `ESC t n`.

> `TODO: verify` — **the `n` value for each page is deliberately omitted here**,
> for the reason given in the Arabic file: vendors renumber the code page table,
> and clone firmware diverges from the Epson-documented ordering while claiming
> compatibility. Read it from the target printer's own command reference and
> confirm by printing.

Because Hebrew needs no shaping, a single-byte code page genuinely covers the
script. The remaining gaps are the ones code pages always have:

- **The shekel sign.** `₪` is present in Windows-1255 but not in ISO-8859-8, and
  ROM font coverage is a separate question from code page definition. Where it is
  missing, print `ILS` rather than a box — the Arabic file's rule about currency
  symbols applies unchanged.
- **Mixed script on one line.** A Hebrew item name beside a Latin brand beside a
  currency symbol is the ordinary case in Israeli retail, and single-byte pages run
  out at exactly that point.
- **The order question in §4**, which no code page choice resolves.

**When to use raster rendering.** Rendering the receipt to a bitmap and sending it
as a graphic (`GS v 0`) removes the code page question, the glyph coverage
question and — importantly — the visual-versus-logical question, because the
renderer resolves the order and what is rendered is what prints.

For Arabic this file's sibling calls raster the default. For Hebrew it is a
narrower recommendation: **use raster if the receipt mixes scripts, if the shekel
sign must appear, or if the printer's byte order cannot be established.** If none
of those hold and the printer has a Hebrew font whose order you have confirmed,
code-page printing is faster and adequate. That is a real difference between the
two scripts, and it is the practical payoff of Hebrew not being cursive.

## 7. Column alignment and the amount side

In an RTL layout, reading starts at the right: description at the right edge,
amount at the left. What matters more than the choice is consistency between the
header, item lines, totals block and tax breakdown — a totals block that keeps the
amount at the right edge while item lines put it at the left is as visible a defect
here as in Arabic.

Within the amount column the digits remain a left-to-right run, so pad to align
the decimal separators vertically, and pad outside the isolate.

**Line budget.** At 80 mm and 48 columns, a 12-column amount field leaves 35
columns for the description. Hebrew is compact — no vowel points in commercial
text, and words are short — so this is usually comfortable, more so than Arabic
and far more so than CJK. At 58 mm and 32 columns, a Hebrew name plus an aligned
amount is workable for short names and not for names carrying an embedded Latin
brand; stack the name on its own line in that case.

## 8. Test matrix

Print on the target hardware. Screen output proves nothing, because the operating
system's text engine does work the printer path does not.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | `סה״כ` (total) alone | Prints, reads right to left, no boxes |
| 2 | A word ending in a final form, e.g. `שלום` | The final mem is at the **left** end of the printed word — if it is at the right end, something reversed the string |
| 3 | `קוקה קולה 2 × 3.50` | Hebrew right, number left-to-right, separator stays inside the number |
| 4 | An item name with an embedded Latin brand | The line's base direction does not flip |
| 5 | `-10%` beside Hebrew text | Sign and percent stay attached, on the correct side |
| 6 | Three item lines of differing name lengths | Decimal separators align vertically |
| 7 | A name copied from supplier data containing nikud | Column alignment does not drift |
| 8 | `₪` in a total line | A glyph prints, not a box or a blank |
| 9 | A full sentence of mixed Hebrew and English | Word order within each run is correct in both |
| 10 | Full receipt at 80 mm, then 58 mm | Both readable; 58 mm stacks rather than squeezes |
| 11 | Reprint of a stored transaction | Identical to the original — confirms nothing visual-order is stored |

Have the output read by someone who reads Hebrew. Test 2 is the one that catches
a reversed pipeline, and it is the one a non-reader is most likely to pass.

## 9. Where this applies

**Israel** is the market this file is written for. Hebrew is the language of
retail there, and Israel is not yet covered by a country file in this repository —
the tax, invoicing and receipt-content requirements are therefore **not** documented
here, and nothing in this file should be read as covering them.

Hebrew also appears in businesses serving Jewish communities elsewhere, where it
is usually a secondary language on the document rather than the primary one. In
that configuration the mixed-script handling in §3 and §6 is the whole job.

The familiar three-way split applies: a shop may need a Hebrew till interface, a
different back-office language for an owner who does not read Hebrew, and a print
template language chosen independently of both. Only the print template drives
anything in this file.

## Notes for POS implementers

**Establish the printer's byte order before writing any template.** Visual versus
logical is the first question for Hebrew, it is a per-model fact, it is not
discoverable at runtime, and getting it wrong reverses every string while
producing output that still looks like Hebrew to a reviewer who does not read it.

**Store logical order. Render visual order. Never store visual order.** Hebrew has
a legacy encoding that makes the violation easy and a DOS-era installed base that
makes inherited visual data plausible. Check what is actually in the database
before assuming.

**Delete the shaping machinery, keep the bidi machinery.** Teams porting from an
Arabic deployment reliably keep too much. Shaping, presentation forms and ligature
handling are dead code for Hebrew. Base direction, isolates, neutral resolution
and display-width measurement are all still load-bearing.

**Raster is a choice here, not a default.** Unlike Arabic and Thai, Hebrew has a
working code-page path. Decide per deployment on the three criteria in §6 rather
than reaching for raster reflexively — and record the decision, because the next
person will assume the Arabic default applied.

**Print the ISO code when the symbol is uncertain.** `ILS` beats a box character
where the price should be.

---

_Maintained by the MISAll team. Last updated: 2026-08_
