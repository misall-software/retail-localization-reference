# Arabic — RTL Receipt Layout and Thermal Printing

**A thermal printer does not implement the Unicode bidirectional algorithm.** It
receives bytes and emits glyphs left to right in the order given. Every layout
decision Arabic requires — reordering, letter shaping, column alignment, where the
currency symbol lands — has to be resolved by the application before the first
byte reaches the printer. Screen output can rely on the operating system's text
engine; print output cannot.

This file covers the engineering problems. It is not an introduction to the
language.

> ### Verification status — unverified draft
>
> The Unicode behaviour described here is specified in the standard and is stable.
> The printer-specific values are not.
>
> **Open items — `TODO: verify`**
>
> 1. Every `ESC t` code page number, against the specific printer's own command
>    reference. Vendors renumber these.
> 2. Whether the target printer performs contextual shaping in firmware or expects
>    pre-shaped presentation forms.
> 3. Whether the target printer's ROM font covers the required repertoire,
>    including the lam-alef ligature.
> 4. Which digit form is expected on receipts in each target market — this is a
>    market convention, not a technical constraint, and it varies.
> 5. Currency symbol glyph coverage per market, particularly for symbols added to
>    Unicode recently; ROM fonts lag the standard by years.
> 6. Whether any target market imposes legal requirements on receipt language or
>    on which script tax figures must appear in.

---

## 1. Direction is a property of the run, not of the string

A receipt line is rarely uniform. `كوكا كولا 2 × 3.50` contains a right-to-left
run, a left-to-right numeric run, and neutral characters between them. The Unicode
bidirectional algorithm (UAX #9) resolves the visual order. What matters in
practice:

**Set the base direction explicitly per line.** The algorithm's default
first-strong heuristic takes the paragraph direction from the first strongly
directional character. On a receipt this is actively harmful: an item whose name
begins with a Latin brand or a SKU gets a left-to-right base direction, and that
one line lays out mirrored relative to every line around it. Set the base
direction to RTL explicitly for each line rather than letting it be inferred.

**Treat each line as its own paragraph.** Receipt lines are independent. Running
the algorithm over the whole receipt as one paragraph lets one line's content
influence another's resolution.

**Reorder once, at the last moment.** Store logical order; convert to visual order
only in the print pipeline. Storing visually-ordered text corrupts search,
comparison, export and anything that later renders the same string on screen.

## 2. Numbers inside Arabic text

Digits form a left-to-right run even inside RTL text. `المجموع 1,234.50` places
the number to the left of the label, and the number's own digits read left to
right. This is correct and expected — resist the instinct to "fix" it.

Two failure modes are common:

**Separators detach from the number.** The comma and period in `1,234.50` are
neutral characters. Inside a number they are resolved as part of the numeric run,
but a trailing separator adjacent to RTL text may resolve to the surrounding
direction and jump to the opposite end of the run. A total that prints as
`.1,234 50` is this bug.

**Signs and percent marks migrate.** A leading minus, a plus, or a `%` next to a
number is neutral or weakly directional and lands on whichever side the algorithm
resolves. A discount showing `10%-` instead of `-10%` is the same class of
problem. Wrap the numeric run in an isolate — see §3.

### Digit forms

Three sets are in use:

| Form | Codepoints | Notes |
| --- | --- | --- |
| Western (ASCII) | U+0030–U+0039 | Widely used on printed commercial documents across the Arab world. |
| Arabic-Indic | U+0660–U+0669 (`٠١٢٣٤٥٦٧٨٩`) | Used in parts of the region. |
| Eastern Arabic-Indic | U+06F0–U+06F9 (`۰۱۲۳۴۵۶۷۸۹`) | Persian/Urdu context; distinct glyphs for some digits. |

Make the digit form a template setting, not a code branch — `TODO: verify` the
expectation per market. Two constraints hold regardless of the choice: convert
digits at render time only, never in stored data; and never mix forms on one
document, which is the visual equivalent of mixing fonts mid-sentence.

Note that Arabic-Indic digits still form left-to-right runs. Switching the digit
form does not change the ordering behaviour, only the glyphs.

## 3. Neutral characters and explicit marks

Neutral characters — space, colon, parentheses, slash, currency symbols — take
their direction from context. At the boundary between a label and a value this is
exactly where the algorithm's answer surprises people.

The tools:

| Character | Codepoint | Use |
| --- | --- | --- |
| RLM — right-to-left mark | U+200F | Invisible strong RTL character. Pins a neutral run to RTL. |
| LRM — left-to-right mark | U+200E | Invisible strong LTR character. |
| LRI / RLI / FSI | U+2066 / U+2067 / U+2068 | Isolates. Wrap a run so its direction cannot leak into surrounding text. |
| PDI | U+2069 | Terminates an isolate. |

**Prefer isolates over marks.** Wrapping a Latin product code or a numeric run in
`LRI … PDI` prevents it from affecting the resolution of anything around it. The
older approach of sprinkling RLM characters works but is positional, fragile, and
undiscoverable to the next maintainer.

**Mirrored characters.** Parentheses, brackets, and angle brackets are mirrored
when rendered in an RTL context — an opening parenthesis is drawn as `)`. If the
rendering path handles mirroring, do not also mirror in application code; doing
both cancels out. If the printer path does not handle it, the application must.
This is a specific thing to test, because a mirrored bracket looks like an
ordinary typo and passes review.

## 4. Column alignment on a fixed-width receipt

This is where most implementations break, and the cause is almost always the same:
**character count is not display width.**

**Combining marks occupy no column.** Arabic diacritics (harakat, U+064B–U+0652)
and the tatweel are frequently absent from commercial text, but they arrive
through copied supplier data. A padding calculation based on string length counts
them and under-pads the line, so a column that was aligned on the developer's test
data drifts on real data.

**Presentation forms and ligatures collapse.** Two codepoints can print as one
glyph — see §5. Length-based padding overshoots.

**Normalise before measuring.** Apply Unicode normalisation, strip or account for
zero-width marks, then compute display width in printer columns. Measure the
string you will actually send.

### Which side does the amount column go?

In an RTL layout, reading starts at the right. The conventional arrangement mirrors
the familiar one: description at the right edge, amount at the left. What matters
more than the choice is consistency between the header, the item lines, the
totals block and any per-tax breakdown — a totals block that keeps the amount at
the right edge while item lines put it at the left is the most common visible
defect on an Arabic receipt.

Within the amount column, the numbers themselves remain left-to-right, so the
alignment problem is unchanged: pad so that the decimal separators line up
vertically. Pad on the correct side of the numeric run, and do the padding
**outside** the isolate, not inside it — padding inside the isolate becomes part
of the isolated run and does not participate in the surrounding layout.

### Worked constraint

At 80 mm and 48 columns, a two-column line with a 12-column amount field leaves
35 columns for the description plus one separator. Arabic item names are compact
relative to English, so this is usually workable — but a name with a Latin brand
element embedded in it consumes width unpredictably and needs the same wrap
handling as any other overflow. At 58 mm and 32 columns, two columns plus an
aligned amount is not viable for most item names; stack the name on its own line
with the amount beneath it, right-aligned to the base direction.

## 5. Shaping and ligatures

Arabic letters take different forms depending on position: isolated, initial,
medial, final. The stored codepoints are position-independent; the printed glyphs
are not.

**Who does the shaping?** Either the printer firmware, using an Arabic ROM font
with a shaping engine, or the application, converting to presentation forms
before sending. Both exist in the field. Assuming the wrong one produces text
that prints as disconnected isolated letters — legible to no one, but recognisably
"Arabic-shaped" enough that it can survive a screenshot review by someone who does
not read Arabic. `TODO: verify` per printer model.

**The lam-alef ligature is mandatory.** `ل` followed by `ا` must render as the
single glyph `لا`. This is not stylistic; the unligated sequence is wrong.
Codepoints exist in the presentation-forms blocks for the ligature and its
variants. If the application is doing the shaping, it must handle this case.

**Presentation-form codepoints are a rendering artefact.** They belong in the
print pipeline only. Never store them, never compare against them, never export
them — they break search, sorting and interchange.

## 6. Encoding on the wire

Most ESC/POS printers do not accept UTF-8. Text is sent as single-byte values
interpreted through a selected code page, chosen with the `ESC t n` command.

Candidate Arabic code pages:

| Code page | Notes |
| --- | --- |
| CP864 | DOS Arabic. Contains presentation forms, so text must be pre-shaped. |
| CP720 | DOS Arabic, transparent ASMO. Different layout from CP864. |
| Windows-1256 | Windows Arabic. Covers the base repertoire; expects the renderer to shape. |
| ISO-8859-6 | Base Arabic, limited repertoire, uncommon in POS firmware. |

> `TODO: verify` — **the `n` value for each page is deliberately omitted here.**
> Vendor implementations renumber the code page table, and clone firmware
> frequently diverges from the Epson-documented ordering while claiming
> compatibility. Read the value out of the target printer's own command reference
> and confirm it by printing.

None of these carry the full Arabic repertoire plus Latin plus the currency
symbols a real receipt needs. Once a receipt has to show Arabic, a Latin brand
name and a currency symbol on the same line, single-byte code pages have run out.

## 7. Raster rendering: the recommended default

Render the receipt to a monochrome bitmap and send it as a graphic (`GS v 0`, or
`ESC *` on older firmware).

**What it solves:** shaping, bidi ordering, ligatures, code pages, glyph coverage,
and mixed-script lines all become the rendering library's problem, and rendering
libraries solve them correctly. What is rendered is what prints.

**What it costs:** more data over the link, so slower printing — noticeable on
serial connections, generally acceptable on USB and network. The printer's own
font settings, double-width and double-height commands no longer apply; the
renderer must produce those effects. Resolution must match the printer's dot
density or output looks soft.

For Arabic this is the right default rather than a fallback. It is also the
approach that scales when one deployment prints Arabic receipts, keeps a
back-office language with an entirely different script, and needs both to work on
the same hardware.

## 8. Line breaking and truncation

- Arabic does not hyphenate. Break on whitespace only.
- **Never truncate mid-word.** Because letters are shaped by position, cutting a
  word changes the final letter's form and produces something that reads as a
  different, misspelled word rather than as an obviously clipped string.
- Truncation with an ellipsis must place the ellipsis at the correct visual end
  for the base direction.
- Zero-width joiners and non-joiners must not be orphaned at a break.

## 9. Test matrix

Print these, on the target hardware, before building the template. Screen output
proves nothing here.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | `المجموع` (total) alone | Letters are connected, not isolated. Shaping works. |
| 2 | `لا` in a word | Renders as the single lam-alef ligature. |
| 3 | `كوكا كولا 2 × 3.50` | Arabic right, number left-to-right, separator inside the number stays inside it. |
| 4 | An item name with an embedded Latin brand | The line's base direction does not flip. |
| 5 | `-10%` beside Arabic text | Sign and percent stay attached, on the correct side. |
| 6 | Three item lines with differing name lengths | Decimal separators align vertically. |
| 7 | A name copied from supplier data containing diacritics | Column alignment does not drift. |
| 8 | The currency symbol for the target market | A glyph prints, not a box or a blank. |
| 9 | Full receipt at 80 mm, then the same at 58 mm | Both are readable; the 58 mm layout is not the 80 mm layout squeezed. |
| 10 | Reprint of a stored transaction | Identical to the original. Confirms nothing visual-order is being stored. |

Have the output read by someone who reads Arabic. Tests 1, 2 and 4 produce failures
that look plausible to a reviewer who does not.

## 10. Where this applies

Arabic is the language of retail across the Gulf states, the Levant, Iraq, Egypt,
Sudan, Libya and the Maghreb. Two practical qualifications:

- **The Maghreb is bilingual in commerce.** French is widely used in retail
  documentation in Morocco, Algeria and Tunisia, often alongside Arabic on the same
  document. Plan for a receipt template carrying both scripts, which makes the
  mixed-direction problems in §1–§4 the normal case rather than the edge case.
- **The Gulf mixes Arabic and English on the same receipt** routinely, and some
  markets have expectations about which language tax figures appear in —
  `TODO: verify` per market, as this can be a legal requirement rather than a
  preference.

A separate consequence for POS design: a shop in these markets may need an Arabic
till interface and an entirely different back-office language for the owner. The
till language, the back-office language and the print template language are three
independent settings, and only the print template drives everything in this file.

## Notes for POS implementers

**Store logical order. Render visual order. Never store visual order.** Every
downstream problem in Arabic receipt printing traces back to a violation of this.

**The print path is not the screen path.** The operating system's text engine
handles the screen. The printer path is code you own end to end, and it has to do
the same work.

**Decide shaping ownership once, per printer model, and write it down.** Whether
the firmware shapes or the application does is a per-model fact, it is not
discoverable at runtime, and it silently produces unreadable output when wrong.

**Reserve currency rendering as a configuration point.** Where a symbol's glyph
coverage is uncertain, print the ISO code instead. `TODO: verify` per market;
a box character where the price should be is worse than three Latin letters.

**Budget testing time on real hardware.** Every failure mode in §9 is invisible in
an emulator, and several are invisible to a reviewer who does not read the script.

---

_Maintained by the MISAll team. Last updated: 2026-08_
