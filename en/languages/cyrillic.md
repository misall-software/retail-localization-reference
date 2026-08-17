# Cyrillic — Four Code Pages, No Default, and Letters That Are Not What They Look Like

**Cyrillic is the easy script in this directory, and it fails in two ways the
other files do not cover.** It reads left to right. Letters do not join, so there
is no shaping engine and no positional forms. There are no stacking marks, no
dictionary line-breaking, and one column per character. Everything the Arabic,
Thai and CJK files spend pages on is simply absent.

What replaces it is quieter. **There is no default encoding.** Western Europe has
one legacy tradition and a printer you never configured is merely wrong about
accents; the Cyrillic world has two live traditions — DOS and Windows — that
disagree across the whole upper half of the byte range, plus a third that sorts
its letters in pseudo-Latin order. A printer's idea of Cyrillic is a per-model
fact, and the application's assumption is not the printer's.

**And a dozen Cyrillic letters are indistinguishable from Latin letters they are
not.** `С` is not `C`. `Р` is not `P`. `а` is not `a`. A product name typed half
in each script renders perfectly, prints perfectly, and matches nothing — so the
search returns empty, the import creates a second record, and the stock count
splits in two. That failure survives every review that does not compare bytes.

This file covers the engineering problems. It is not an introduction to any of
the languages that use the script.

> ### Verification status — unverified draft
>
> The Unicode and code page behaviour described here is specified and stable, and
> the codepoint-level claims were checked against the Unicode Character Database.
> The printer-specific values are not stable, and neither are the market
> conventions.
>
> **Open items — `TODO: verify`**
>
> 1. Every `ESC t` code page number, against the specific printer's own command
>    reference. Vendors renumber these, as noted in the Arabic file.
> 2. Whether the target printer has a Cyrillic ROM font at all, and which code
>    page reaches it.
> 3. **Which Cyrillic code page family the firmware implements — DOS (CP866) or
>    Windows (CP1251) — and which one it selects at power-on.** This is the first
>    question for a Cyrillic printer, and there is no safe default. See §5.
> 4. Whether the ROM font renders the 33 Russian letters at one column or two.
>    UAX #11 classes exactly those letters as Ambiguous width; a printer with a
>    CJK-derived font may print them double-width. See §8.
> 5. Whether the ruble sign `₽` (U+20BD) — or `₸`, `₴`, `⃀`, `₮` — is present in
>    the ROM font, or whether the ISO code must be printed instead.
> 6. Whether the target market mandates a fiscal device that owns the receipt
>    format and its encoding, in which case §5 is answered by that device's
>    specification rather than by the integrator.
> 7. Conventional symbol position, decimal separator and group separator on
>    retail documents in each target market, read from CLDR and confirmed against
>    sample receipts.
> 8. Whether any target market imposes legal requirements on receipt language, or
>    on the script in which tax figures must appear.
> 9. The current status of Kazakhstan's Cyrillic-to-Latin transition, and what it
>    implies for stored product data. See §9.
> 10. Bulgaria's post-euro price display rules. Secondary reporting places the end
>     of mandatory dual lev/euro display at **2026-08-08**, and one source gives a
>     different date. See §7.
> 11. Whether any target market's document rules require `ё` to be preserved
>     rather than folded to `е` in personal or company names. See §3.
> 12. Whether Bulgarian and Serbian localized letterforms matter for labels and
>     signage in the target market. See §9.

---

## 1. What Cyrillic does not need

Worth stating explicitly, because a team arriving from any other file in this
directory will carry machinery it can now delete:

| Elsewhere in this directory | Cyrillic |
| --- | --- |
| Right-to-left layout and the bidirectional algorithm (Arabic, Hebrew) | **Not applicable.** Left to right throughout. |
| Contextual shaping and positional forms (Arabic) | **Not applicable.** One form per letter. |
| Visual-versus-logical byte order (Hebrew) | **Does not arise.** |
| Dictionary-based line breaking (Thai) | **Not needed.** Words are whitespace-separated. |
| Marks stacking three and four deep (Thai, Vietnamese) | **None** in normal text. |
| Two columns per character (CJK) | **One column** — with one exception, in §8. |
| Multi-byte printer mode (CJK) | **Not needed.** Single-byte pages cover the Slavic set. |

What does carry over is the Latin-accented file's central warning: **the failure
is silent.** Cyrillic breaks in ways that leave the output looking like ordinary
Cyrillic to anyone who does not read it, and in one case (§2) looking correct
even to someone who does.

## 2. The homoglyph problem

This is the distinctive Cyrillic problem, and it is a data problem rather than a
rendering one. Nothing in the print path causes it and nothing in the print path
reveals it.

A group of Cyrillic letters is visually identical to a Latin letter with a
different codepoint:

| Cyrillic | Latin | | Cyrillic | Latin |
| --- | --- | --- | --- | --- |
| `А` U+0410 | `A` U+0041 | | `а` U+0430 | `a` U+0061 |
| `В` U+0412 | `B` U+0042 | | `е` U+0435 | `e` U+0065 |
| `Е` U+0415 | `E` U+0045 | | `о` U+043E | `o` U+006F |
| `К` U+041A | `K` U+004B | | `р` U+0440 | `p` U+0070 |
| `М` U+041C | `M` U+004D | | `с` U+0441 | `c` U+0063 |
| `Н` U+041D | `H` U+0048 | | `у` U+0443 | `y` U+0079 |
| `О` U+041E | `O` U+004F | | `х` U+0445 | `x` U+0078 |
| `Р` U+0420 | `P` U+0050 | | `і` U+0456 | `i` U+0069 |
| `С` U+0421 | `C` U+0043 | | `ј` U+0458 | `j` U+006A |
| `Т` U+0422 | `T` U+0054 | | `ѕ` U+0455 | `s` U+0073 |
| `У` U+0423 | `Y` U+0059 | | | |
| `Х` U+0425 | `X` U+0058 | | | |

The last three lowercase rows are Ukrainian, Serbian and Macedonian letters; a
Russian-only deployment sees the first seven. `І` U+0406 and `Ј` U+0408 pair with
uppercase `I` and `J` the same way.

**Where it bites.** In every case the string on screen is correct and the
comparison is not:

- A cashier searches for a product by name and gets nothing, because the record
  was entered with one script and the query typed in the other.
- A supplier catalogue import creates a new item instead of matching the existing
  one. Stock for one product now sits in two records, and neither is right.
- An article code or SKU entered on a Cyrillic keyboard layout — `С100` with a
  Cyrillic `С` — cannot be found by anyone typing it in Latin, and looks
  identical on the label.
- Two product records display the same name in the same list. Nothing about the
  list says why.
- A report exported to a spreadsheet fails a lookup at the accountant's end, and
  the accountant reasonably concludes the export is broken.

**The keyboard layout is the source.** Operators in these markets switch layouts
constantly, and the switch is modal — a Latin `c` and a Cyrillic `с` are the same
physical key. Nothing about the resulting string looks wrong at the moment of
entry, which is why this arrives through manual data entry far more often than
through import.

**Detection.** Classify the script of each letter and flag any *token* that
contains both. A mixed-script line is normal — a Cyrillic product name beside a
Latin brand is everyday data — so the signal is mixing inside one
whitespace-delimited token, not inside the line:

```python
import unicodedata

def scripts(token):
    found = set()
    for c in token:
        if not c.isalpha():
            continue
        name = unicodedata.name(c, "")
        found.add("Cyrillic" if name.startswith("CYRILLIC")
                  else "Latin" if name.startswith("LATIN")
                  else "other")
    return found

def suspect(token):
    return {"Cyrillic", "Latin"} <= scripts(token)
```

Three rules follow:

**Validate at entry, not only at migration.** This is not a legacy data problem
to be cleaned once. The keyboard is still there tomorrow. The check belongs on
product creation, on import and on code entry, permanently.

**Flag, never auto-convert.** By the time anyone runs this check, a mixed-script
record may have months of stock movements and sales history behind it. Converting
the string silently merges or orphans that history. Report the candidates and let
a human decide.

**Constrain the fields that do not need letters.** Article codes, SKUs and
internal references should reject Cyrillic letters outright, or reject letters
altogether. This removes the most damaging half of the problem by policy rather
than by detection.

## 3. Ё, Й, and the forms a letter arrives in

Two separate problems reach the same fix.

**Ё is often written as Е.** `ё` (U+0451) is a distinct letter, and Russian
printed matter routinely substitutes `е` for it — `ёлка`/`елка`, `Пётр`/`Петр`.
Both spellings occur in real catalogues, often in the same catalogue. A customer
searching one will not find the other.

Fold `ё` to `е` in **search input on both sides of the comparison**, and leave the
stored data alone. Folding stored data destroys a distinction that some documents
keep. `TODO: verify` whether any target market's document rules require `ё` to be
preserved in personal or company names.

**Ё and Й have canonical decompositions.** Checked against the Unicode Character
Database:

| Composed | Decomposes to | |
| --- | --- | --- |
| `Ё` U+0401 / `ё` U+0451 | `Е` U+0415 / `е` U+0435 + U+0308 | combining diaeresis |
| `Й` U+0419 / `й` U+0439 | `И` U+0418 / `и` U+0438 + U+0306 | combining breve |
| `Ў` U+040E / `ў` U+045E | `У` U+0423 / `у` U+0443 + U+0306 | Belarusian |
| `Ї` U+0407 / `ї` U+0457 | `І` U+0406 / `і` U+0456 + U+0308 | Ukrainian |

Decomposed input arrives from macOS filesystems, from some PDF extractions and
from web forms that never normalised. It is the Latin-accented file's failure in
Cyrillic clothing, and worse in one respect: **through a single-byte code page the
combining mark is dropped and `й` becomes `и`** — not a box, not a question mark,
a different letter that leaves a plausible Russian word behind. `Йогурт` prints as
`Иогурт`, which a Russian reader will notice and a reviewer will not.

It also inflates the character count by one, so column arithmetic disagrees with
printed width, and it breaks equality against a composed copy of the same string —
which puts it back into §2 territory.

Normalise to **NFC at import and again before printing**. Same rule as the
Latin-accented file, same reason.

## 4. Sorting is not codepoint order

Codepoint order is wrong for every Cyrillic language, and wrong most visibly for
Russian. The Russian alphabet places `Ё` immediately after `Е`, but the codepoints
do not:

| Letter | Codepoint | Where codepoint order files it |
| --- | --- | --- |
| `Ё` | U+0401 | **Before `А`** (U+0410) — first in the whole list |
| `А`…`Я` | U+0410–U+042F | uppercase block |
| `а`…`я` | U+0430–U+044F | lowercase block, entirely after uppercase |
| `ё` | U+0451 | **After `я`** (U+044F) — last in the whole list |

So a product list sorted on codepoints puts every `Ё` name at the very top and
every `ё` name at the very bottom, with the rest of the alphabet in between and
lowercase filed after uppercase. On a printed stock list this reads as data
corruption rather than as a sort order.

The other alphabets diverge further:

- **Ukrainian** orders `Ґ` after `Г`, and `Є`, `І`, `Ї` between `Е`/`Ж` and `Й` —
  but those letters sit at U+0490, U+0404, U+0406 and U+0407, outside the
  contiguous run.
- **Serbian** orders `Ђ Ј Љ Њ Ћ Џ` inside the alphabet (`Ђ` after `Д`, `Ј` after
  `И`, and so on), while their codepoints U+0402–U+040F all fall *before* `А`.
- **Bulgarian, Macedonian, Kazakh and Mongolian** each have their own order.

**Sort with ICU and the correct locale** — `ru`, `uk`, `sr`, `bg`, `kk`, `mn` —
not with a generic "Cyrillic" collation and never on bytes. The locale is part of
the answer, not a formality: the same string sorts differently under `ru` and `sr`.

One trap specific to legacy data: **KOI8-R does not store its letters in
alphabetical order at all.** Its byte order is a pseudo-Latin transliteration
sequence inherited from teletype practice. Anything that sorts on stored 8-bit
bytes from a KOI8 source is wrong in a third way, distinct from both codepoint
order and correct collation.

## 5. Four code pages, and no default

Most ESC/POS printers do not accept UTF-8. Text is sent as single-byte values
through a code page selected with `ESC t n`.

> `TODO: verify` — **the `n` value for each page is deliberately omitted here**,
> for the reason given in the Arabic file: vendors renumber the code page table,
> and clone firmware diverges from the Epson-documented ordering while claiming
> compatibility. Read it from the target printer's own command reference and
> confirm by printing.

| Page | Covers | Notes |
| --- | --- | --- |
| **Windows-1251** (CP1251) | Russian, Ukrainian, Belarusian, Bulgarian, Serbian, Macedonian | The Windows tradition and the usual application-side assumption. Uppercase at 0xC0–0xDF, lowercase at 0xE0–0xFF. **No ruble sign.** |
| **CP866** | Russian and Bulgarian fully; Ukrainian partially — has `Є є Ї ї`, lacks `Ґ ґ І і` | The DOS tradition, and common in thermal printer firmware. Letters at 0x80–0xAF and 0xE0–0xEF; **0xB0–0xDF is box-drawing characters**, which is what makes its mojibake recognisable. |
| **CP1125** | CP866 plus the missing Ukrainian letters | Ukrainian variant, filling the 0xF0 row. |
| **CP1131** | CP866 variant carrying Belarusian `Ў ў` alongside Ukrainian letters | Belarusian variant. |
| **KOI8-R** | Russian and Bulgarian | Letters in pseudo-Latin order, not alphabetical. Stripping the high bit yields a rough Latin transliteration — the design intent, and a useful fingerprint. |
| **KOI8-U** | KOI8-R plus Ukrainian | |
| **ISO-8859-5** | Slavic Cyrillic set | Rare in POS firmware; appears in data feeds. |
| **Mac Cyrillic** | Slavic Cyrillic set | Rare; turns up in files from older Mac systems. |

Four consequences.

**There is no default to fall back on.** CP866 and Windows-1251 are both current,
both plausible in firmware, and disagree about nearly every byte above 0x7F. A
printer that was never configured is not "probably about right" the way a CP437
printer is for English — it is either right or completely wrong, and which one is
not visible until something Cyrillic prints. Establish this before writing a
template.

**Windows-1251 covers the Slavic set only.** Kazakh, Tatar, Bashkir, Tajik,
Uzbek in Cyrillic and Mongolian all require letters — `ә ғ қ ң ө ұ ү һ і`, `Ө`,
`Ү`, `ҳ`, `ў` — that are not in it. Kazakhstan standardised its own altered
variant (STRK1048) for exactly this reason. For any of those markets the
single-byte path is not a compromise, it is a dead end: go to raster.

**The ruble sign cannot be encoded in any of them.** `₽` U+20BD was added in
Unicode 7.0, in 2014, long after all of these pages were fixed. §7 covers what to
do instead.

**A fiscal device may take the decision away from you.** Several Cyrillic-script
markets operate mandatory fiscal-device regimes in which the receipt is produced
by a registered device rather than by the application. Where that applies, the
code page, the template and the field order are specified by that device's
documentation, and this section is answered for you. Which markets, and what those
devices require, is `TODO: verify` — **this repository has no country file for any
Cyrillic-script market**, and nothing here should be read as covering it.

**When to use raster.** Rendering the receipt to a bitmap and sending it as a
graphic (`GS v 0`) removes the code page question, the glyph coverage question and
the ambiguous-width question in §8. For the Slavic set with a confirmed code page,
single-byte printing works and is faster — the Hebrew file's position, for the
same reason. **Beyond the Slavic set, raster is the path**, because no single-byte
page covers the repertoire.

## 6. Reading the mojibake

Cyrillic mojibake is diagnosable from the printed output, which makes a sample
print worth more here than in most of these files. What follows is derived from
the published code page layouts.

| What prints | What happened |
| --- | --- |
| **Box-drawing and line characters where capitals should be**, lowercase Cyrillic that is wrong but is letters, and stray `№ ¤ ■ √ °` | **Windows-1251 bytes into a CP866 printer.** CP1251's uppercase range 0xC0–0xDF lands in CP866's box-drawing block; its lowercase lands partly on the wrong letters and partly on the symbol row. The most common single failure in this script. |
| Curly quotes, dashes, `€`, `‰` and stray Serbian letters where capitals should be | **CP866 bytes read as Windows-1251.** CP866's uppercase range 0x80–0x9F is CP1251's punctuation area. |
| Two Latin-ish characters printed for every intended letter, many of them beginning `Р`, `С` or `Ð` | **UTF-8 bytes sent as if single-byte.** Cyrillic is two bytes in UTF-8, so the character count doubles — a reliable tell. |
| `?` or blanks, one per letter, ASCII unaffected | **Transcoded to a page with no Cyrillic** (CP437, CP850). The letters were destroyed at the encoder, before anything reached the printer. |
| Boxes, one per letter, evenly spaced | **No Cyrillic ROM font.** The code page is irrelevant — the printer has no glyphs to draw. |
| Correct Russian, but Ukrainian or Kazakh letters wrong or missing | **Right family, wrong variant** — CP866 where CP1125 was needed, or Windows-1251 where the Kazakh variant was. |
| Correct letters at twice the expected width | See §8. Not an encoding fault. |

**The distinction that decides what to fix:** question marks and blanks mean the
data was destroyed upstream and no printer setting will bring it back — fix the
encoder. Boxes mean the data arrived intact and the printer cannot draw it — fix
the font or switch to raster. They look similarly broken and have nothing in
common.

## 7. Currency symbols

| Sign | Codepoint | Currency | Note |
| --- | --- | --- | --- |
| `₽` | U+20BD | RUB | Added in **Unicode 7.0 (2014)**. In none of the code pages in §5. |
| `₸` | U+20B8 | KZT | |
| `₴` | U+20B4 | UAH | |
| `⃀` | U+20C0 | KGS | Newer still — absent from Unicode 13.0. Assume no ROM font has it. |
| `₮` | U+20AE | MNT | |

The Serbian dinar has no dedicated sign; `дин.` and `RSD` are both used.

**The traditional written abbreviations predate the signs and are still common in
print** — `руб.`, `грн.`, `тг.` — and on a receipt they have the advantage of
being encodable in any of the code pages in §5. Which form a market expects on a
retail document is convention rather than specification: `TODO: verify` against
sample receipts, and do not let a system default to the implementer's home
convention.

**Where the symbol cannot be printed, print the ISO code.** `RUB` beats a box in
the price field. This is the Arabic and Hebrew files' rule and it applies here
with more force, because the ruble sign is not merely uncertain in ROM fonts — it
is absent from every legacy code page by construction.

**Separators.** CLDR records a **comma decimal separator and a space group
separator** for `ru`, `uk` and `kk`: `1 234,56`. Read the values from CLDR per
market rather than hard-coding them, and note that the group separator is a space
character — which is a line-breaking hazard as well as a formatting one, so use a
no-break space and confirm it survives the print path.

**Bulgaria switched currency during this repository's lifetime.** Bulgaria adopted
the euro on **2026-01-01**, replacing the lev at a fixed rate of 1.95583 BGN to
1 EUR, with the lev ceasing to be legal tender on 2026-02-01. A mandatory dual
lev/euro price display ran from 2025-08-08; secondary reporting places its end at
**2026-08-08**, after which the euro price is the payable one and any lev figure
is informational only. **Sources disagree** — one gives 2026-06-30 for the end of
dual display, which may be the end of free bank exchange rather than of dual
pricing. All of this is secondary reporting, none is confirmed against the
Bulgarian authorities, and there is no Bulgaria country file here. `TODO: verify`
before configuring a till in that market.

## 8. Width: one column, except when it is two

Cyrillic is single-width. One column per character, no wide characters, no
zero-width marks in normal text — so the column arithmetic that the Arabic,
Hebrew, Thai and CJK files all have to correct is simply correct here.

**With one exception, and it is a real one.** UAX #11 assigns the East Asian Width
class **Ambiguous** to exactly the Russian alphabet — U+0401, U+0410–U+044F,
U+0451 — and **Narrow** to everything else in the Cyrillic block. Ambiguous
characters "can be sometimes wide and sometimes narrow"; they render full-width in
an East Asian font context and narrow elsewhere.

The consequence for a POS is specific:

- A printer whose ROM font is CJK-derived — common on hardware built for the
  Chinese domestic market and resold elsewhere — may render Russian letters at
  **two columns each**, halving the usable line and breaking every alignment
  calculation, while the encoding is entirely correct.
- Because the Ambiguous set is *exactly* the Russian alphabet, the letters outside
  it stay narrow. A Ukrainian word containing `і` or `ї`, or a Kazakh word
  containing `ә` or `ң`, can therefore print with **mixed widths inside a single
  word**. That is not a plausible encoding fault, and it is worth recognising as
  the font-context problem it is rather than debugging the code page.

Measure the width empirically on the target hardware rather than assuming, exactly
as the CJK file says about its own ambiguous characters. `TODO: verify` per model.

**Line budget.** At 80 mm and 48 columns, a 12-column amount field leaves 35
columns for the description. Russian retail names run long and there is no
compensating density — unlike CJK, a Cyrillic character carries about as much
meaning as a Latin one — so two-line item names are ordinary rather than
exceptional. At 58 mm and 32 columns, budget two lines for the name and put the
amount beneath it. If the ambiguous-width behaviour above applies, halve all of
these numbers.

## 9. Where two scripts write the same language

**Serbian is digraphic.** Cyrillic and Latin are both in use for the same
language, readers use both, and a Serbian catalogue can legitimately contain
either or both. Transliteration is close to letter-for-letter, but not
length-preserving: `Љ Њ Џ` become the Latin digraphs `Lj Nj Dž`, so a converted
name is longer and a round trip is not guaranteed. Store what the customer is
meant to see; do not convert silently at print time.

**Bulgarian and Serbian use different letterforms for the same codepoints.**
`б г д п т` are drawn differently in the Bulgarian and Serbian traditions from the
Russian ones. A real font handles this through language-tagged alternates; a
thermal printer's ROM font has one set of shapes, normally the Russian ones. This
does not affect whether a receipt is readable, and it can affect shelf labels,
signage and anything laid out with a real font. Convention rather than
specification — `TODO: verify` whether it matters in the target market before
spending anything on it.

**Kazakhstan is mid-transition from Cyrillic to Latin**, and the timetable has
moved more than once. `TODO: verify` the current position. The implication for a
POS does not depend on the date: for years, both scripts will be present in real
data, the same product will exist under two names, and search has to cross the
scripts. Plan for two name fields, not for a conversion.

**Uzbekistan** uses Latin officially with Cyrillic still widely read; **Mongolia**
uses Cyrillic with `Ө` and `Ү`, outside Windows-1251.

## 10. Test matrix

Print on the target hardware. Screen output proves nothing, because the operating
system's text engine does work the printer path does not.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | `Итого` (total) alone | Prints as letters, no boxes |
| 2 | An all-capitals word, e.g. `МОЛОКО` | Capitals print as letters, **not as box-drawing characters** — this is the CP1251-into-CP866 test |
| 3 | `Ёлка` and `ёж` | Both `Ё` and `ё` print, and are not silently `Е`/`е` |
| 4 | `Йогурт` | The breve over `й` is present — catches decomposed input surviving to the printer |
| 5 | A word using a letter of the target market's own alphabet — `ґ і ї` for Ukrainian, `ә ң ө ұ ү` for Kazakh, `ө ү` for Mongolian | Prints; also confirms the code page **variant**, not just the family |
| 6 | An item name mixing Cyrillic with a Latin brand | Both readable on one line |
| 7 | `₽` (or `₸`, `₴`) in a total line | A glyph prints, not a box or a blank |
| 8 | `1 234,56` with the market's separators | Separators as configured; the group space does not become a line break |
| 9 | Three item lines of differing name lengths | Decimal separators align vertically — catches ambiguous double-width |
| 10 | The longest real product name, at 80 mm then 58 mm | Both readable; 58 mm wraps rather than squeezes |
| 11 | `-10%` beside Cyrillic text | Sign and percent stay attached |
| 12 | Reprint of a stored transaction | Identical to the original |
| 13 | A sorted product list including names starting `Ё` and `Э` | `Ё` files immediately after `Е`, not first or last in the list |
| 14 | Search for a name deliberately typed with a Latin `с` or `а` | The system flags it rather than silently creating a second record |

Tests 13 and 14 are not print tests, and they are the two that catch the failures
in §2 and §4 — the ones a native reader looking at a sample receipt will pass
without noticing.

Have the printed output read by someone who reads the target language. Test 4 is
the one a non-reader will pass.

## 11. Where this applies

Cyrillic is the retail script in **Russia, Belarus, Kazakhstan, Kyrgyzstan,
Tajikistan, Mongolia, Serbia, North Macedonia and Montenegro**, and in **Ukraine**;
in **Bulgaria** alongside a currency that changed in 2026 (§7); and in
**Uzbekistan** alongside Latin. Chinese-owned retail and food service is
long-established in several of these markets.

**None of them has a country file in this repository.** Tax rates, fiscal device
requirements, invoicing rules and mandatory receipt content are therefore **not**
documented here, and nothing in this file should be read as covering them. Several
of these markets are understood to operate mandatory fiscal-device regimes, which
would constrain the receipt template and possibly its encoding — that is item 6 in
the verification list, and it is unresearched rather than answered.

The familiar three-way split applies: a shop may need a Cyrillic till interface, a
different back-office language for an owner who does not read Cyrillic, and a
print template language chosen independently of both. Only the print template
drives §5 through §8; §2 through §4 apply to the back office as well, and in fact
apply hardest there, because that is where product data is created.

## Notes for POS implementers

**Establish the printer's code page family before writing a template, or go
raster.** DOS and Windows Cyrillic are both live, they disagree everywhere above
0x7F, and no default is safer than the other. This is the Cyrillic equivalent of
the Hebrew byte-order question: per-model, not discoverable at runtime, and cheap
to settle with one sample print.

**Treat the homoglyph check as permanent input validation, not a migration.** The
keyboard that produces mixed-script strings is still attached tomorrow. Flag,
never auto-convert, and forbid letters outright in code and SKU fields.

**Normalise to NFC at import and before printing.** A decomposed `й` loses its
breve through a single-byte page and becomes `и` — a different letter in a
still-plausible word.

**Sort with ICU and a real locale.** Codepoint order files `Ё` first and `ё` last
in Russian, and misplaces the whole Serbian and Ukrainian alphabets. A stock list
in that order reads as corruption.

**Print the ISO code when the symbol is uncertain.** `₽` is absent from every
legacy Cyrillic code page by construction, not merely uncertain in ROM fonts.
`RUB` in the price field beats a box.

**Beyond Russian, Ukrainian, Belarusian, Bulgarian, Serbian and Macedonian, stop
looking for a code page.** Kazakh, Mongolian, Tatar, Tajik and Uzbek Cyrillic are
not covered by any of them. Raster is the answer, and knowing that early saves a
procurement cycle.

**Check whether the market puts a fiscal device between you and the paper.** If it
does, the questions in §5 are answered by that device's specification, and the
integration is a different job from the one this file describes.

---

_Maintained by the MISAll team. Last updated: 2026-08_
