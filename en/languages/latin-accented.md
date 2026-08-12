# Accented Latin Scripts — Receipt Printing

**These are the languages that look safe and are not.** Spanish, Portuguese,
French, German, Italian, Indonesian, Malay, Turkish and the Nordic languages all
use the Latin alphabet, so a template built for English appears to work — until a
product name contains `ñ`, `ç`, `ã` or `ü` and the printer emits the wrong glyph.

The failure mode is what makes this file necessary: **the output is still
readable**. `Piña` printing as `Pina`, `São` as `Sao`, `Größe` as `GrOSe` — none
of these look like a bug to someone testing with clean data, and all of them pass
review. Arabic and Thai fail loudly; these fail quietly and reach production.

> ### Verification status
>
> Unicode behaviour here is stable. Code page numbering is vendor-specific.
>
> **Open items — `TODO: verify`**
>
> 1. Which code page the target printer uses for the intended market, and its
>    numeric selector value.
> 2. Whether the ROM font covers every character the catalogue uses — check the
>    less common ones rather than the vowels.
> 3. Whether supplier-provided product data arrives in a legacy encoding.

---

## 1. The repertoire is larger than it looks

| Language | Characters beyond ASCII |
| --- | --- |
| Spanish | `ñ Ñ á é í ó ú ü ¿ ¡` |
| Portuguese | `ã õ á â à é ê í ó ô ú ç` |
| French | `é è ê ë à â ù û î ï ô ç œ æ` |
| German | `ä ö ü ß` (and `ẞ`) |
| Italian | `à è é ì ò ù` |
| Turkish | `ç ğ ı İ ö ş ü` — note dotted and dotless i |
| Indonesian / Malay | none in normal commercial use |
| Nordic | `å ä ö æ ø` |

Two of these deserve attention beyond the accented vowels:

**Spanish inverted punctuation.** `¿` and `¡` are not decorative; a question
written without the opening mark reads as incomplete. They sit outside ASCII and
are frequently the first thing to break.

**Turkish dotted and dotless i.** `i` uppercases to `İ`, and `ı` uppercases to
`I`. A naive `toUpperCase()` on a Turkish product name produces a different word.
If the receipt template upper-cases anything, this is a real defect, not a
cosmetic one.

**German ß** has an uppercase form `ẞ` that many fonts lack; the conventional
fallback is `SS`, which changes the string length and therefore the column width.

## 2. Getting the bytes right

Most ESC/POS printers do not accept UTF-8. Text is sent as single bytes
interpreted through a selected code page.

| Code page | Covers |
| --- | --- |
| CP850 | Western European, DOS-era, widely present in printer ROM |
| CP858 | CP850 plus the euro sign |
| Windows-1252 | Western European, the usual Windows encoding |
| CP860 | Portuguese |
| ISO-8859-1 / -15 | Latin-1 and its euro-bearing revision |
| Windows-1254 | Turkish |

The default page on a printer out of the box is usually **CP437**, which is US
English and covers almost none of the above. A printer that has never had its
code page set will mangle every accented character, and this is the most common
single cause of the problem.

`TODO: verify` the numeric selector for the chosen page on the target model —
vendor numbering diverges, as documented in the Arabic file.

**The euro sign is a recurring nuisance.** It is absent from CP850 and from
ISO-8859-1. If prices are in euros, either select a page that has it (CP858,
Windows-1252, ISO-8859-15) or print `EUR`.

## 3. Precomposed versus decomposed

`é` can be one codepoint (U+00E9) or two (`e` + U+0301). They look identical on
screen and are not the same bytes. Data arriving from a supplier spreadsheet, a
web form, or a macOS filesystem may be decomposed.

A decomposed string sent through a single-byte code page loses the accent
entirely — the base letter encodes and the combining mark does not. **Normalise
to NFC on import and again before printing.** This one line of code removes a
whole class of intermittent, unreproducible accent bugs.

It also fixes a quieter problem: a decomposed string has more codepoints than a
precomposed one, so any column calculation based on character count disagrees
with the printed width. Normalising makes the two agree.

## 4. Column width

Unlike CJK, every character here is one column wide, so width equals count —
**after** normalisation. Before it, combining marks inflate the count and
under-pad the line.

The practical issue is not width per character but length per word. Spanish and
Portuguese descriptions run roughly a fifth longer than their English
equivalents, French and German longer still, and German compounds produce single
unbreakable words that no column width accommodates. A description column sized
from English test data will truncate in production; size it from real catalogue
data in the target language.

## 5. Test matrix

Print on the target hardware, with real supplier data rather than clean test
strings.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | `Piña colada`, `São Paulo`, `Crème brûlée`, `Größe` | Accents present, not silently stripped |
| 2 | `¿Cuánto?` `¡Gracias!` | Inverted marks print |
| 3 | The currency symbol for the market | A glyph, not a box |
| 4 | A name copied from a supplier spreadsheet | Same as test 1 — catches decomposed input |
| 5 | Any upper-cased text, in Turkish | `i` becomes `İ`, not `I` |
| 6 | Long German or Portuguese description | Wraps rather than truncating mid-word |
| 7 | Reprint of a stored transaction | Identical to the original |

Test 4 is the one most often skipped and most often fails, because it is the only
test that uses data the developer did not type.

## 6. Where this applies

Directly on the customer receipt in **Peru** (Spanish), and across the Spanish-
and Portuguese-speaking markets generally. **Indonesia** and **Malaysia** use
Latin script with no diacritics in normal commercial use, so they are unaffected —
which is worth knowing, because it means those two markets need no code page work
at all.

French is relevant in the Maghreb, where it appears on receipts alongside Arabic —
see the Arabic file for the mixed-direction consequences.

## Notes for POS implementers

**Set the code page explicitly.** Never rely on the printer default. This is one
line of initialisation and it prevents the most common failure here.

**Normalise to NFC on import and before printing.**

**Test with supplier data, not typed data.** Every subtle failure in this file
survives testing with strings a developer typed by hand.

**When in doubt, raster.** The reasoning in the Arabic, Thai and CJK files applies
here too, with the caveat that these languages are the ones least likely to need
it — a correctly selected code page genuinely suffices for Spanish or Portuguese
alone. Raster becomes worthwhile once a Chinese-language back office shares the
same print path.

---

_Maintained by the MISAll team. Last updated: 2026-08_
