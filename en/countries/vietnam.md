# Vietnam — Retail & POS Localization

**Vietnam separates the receipt from the invoice.** The slip handed to the
customer at the counter and the legal e-invoice registered with the tax authority
are two different documents, and conflating them is the most common structural
mistake in a Vietnamese POS deployment. Currency is the dong (VND), which has no
minor unit in practice and produces very large printed numbers. The interface
language is Vietnamese, whose diacritics break more thermal printers than any
other Latin-script language.

> ### Verification status — partially verified, 2026-08
>
> Items 1, 2, 5, 6 and 8 below have been checked against secondary sources and are
> recorded in the body with their governing instruments. **Secondary sources are
> not primary sources**: confirm against the instrument text or the tax
> administration before relying on any of it.
>
> **Resolved this pass — reconfirm before publishing**
>
> - Standard rate 10%; temporary reduction to 8% in force **to 31 December 2026**
>   under Resolution 204/2025/QH15, implemented by Decree 174/2025/ND-CP.
> - Decree 123/2020/ND-CP as amended by **Decree 70/2025/ND-CP, effective
>   1 June 2025**.
> - Cash-register e-invoice obligation extends to household and individual
>   businesses with annual revenue at or above **VND 1 billion**, plus named
>   retail, restaurant, hotel, transport and entertainment sectors.
> - A digital signature is **not** mandatory on cash-register e-invoices.
>
> **Still open — `TODO: verify`**
>
> 1. Exactly which goods and services fall inside the 8% reduction, and how a
>    retail catalogue maps onto that list. The exclusions are sector-based and
>    the boundary is where the errors live.
> 2. What happens on 1 January 2027 when the reduction lapses, and whether a
>    further extension has been enacted by then.
> 3. Which reduced (5%) and zero rates apply to specific retail goods.
> 4. Whether displayed consumer prices are legally required to be VAT-inclusive.
> 5. The full mandatory field list for a cash-register e-invoice.
> 6. Whether a QR or lookup code is mandatory on the printed representation, and
>    what it must encode.
> 7. Timing rules — when the invoice must be issued relative to the sale, and what
>    is permitted when the connection is unavailable.
> 8. Tax code (MST) format and validation rules.
> 9. Whether the printed counter slip is itself regulated, or only the e-invoice.
> 10. The authority's current portal URL for each of the above.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `VND` | official-authority |
| Symbol | `₫` (U+20AB). Also written `đ`, and `VNĐ` in running text. | official-authority |
| Symbol position | Suffix — `150.000 ₫`. | unverified |
| Decimal places | 0 in practice. `TODO: verify` whether a minor unit remains defined but unused. | unverified |
| Thousands separator | `.` (period) — decimal separator `,` (comma), following Vietnamese convention. Software defaulting to English conventions inverts both. | unverified |
| Typical price magnitude | Roughly 10,000 to 10,000,000 VND for everyday retail lines; a bottle of water is five figures. Order of magnitude only, given here to size fields. | unverified |

Confirm the code, symbol and subdivision against the State Bank of Vietnam.

**Formatting consequences.** This is the field-width case that breaks templates
built elsewhere. Seven to nine integer digits plus separators is routine, and a
wholesale total can run longer. An amount column sized for `1,234.56` will
overflow on the first sale.

Digit grouping is not cosmetic here — it is what makes a seven-digit number
readable at a glance, and its absence causes real miskeying at the counter. Group
by three, and use the period, not the comma. Because there is no fractional part,
alignment is on the last digit rather than on a decimal point, which simplifies
column layout — but only if the formatter is genuinely configured for zero
decimals rather than rendering `150.000,00`.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | Standard rate 10%, **temporarily reduced to 8% through 31 December 2026** under Resolution 204/2025/QH15, implemented by Decree 174/2025/ND-CP, running from 1 July 2025. A 5% reduced rate and a 0% export rate also exist. The reduction excludes named sectors — telecommunications, real estate, finance, banking, securities and insurance among them — so it is not a blanket 8%. | public-regulation |
| Tax-inclusive or exclusive display | Consumer-facing retail prices are quoted VAT-inclusive in ordinary practice. `TODO: verify` whether this is a legal display requirement. | unverified |
| Fiscal system name | Electronic invoicing (hóa đơn điện tử), administered by the tax administration under the Ministry of Finance. Retail and food service fall under e-invoices generated from cash registers (hóa đơn điện tử khởi tạo từ máy tính tiền). Governing framework: **Decree 123/2020/ND-CP as amended by Decree 70/2025/ND-CP, effective 1 June 2025**. | public-regulation |
| Who must issue cash-register e-invoices | Household and individual businesses with annual revenue of **VND 1 billion or more**, plus enterprises in retail (shopping centres, supermarkets, retail stores), restaurants and catering, hotels, passenger transport, and entertainment. Registers must be connected to the tax authority's system for per-invoice transmission. | public-regulation |
| Digital signature | **Not mandatory** on e-invoices generated from cash registers, unlike standard e-invoices. | public-regulation |

**Do not hardcode the rate, and note the date.** The reduction has been extended by
successive instruments, each covering a defined period and an enumerated set of
goods. The current one **lapses on 31 December 2026** — a system deployed in 2026
with 8% written into it produces wrong tax from 1 January 2027 unless a further
extension is enacted, and it will do so silently.

A deployment that survives a rate change needs VAT rates as dated, editable
records with effective-from and effective-to dates, and needs historical sales to
keep the rate that applied on their own transaction date. Reprinting a receipt
from last year at this year's rate is a defect, not a rounding difference.

The same structure handles the coverage problem: because the reduction applies to
some categories and not others, the rate has to attach to the product's tax
category, and the category-to-rate mapping has to be editable without a software
release.

## Receipt requirements

### Mandatory fields

Fields commonly required on a cash-register e-invoice. This is a starting point
for verification, **not a confirmed specification** — `TODO: verify` the complete
list and which fields are conditional.

- Seller name, address, and tax code (MST) — `public-regulation`
- Buyer name and tax code, where the buyer requests an invoice for deduction — `public-regulation`
- Invoice form and serial symbol, and invoice number — `public-regulation`
- Date of issue — `public-regulation`
- Item name, unit of measure, quantity, unit price, line amount — `public-regulation`
- VAT rate and VAT amount — `public-regulation`
- Total payable — `public-regulation`
- Seller's digital signature — `public-regulation`
- Tax authority code, where applicable — `public-regulation` `TODO: verify`

### QR code

`TODO: verify` whether a QR or lookup code is mandatory on the printed
representation and what it must encode. A lookup reference allowing the customer
to retrieve the registered invoice is commonly present in practice; treat its
legal status as open until confirmed.

### Common paper widths

- **80 mm** — the default for fixed counters. Typically 576 dots at 203 dpi,
  giving 48 characters per line in Font A; some models print 512 dots, giving 42.
- **58 mm** — handhelds and mobile printers. Typically 384 dots, 32 characters
  in Font A.

Vietnamese item names are long. Diacritics do not add width in a monospaced font,
but Vietnamese words are short and numerous, so a product description wraps across
more lines than its English equivalent. Budget for two-line item names at 58 mm
and do not truncate mid-word.

## Languages used in retail

Vietnamese is the working language of retail. English appears in tourist-facing
and international-brand contexts, but a till operated by locally hired staff needs
a Vietnamese interface, and the printed slip is expected in Vietnamese.

**Back office in one language, till in another.** Chinese-owned wholesalers and
shops in Vietnam commonly run purchasing, stock and reporting in Chinese while the
cashier interface and the printed receipt stay in Vietnamese. The requirement is
one data set with the interface language resolved per user, plus a print template
language set independently of both — the owner may read reports in Chinese and
still need every customer-facing document to print in Vietnamese.

Product names are the place this gets subtle. A single product often needs two
names: an internal name the owner recognises and a Vietnamese customer-facing name
that prints on the receipt and the shelf label. One name field forces the owner to
choose between a back office they can read and a receipt the customer can read.

## Payment methods

| Method | Notes |
| --- | --- |
| Bank transfer by QR | Very widely used at the counter, including for small amounts, generally through the interbank QR standard (VietQR, over the NAPAS 247 rails). The customer scans, transfers, and shows the confirmation. Settlement is not instant to the POS, so the sale is closed on visual confirmation — build for that reality rather than assuming a callback. |
| E-wallets | Several established wallet apps — MoMo, ZaloPay and Viettel Money among them — each with its own merchant integration and its own reconciliation report. Treat each as a distinct tender type rather than merging them into "wallet". |
| Cash | Still substantial, particularly outside major cities and in wholesale. |
| Cards | Domestic debit switch plus international schemes, generally through a bank terminal. POS-to-terminal integration is not universal. |

Reconciliation is the hard part. Transfers arrive in a bank account with a memo
field the customer may or may not have filled in correctly. The POS should record
a reference for every non-cash tender and make it editable after the fact, because
the person matching the bank statement at end of day is frequently not the person
who took the payment.

## Notes for POS implementers

**The counter slip and the e-invoice are different documents.** The customer
usually wants a slip immediately; the e-invoice is registered separately and may
be requested only by customers who need it for deduction. Model them as two
artefacts linked by the sale, with independent numbering, independent print
templates, and independent lifecycles. Systems that try to make one printed
document serve both roles tend to fail at the first request for a tax invoice
after the fact.

**Character encoding is the first thing to test, not the last.** See the encoding
section below — a POS that prints `Cà phê sữa đá` as `C? ph? s?a ?á` is not
deployable, and this is discovered on the printer, never in the emulator.

**Digit grouping is a correctness feature.** With no decimals and seven to nine
digits, an ungrouped amount is genuinely misread. Verify grouping renders on the
receipt, on the customer display, in reports and in the amount-tendered field —
these are frequently four different formatters.

**Time zone.** Indochina Time, UTC+7, no daylight saving. Store timestamps with
offset. Make the business-day boundary configurable for shops trading past
midnight.

**Tax code capture.** A customer asking for a VAT invoice will produce a company
tax code, often after the sale has been rung up. Decide whether that is a
mid-transaction edit or a follow-up issuance before designing the flow. `TODO:
verify` the MST format before adding client-side validation.

### Vietnamese text on thermal printers

Vietnamese is Latin script, but it stacks a vowel-quality diacritic and a tone
mark on the same letter — `ế`, `ộ`, `ữ` — producing a repertoire far larger than
any single-byte Western code page covers.

- **Most ESC/POS printers do not accept UTF-8.** Text is sent as bytes and
  interpreted through a selected code page.
- **Windows-1258 does not cover the full precomposed repertoire.** It encodes
  some Vietnamese characters as base letter plus a combining tone mark, so a naive
  transcode drops or mangles tone marks even when the code page is nominally
  correct.
- **Legacy encodings still appear in supplier data** — TCVN3 and VNI-style
  encodings turn up in spreadsheets of product names. Normalise on import; do not
  pass them through to the printer.
- **Code page selection is vendor-specific.** The command that selects a code page
  is standard, but the numeric value identifying a Vietnamese page is not
  consistent across firmware. `TODO: verify` against the specific printer's command
  reference rather than trusting a generic table.
- **Raster fallback is the reliable answer.** Rendering the receipt to a bitmap
  and sending it as a graphic bypasses code pages and printer fonts entirely.
  It is slower and sends more data, but it prints exactly what was rendered.
  For a mixed-language deployment — Vietnamese receipts, occasional Chinese in the
  back office — this is usually the correct default rather than the fallback.

**Test string.** Print this before writing any layout code:

```
Cà phê sữa đá — Nguyễn Huệ — 150.000 ₫
Tổng cộng: 1.234.567 ₫
```

Check the tone marks specifically, check that `₫` renders rather than printing as
a box, and check that the periods survive as grouping separators. If `₫` is not in
the printer's repertoire, print `VND` instead — an unreadable currency symbol is
worse than a three-letter code.

---

_Last updated: 2026-08_
