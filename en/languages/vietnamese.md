# Vietnamese — Receipt Layout and Printing

**Vietnamese is Latin script that behaves like a non-Latin one.** It stacks two
diacritics on a single vowel — one marking vowel quality, one marking tone — which
produces a repertoire of roughly 134 letters beyond ASCII. No single-byte code
page covers it fully, including the one nominally designed for Vietnamese.

The failure mode sits between the two extremes documented elsewhere in this
repository. It is louder than accented Latin, where a dropped accent still reads;
quieter than Arabic, where broken output is obviously broken. A Vietnamese
receipt with the tone marks missing looks like Vietnamese to a non-reader and
reads as a different word, or as nothing, to a Vietnamese one.

> ### Verification status
>
> Unicode behaviour here is stable. Printer values are not.
>
> **Open items — `TODO: verify`**
>
> 1. Vietnamese code page support on the target printer and its selector value.
> 2. Whether the ROM font covers the full precomposed repertoire.
> 3. Whether supplier-provided product data arrives in a legacy encoding.

---

## 1. Two marks on one vowel

A Vietnamese vowel can carry both a quality diacritic and a tone mark:

| Layer | Examples |
| --- | --- |
| Base vowel | `a e i o u y` |
| Quality | `â ă ê ô ơ ư` — circumflex, breve, horn |
| Tone | grave, hook above, tilde, acute, dot below |
| Both | `ế ộ ữ ằ ợ` |

Plus `đ`, which is a distinct letter, not a `d` with a stroke to be normalised
away.

Every one of these has a precomposed codepoint, so the text itself is
straightforward — the problem is entirely about getting it to a printer.

## 2. Why the obvious code page does not work

Most ESC/POS printers do not accept UTF-8, so text goes through a selected
single-byte code page. For Vietnamese the candidates are:

| Encoding | Problem |
| --- | --- |
| **Windows-1258** | The nominal Vietnamese page. **Does not cover the full precomposed repertoire** — it encodes some syllables as base letter plus a combining tone mark, so a naive transcode drops or mangles tones even when the code page is nominally correct. |
| TCVN3 (ABC) | Legacy. Splits Vietnamese across two fonts, one for lowercase and one for uppercase. Still turns up in old data. |
| VNI | Legacy, a different split again. |
| VISCII | Legacy, rarely in printer ROM. |

This is the crux: **selecting the "right" code page is not sufficient.** A
Vietnamese deployment that has correctly set CP1258 can still lose tone marks.

`TODO: verify` the selector value and the actual coverage on the target model,
by printing rather than by reading the datasheet.

## 3. Legacy encodings in supplier data

Product catalogues arrive as spreadsheets, and Vietnamese spreadsheets from
long-established suppliers are frequently in TCVN3 or VNI rather than Unicode.
Pasted into a Unicode system they become mojibake, or worse, become plausible but
wrong text.

**Normalise on import; never pass legacy encodings through to the printer.** Test
an import with a small batch before loading several thousand product names, and
have a Vietnamese reader check the result — an import that silently corrupts a
catalogue is expensive to unwind after prices and stock are attached to it.

Also normalise to **NFC**. Decomposed input loses marks through a single-byte
code page and inflates character counts so column arithmetic disagrees with the
printed width — the same mechanism described in the accented-Latin file, with
more to lose.

## 4. Raster rendering

For Vietnamese this is the recommended default rather than a fallback, because
the alternative depends on a code page that is known not to cover the language
completely. Rendering the receipt to a bitmap resolves coverage, encoding and
mark placement together.

Unlike Thai, there is no line-breaking complication: Vietnamese words are
space-separated, so ordinary whitespace wrapping is correct. Do not break inside
a word.

## 5. Width, sorting and the currency symbol

**Width.** Every character is one column, so width equals count after NFC
normalisation. Before it, combining marks inflate the count.

**Length.** Vietnamese words are short but numerous, so a product description
wraps across more lines than its English equivalent. Budget for two-line item
names at 58 mm — see the Vietnam country file.

**Sorting.** Vietnamese alphabetical order places `đ` after `d`, and orders the
vowel-quality letters after their base vowels. Codepoint order does not produce
this. Use a Vietnamese collation (ICU `vi` locale) for product lists and search,
for the same practical reason given in the Thai file: staff use those lists all
day.

**Currency.** `₫` (U+20AB) is frequently absent from printer ROM. Verify it
prints; fall back to `VND` rather than shipping a box character. Note also that
the dong uses a period as the thousands separator and no decimals — that is a
formatting matter covered in the Vietnam country file, but it is the other half
of what makes a Vietnamese receipt look right.

## 6. Test matrix

Print on the target hardware and have a Vietnamese reader check it.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | `Cà phê sữa đá` | Every tone and quality mark present |
| 2 | `Nguyễn` | The stacked marks on `ễ` render correctly |
| 3 | `đ` in a word | Renders as `đ`, not `d` |
| 4 | `Tổng cộng: 1.234.567 ₫` | Marks correct, periods surviving as group separators, `₫` a glyph |
| 5 | A name imported from a supplier spreadsheet | Same as test 1 — catches legacy encodings |
| 6 | Three item lines of differing lengths | Amount alignment holds |
| 7 | Product list sorted alphabetically | `đ` sorts after `d` |
| 8 | Reprint of a stored transaction | Identical to the original |

Test 5 is the one that catches the problem developers cannot reproduce, because
it is the only test using data nobody typed by hand.

## Notes for POS implementers

**Do not trust the code page alone.** CP1258 being selected is not evidence that
Vietnamese will print correctly. Print and look.

**Raster by default.**

**Normalise to NFC on import and before printing.**

**Test the import path, not just the print path.** Legacy-encoded supplier data
is the most common way a Vietnamese catalogue gets corrupted, and it happens
before anything reaches a printer.

---

_Maintained by the MISAll team. Last updated: 2026-08_
