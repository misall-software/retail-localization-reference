# Thailand — Retail & POS Localization

**Two things define a Thai deployment: a VAT rate with an expiry date, and a
script that breaks naive text layout.** VAT sits at 7% against a statutory 10%,
extended by cabinet decision and currently reported as running to 30 September
2026 — the nearest expiry of any rate in this repository. Separately, Thai is
written without spaces between words and stacks vowel and tone marks above and
below the base letter, which defeats both line-breaking and column alignment code
written for European scripts. E-tax invoicing, by contrast, remains voluntary.

> ### Verification status — partially verified, 2026-08
>
> Checked against secondary sources. Confirm against the Revenue Department before
> relying on any of it.
>
> **Resolved this pass**
>
> - VAT **7%** against a statutory 10%, reported as extended to **30 September
>   2026**. Nearest expiry in this repository — see below.
> - E-Tax Invoice and e-Receipt is **voluntary**; no legislated B2B mandate
>   reported for 2026 or 2027.
> - Where used, the system works in XML with PDF/A-3, under RD STD 03-2566,
>   secured by a qualified digital signature or an ETDA time stamp, with monthly
>   transmission by the 15th of the following month.
> - A tax invoice must carry the **13-digit TIN of both buyer and seller**, the
>   date, a description, and VAT as a separate line. Omitting any of these blocks
>   the buyer's input VAT claim.
>
> **Still open — `TODO: verify`**
>
> 1. Whether the 7% rate has been extended beyond 2026-09-30, and what applies
>    from 1 October 2026. **This is the most urgent item in this file.**
> 2. Whether displayed consumer prices are legally required to be tax-inclusive.
> 3. Mandatory fields for a simple retail receipt as distinct from a full tax
>    invoice.
> 4. Whether the Buddhist Era calendar is required, permitted or merely customary
>    on receipts.
> 5. Thai code page support on the target printer.
> 6. VAT registration threshold.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `THB` | official-authority |
| Symbol | `฿` (U+0E3F) | official-authority |
| Symbol position | Prefix — `฿1,250.00` | unverified |
| Decimal places | 2 | official-authority |
| Thousands separator | `,`; decimal separator `.` | unverified |
| Typical price magnitude | Roughly 20 to 5,000 THB for everyday retail lines | unverified |

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | **7%**, a reduction from the statutory 10%, reported as extended **to 30 September 2026**. | public-regulation |
| Tax-inclusive or exclusive display | Consumer prices quoted VAT-inclusive in ordinary practice. `TODO: verify` legal basis. | unverified |
| Fiscal system name | Revenue Department. **e-Tax Invoice & e-Receipt — voluntary**, with tax incentives for adoption rather than a mandate. | official-authority |

**The expiry is the point.** A rate that has been extended repeatedly by cabinet
decision is not a constant, and this one has the nearest horizon of anything in
this repository. Any system deployed in Thailand needs VAT as a dated, editable
record with effective-from and effective-to dates, and historical transactions must
retain the rate that applied on their own date. If 7% is compiled in, the failure
mode after 30 September 2026 is silently wrong tax on every sale.

**Tax invoice versus receipt.** The 13-digit TIN of *both* parties is required on a
tax invoice. That means a business customer's TIN has to be capturable at the
counter, often after the sale has been rung up — decide whether that is a
mid-transaction edit or a separate issuance before designing the flow.
`TODO: verify` what a simple retail receipt must contain by contrast.

## Receipt requirements

`TODO: verify` the mandatory field list for a retail receipt. For a full tax
invoice the confirmed elements are: seller TIN (13 digits), buyer TIN (13 digits),
date, description of goods or services, and VAT shown as a separate line.

**Paper widths:** 80 mm (48 or 42 characters at Font A) and 58 mm (32).

**Calendar.** Thailand commonly uses the Buddhist Era, 543 years ahead of the
Common Era — 2026 CE is 2569 BE. Dates on Thai commercial documents may be
expected in BE. `TODO: verify` whether this is required, permitted or customary.
Whatever the answer, store dates in a single canonical form and convert at render
time; storing BE dates guarantees an off-by-543 bug somewhere downstream.

## Languages used in retail

Thai is the working language of retail, and it is the harder half of this file.

**No spaces between words.** Thai text runs continuously; word boundaries are
implicit. Line breaking therefore cannot be done by splitting on whitespace — a
naive wrap breaks mid-word, which in Thai produces something between unreadable
and wrong. Correct wrapping needs a dictionary-based or ICU-style line-break
algorithm. `TODO: verify` what the chosen rendering path provides.

**Stacked marks.** Thai places vowel signs above and below the consonant and adds
tone marks above those, so a single displayed cluster can be three or four
codepoints tall. Two consequences, both familiar from the Arabic file:

- **Column alignment computed on string length is wrong.** Combining marks occupy
  no horizontal column. Measure display width, not codepoint count.
- **Line height must accommodate the stack.** Tight leading clips the upper tone
  marks, which is legible enough to pass review by a non-reader and wrong to a
  Thai reader.

**Encoding.** Thai needs a dedicated code page — TIS-620 and its Windows variant
CP874 are the usual candidates. `TODO: verify` support and the `ESC t` value on the
target printer; as elsewhere, vendor numbering varies. Raster rendering avoids the
code page question and, given the line-breaking requirement above, is the
recommended default here.

**Deployment pattern.** Chinese-owned businesses commonly pair a Chinese back
office with a Thai till and Thai receipts. Products need two names — a Thai one
for the customer-facing output, an internal one the owner can read.

## Payment methods

| Method | Notes |
| --- | --- |
| PromptPay | The national QR and account-proxy transfer rail; dominant for non-cash, including small amounts. Confirmation is visual at the counter. |
| Cash | Still substantial. |
| Cards | Widely accepted in urban retail through bank terminals. |
| E-wallets | Present alongside PromptPay. |

## Notes for POS implementers

**Put the rate expiry in the deployment checklist.** 30 September 2026 is close
enough that a system going live now will cross it.

**Test Thai rendering on hardware, with a Thai reader.** Clipped tone marks and
mid-word breaks are exactly the failures that survive a review by someone who does
not read the script — the same trap documented in the Arabic file.

**Time zone.** UTC+7, no daylight saving.

---

_Last updated: 2026-08_
