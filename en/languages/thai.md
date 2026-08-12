# Thai — Receipt Layout and Printing

**Thai is written without spaces between words, and stacks up to three marks
vertically on one consonant.** Those two facts break line wrapping and column
alignment respectively, and both are written into code that has never seen a
non-European script. A third fact breaks product search: several Thai vowels are
*written* before the consonant they are *pronounced* after, so alphabetical
sorting by codepoint does not produce Thai alphabetical order.

None of this is exotic. It is the normal case for every Thai deployment.

> ### Verification status
>
> Unicode behaviour here is specified and stable. Printer values are not.
>
> **Open items — `TODO: verify`**
>
> 1. Thai code page support on the target printer and its selector value.
> 2. Whether the ROM font renders the full three-level mark stack without
>    clipping.
> 3. Whether the kitchen printer — usually a different, cheaper model — behaves
>    the same as the front-of-house one.
> 4. Whether the Buddhist Era calendar is required, permitted or merely customary
>    on printed documents. See the Thailand country file.

---

## 1. No spaces between words

Thai runs continuously. Spaces exist, but they separate phrases and sentences,
not words — roughly where English uses a comma or a full stop.

The consequence: **wrapping on whitespace is wrong.** It produces lines that break
in the middle of words, which in Thai is not a cosmetic clipping artefact but a
different string. Correct wrapping needs a dictionary-based or ICU-style
line-break algorithm (UAX #14 handles Thai through dictionary lookup, not through
character properties alone).

`TODO: verify` what the chosen rendering path provides. This is the first
question to ask, because a text layer with no Thai dictionary cannot wrap Thai
correctly no matter how it is configured.

There is no capitalisation and no full stop, so there are also no case-conversion
or sentence-detection bugs to worry about — a small mercy.

## 2. The mark stack

A Thai syllable cluster is built up vertically:

- **Base consonant** — the only part that occupies a column
- **Above or below vowel** — `ิ ี ึ ื` above, `ุ ู` below
- **Tone mark** above the upper vowel — `่ ้ ๊ ๋`
- Occasionally **thanthakhat** `์` on top

So a single displayed cluster can be four codepoints tall and **one column wide**.
Two consequences, both of which appear elsewhere in this repository:

**Column arithmetic on codepoint count is wrong.** Combining marks occupy no
horizontal space. A padding calculation based on string length over-counts and
under-pads, so columns drift on real data while looking correct on ASCII test
data. Measure display width, counting only the base characters.

**Line height must accommodate the stack.** Tight leading clips the upper tone
marks. A clipped tone mark is legible enough that a non-reader sees nothing wrong,
and wrong enough that a Thai reader gets a different word — the same trap as the
disconnected Arabic letters documented in the Arabic file.

**Sara Am** `ำ` is a single codepoint that renders as a mark above plus a trailing
tail. If a renderer decomposes it, it can end up split across a line break. Worth
including in test data.

## 3. Sorting is not codepoint order

Five Thai vowels are written to the *left* of the consonant they follow
phonetically: `เ แ โ ใ ไ`. A word beginning with one of these sorts, in Thai
dictionary order, under the *consonant*, not under the vowel.

This does not affect printing — but it affects every product list, every search
box and every alphabetical report the staff use. Sorting Thai product names by
raw codepoint produces an order that looks arbitrary to a Thai speaker, and staff
lose time hunting for items.

Use a Thai collation (ICU `th` locale) for any user-facing sort or search. This is
the one item in this file that is invisible on the receipt and visible every day
at the counter.

## 4. Encoding

Most ESC/POS printers do not accept UTF-8. Thai needs a dedicated code page:

| Code page | Notes |
| --- | --- |
| TIS-620 | The Thai national standard |
| CP874 | The Windows variant, TIS-620 plus a few additions |

`TODO: verify` support and the selector value on the target model; vendor
numbering diverges, as documented in the Arabic file.

**Raster rendering is the recommended default here**, more strongly than for
accented Latin. It resolves the mark stacking, the glyph coverage and the code
page at once — but note that it does **not** solve line breaking. Wrapping happens
before rendering, so a raster path still needs a Thai-aware line-break algorithm
upstream. This is the one place where raster is not a complete answer.

## 5. Digits and calendar

Thai has its own digits, `๐๑๒๓๔๕๖๗๘๙` (U+0E50–U+0E59), alongside the Western
ones. Western digits are usual on commercial documents; make the choice a
template setting rather than a code branch, and never mix forms on one document —
the same rule as the Arabic file.

The Buddhist Era calendar runs 543 years ahead of the Common Era, so 2026 CE is
2569 BE, and Thai commercial documents commonly use it. Store dates in one
canonical form and convert at render time; storing BE dates guarantees an
off-by-543 bug somewhere downstream. See the Thailand country file for the open
question of whether BE is required or merely customary.

## 6. Test matrix

Print on the target hardware, and have the output read by someone who reads Thai.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | A word with a three-level stack, e.g. `ที่` | All marks present, none clipped at the top |
| 2 | A product name long enough to wrap | Break falls between words, not inside one |
| 3 | `ำ` (sara am) at a line end | Not split across the break |
| 4 | Three item lines of differing name lengths | Amount decimal points align vertically |
| 5 | `฿` currency symbol | A glyph, not a box |
| 6 | Product list sorted alphabetically | Words starting `เ แ โ ใ ไ` sort under the consonant |
| 7 | The same receipt on the kitchen printer | Same result as front of house |
| 8 | Reprint of a stored transaction | Identical to the original |

Tests 1, 2 and 6 produce failures that look fine to a reviewer who does not read
Thai. Test 7 exists because the kitchen printer is frequently a different and
cheaper model — see the food service sections.

## Notes for POS implementers

**Line breaking is the hard part, and raster does not fix it.** Establish early
whether the stack has a Thai dictionary available.

**Measure display width, not codepoint count.** Same rule as Arabic and CJK, same
reason.

**Give the kitchen printer its own acceptance test.** Narrow paper, cheaper
hardware, read under time pressure.

**Use a Thai collation for sorting.** The only item here that never shows up on a
receipt and costs staff time every shift.

---

_Maintained by the MISAll team. Last updated: 2026-08_
