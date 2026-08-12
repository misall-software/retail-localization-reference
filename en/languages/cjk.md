# Chinese, Japanese and Korean — Receipt Layout and Printing

**One CJK character occupies two columns, and almost every alignment bug on a
CJK receipt comes from code that assumed it occupied one.** A 48-column line
holds 48 Latin characters or 24 Chinese ones, and a line mixing the two holds
something in between that has to be computed rather than counted. On top of that,
CJK needs a font the printer may not have, a separate character mode to reach it,
and line-breaking rules that have nothing to do with whitespace.

This matters even where the customer-facing receipt is not in Chinese: a shop
whose back office runs in Chinese still prints Chinese on internal documents —
purchase orders, stock counts, shelf labels, kitchen tickets.

> ### Verification status
>
> The Unicode width and line-breaking behaviour described here is specified and
> stable. The printer-specific values are not.
>
> **Open items — `TODO: verify`**
>
> 1. Whether the target printer has a CJK font in ROM at all, and for which of
>    the three scripts.
> 2. The exact command values for entering and leaving multi-byte character mode
>    on the target printer.
> 3. Which encoding the printer's CJK mode expects — this is not always the one
>    the vendor's documentation claims.
> 4. Whether the ROM font covers the specific characters in the catalogue,
>    including rare surname characters and Traditional forms.

---

## 1. Width is the whole problem

Unicode defines an East Asian Width property (UAX #11). Characters are Wide,
Narrow, Fullwidth, Halfwidth, Ambiguous or Neutral. For a fixed-pitch thermal
printer the practical rule is:

| Character class | Columns |
| --- | --- |
| Han (漢字), Hiragana, Katakana, Hangul | **2** |
| Fullwidth forms — `：`, `（`, `１` | **2** |
| CJK punctuation — `。`, `、`, `《` | **2** |
| Halfwidth Katakana — `ｱ`, `ﾞ` | **1** |
| Latin, digits, ASCII punctuation | 1 |

So `len(s)` is wrong, and it is wrong in the direction that silently overflows a
line. The fix is a display-width function:

```python
import unicodedata

def width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else
               0 if unicodedata.combining(c) else 1
               for c in s)
```

Pad with this, truncate with this, and compute the item-name column with this.
Every language in this repository that has an alignment problem — Arabic, Thai,
Vietnamese — has a variant of the same bug; CJK is where it bites hardest because
the error is a factor of two rather than a stray column.

**Ambiguous width is a real trap.** Characters like `°`, `±`, `←` and the Greek
letters are classed Ambiguous: one column in a Western context, two in a CJK
font. The printer decides, not the standard. If a catalogue uses them, measure
them empirically on the target hardware rather than trusting the property.

### The 80 mm line budget

At 48 columns, a two-column layout with a 12-column amount field leaves 35
columns for the description — that is **17 Chinese characters**, not 35. Product
names routinely exceed it. At 58 mm and 32 columns the description column is
around 19 columns, or **9 Chinese characters**, which fits almost nothing.

Plan for the name on its own line at 58 mm. This is not a degraded layout; it is
the only workable one.

## 2. Line breaking

CJK breaks between almost any two characters — no whitespace required. That makes
wrapping easy and makes naive wrapping look wrong, because there are rules about
where a break may *not* fall. These are the kinsoku rules:

- **Closing punctuation may not start a line**: `。`, `，`, `、`, `）`, `」`, `》`
- **Opening punctuation may not end a line**: `（`, `「`, `《`
- A number and its unit should not be split
- Latin words embedded in CJK text still break on whitespace, not mid-word

A receipt is short enough that the cheap fix is usually sufficient: when a break
would place forbidden punctuation at the start of a line, pull the preceding
character down with it.

## 3. Getting the bytes to the printer

Most ESC/POS printers do not accept UTF-8. For CJK there is an additional layer
beyond the single-byte code pages used elsewhere: a **multi-byte character mode**
that must be entered explicitly, after which the printer interprets byte pairs
through a CJK font in ROM.

| Script | Encodings commonly expected |
| --- | --- |
| Simplified Chinese | GB18030, GBK, GB2312 |
| Traditional Chinese | Big5 |
| Japanese | Shift_JIS |
| Korean | EUC-KR |

`TODO: verify` all of the following on the target model, because vendor
documentation is frequently wrong about them:

- Whether a CJK ROM font is present at all. **Printers sold into Western markets
  frequently have none**, and will print boxes or nothing regardless of what you
  send. This is the single most common cause of "it works on my desk and not at
  the customer".
- The commands to enter and leave multi-byte mode, and whether they must bracket
  every CJK run or can be set once.
- Which encoding that mode actually expects.
- Whether the ROM covers your characters. Rare surname characters and Traditional
  forms are where coverage runs out, and a customer's own shop name is exactly
  where a missing glyph is least acceptable.

**Simplified and Traditional are not interchangeable.** A catalogue in one may
be partly unreadable in a market using the other, and converting is not a
character-by-character mapping — one simplified form can correspond to several
traditional ones. Treat them as separate name fields where both markets are
served, not as a runtime conversion.

## 4. Raster rendering

As with Arabic and Thai, rendering the receipt to a bitmap and sending it as a
graphic removes the font question, the encoding question and the mode-switching
question in one step. What is rendered is what prints.

For CJK this is more attractive than elsewhere, because the alternative depends
on a ROM font whose coverage you cannot inspect and cannot fix. The cost is the
usual one: more data, slower printing, and the printer's own size and emphasis
commands no longer apply.

Where a deployment prints Chinese back-office documents *and* a local-language
receipt — the normal case in this repository — raster gives one print path for
both instead of two.

## 5. Test matrix

Print on the target hardware. Screen output proves nothing.

| # | Test | Passes when |
| --- | --- | --- |
| 1 | A Chinese product name | Characters print; no boxes, no blanks |
| 2 | A line mixing Chinese and a Latin brand | Column boundaries land where intended |
| 3 | Three item lines of differing name lengths | Amount decimal points align vertically |
| 4 | A name long enough to wrap | Break is not before `。` or `，` |
| 5 | A rare surname character, and the shop's own name | Prints rather than falling back to a box |
| 6 | Traditional forms, if the market uses them | Print correctly |
| 7 | Halfwidth katakana, for Japanese | Occupies one column, not two |
| 8 | Full receipt at 80 mm, then 58 mm | Both readable; 58 mm stacks rather than squeezes |
| 9 | Reprint of a stored transaction | Identical to the original |

## 6. Where this applies

Chinese is the back-office language across most deployments in this repository,
which makes this file relevant to every country in it, not only to the markets
where Chinese appears on the customer receipt.

It reaches customer-facing output directly in **Malaysia**, where Chinese is in
genuine commercial use, and on **kitchen tickets** wherever a Chinese-owned
restaurant runs a Chinese-reading kitchen — see the food service sections.

Japanese and Korean appear in their own markets and in Japanese and Korean
restaurant segments abroad.

## Notes for POS implementers

**Replace every length calculation in the print path.** If any part of the
receipt template measures with a plain character count, it is wrong for CJK. This
is a mechanical change and it is worth doing before anything else.

**Decide the print path per printer model, and record it.** ROM font presence is
a per-model fact that cannot be discovered at runtime and produces unreadable
output when assumed wrongly — the same warning as the Arabic file, for the same
reason.

**Two name fields, not one.** The pattern documented throughout this repository —
an internal name the owner reads and a local-language name the customer reads —
is what makes CJK back-office output and local-language receipts coexist.

---

_Maintained by the MISAll team. Last updated: 2026-08_
