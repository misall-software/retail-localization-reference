# Peru — Retail & POS Localization

**Peru's electronic receipt regime distinguishes the document type by who the
customer is.** A sale to a consumer and a sale to a business are different legal
documents with different required data, and the cashier has to know which one to
issue at the moment of sale. Currency is the sol (PEN), the consumption tax is
IGV, and the tax authority is SUNAT.

> ### Verification status — partially verified, 2026-08
>
> Several items have been checked against secondary sources and are recorded in
> the body. **Secondary sources are not primary sources**: confirm against SUNAT
> or the governing resolution before relying on any of it.
>
> **Resolved this pass — reconfirm before publishing**
>
> - IGV **18%** (16% IGV + 2% IPM), unchanged for 2026.
> - A temporary **10%** rate for micro and small restaurants, hotels and tourist
>   lodging, through 31 December 2026.
> - Boleta requires customer identity document above **S/ 700**.
> - Plastic bag tax (ICBPER) at **S/ 0.50** per bag, the rate since 2023.
> - QR payload, field order, separator and print size constraints — see below.
>
> **Still open — `TODO: verify`**
>
> 1. The exact qualifying conditions for the reduced restaurant/hotel rate, and
>    whether it applies to the intended business.
> 2. Whether displayed consumer prices are legally required to be tax-inclusive.
> 3. The full mandatory field list for each electronic document type.
> 4. The current scope of the QR obligation across emission routes, and the print
>    constraints, against the governing resolution.
> 5. Which transmission routes are currently available for registering documents,
>    and any obligation to use an authorised intermediary.
> 6. The deadline for transmitting a document after the sale, and what is permitted
>    when the connection is unavailable.
> 7. Whether selective consumption tax applies to any goods in the intended
>    catalogue, and at what rates.
> 8. Taxpayer identifier (RUC) and consumer identity document formats and
>    validation rules.
> 9. Whether cash rounding to the nearest ten céntimos has a legal basis.
> 10. The current scope of interoperability between the major mobile wallet
>     services, and what each requires of a merchant.
> 11. The authority's current portal URL for each of the above.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `PEN` | official-authority |
| Symbol | `S/` — the older `S/.` form persists in printed material. | official-authority |
| Symbol position | Prefix — `S/ 125.00`. | unverified |
| Decimal places | 2 | official-authority |
| Thousands separator | `,` — decimal separator `.` | unverified |
| Typical price magnitude | Roughly 1 to 500 PEN for everyday retail lines. Order of magnitude only, given here to size fields. | unverified |

Confirm the code, symbol and subdivision against the Banco Central de Reserva del
Perú.

**Formatting consequences.** Amounts are short and unremarkable — two or three
integer digits and two decimals — so field width is not the concern it is in
Vietnam. The concern is the coin situation: the smallest denominations have been
withdrawn from circulation over time, and cash totals are commonly settled to the
nearest ten céntimos while card and wallet payments settle to the exact centavo.
That produces a systematic cash-versus-recorded discrepancy unless rounding is
modelled explicitly as its own amount on the sale. See open item 11 before
implementing it.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | IGV at **18%** — a 16% IGV component plus a 2% municipal promotion component (IPM), quoted and printed as a single 18% figure. | public-regulation |
| Reduced rate | A temporary **10%** rate (8% IGV + 2% IPM) applies to micro and small enterprises in restaurants, hotels and tourist lodging, subject to income and activity-mix conditions, **through 31 December 2026**. `TODO: verify` the exact qualifying conditions and current status. Directly relevant to food-service operators — do not assume a single 18% rate covers the catalogue. | public-regulation |
| Tax-inclusive or exclusive display | Consumer-facing retail prices are quoted tax-inclusive in ordinary practice; business-to-business documents commonly show the net amount and IGV separately. `TODO: verify` whether inclusive display is a legal requirement. | unverified |
| Fiscal system name | Electronic payment vouchers — Comprobantes de Pago Electrónicos (CPE) — administered by SUNAT (Superintendencia Nacional de Aduanas y de Administración Tributaria). Documents are generated as structured XML and registered with SUNAT, which returns an acceptance response. `TODO: verify` current system naming, document catalogue, and transmission routes. | official-authority |

**Additional levies that reach the receipt.** Two are worth checking against the
intended product catalogue before assuming a single tax rate is enough:

- A per-unit tax on plastic bags (ICBPER) at **S/ 0.50 per bag**, the rate in
  force since 2023 after a scheduled ramp from 2019 — `public-regulation`. It
  appears as its own line rather than being folded into the item price, so the
  till needs a bag as a sellable line item with its own tax treatment. Declared
  and paid monthly by the establishment.
- Selective consumption tax on specific categories such as alcohol, tobacco,
  fuel and sugary drinks — `public-regulation` `TODO: verify` applicability and
  rates. Where it applies it is computed before IGV, so the tax engine must
  support a levy that forms part of the base for another tax. A flat
  percentage-per-line model cannot express this.

## Receipt requirements

### Document types

The distinction drives the whole flow and has no equivalent in many markets:

| Document | Issued to | Key consequence |
| --- | --- | --- |
| Boleta de venta electrónica | Consumers | Customer identity document (DNI, foreigner's card, or passport) and full name required when the total exceeds **S/ 700**. Below that, customer fields are optional. |
| Factura electrónica | Businesses | Requires the buyer's taxpayer identifier (RUC). Enables the buyer's tax credit. |
| Nota de crédito / Nota de débito | Either | Adjustments and reversals. Must reference the original document. |

The cashier chooses at the point of sale, and the choice changes what data must
be captured. A till interface that buries this in a settings menu will produce a
queue of customers asking for a factura after the boleta has been issued — which
is a credit note plus a reissue, not an edit.

### Mandatory fields

Fields commonly required on an electronic voucher. This is a starting point for
verification, **not a confirmed specification** — `TODO: verify` the complete list
per document type.

- Issuer name, RUC, and address — `public-regulation`
- Document type and serial/correlative number — `public-regulation`
- Date of issue — `public-regulation`
- Customer identifier — RUC for a factura; identity document number for a boleta
  above the threshold — `public-regulation`
- Item description, quantity, unit price, line total — `public-regulation`
- Taxable base and IGV amount — `public-regulation`
- Any separately levied tax, shown as its own line — `public-regulation`
- Total payable, and the amount in words where required — `public-regulation` `TODO: verify`
- Document reference for credit and debit notes — `public-regulation`
- QR code — `public-regulation`

### QR code

Required on the printed representation since 1 January 2019 —
`public-regulation`. Note the scope: the obligation attaches to vouchers issued
through the taxpayer's own emission system (SEE-Del contribuyente); it has been
described as not applying to SUNAT's own web-based and free-facturador routes —
`TODO: verify` the current scope against the governing resolution.

**Encoded payload.** Fields in fixed order, separated by the pipe character `|`:

```
RUC | document type | series | number | total IGV | total amount |
issue date | acquirer document type | acquirer document number | hash value
```

**Print constraints** — `public-regulation`, `TODO: verify` against the current
resolution before building the template:

- Position: lower part of the printed representation
- Maximum size: 2 cm high by 6 cm wide
- Quiet zone: at least 1 mm
- Printed in black
- Symbology: QR Code 2005, per ISO/IEC 18004:2006

The size ceiling is the constraint that bites. A payload carrying a hash plus ten
pipe-separated fields inside 2 cm at 203 dpi is roughly 160 dots — verify the
module size scans reliably on your printer before committing the layout, and
reserve the area from the start rather than fitting it in at the end.

### Common paper widths

- **80 mm** — the default for fixed counters. Typically 576 dots at 203 dpi,
  giving 48 characters per line in Font A; some models print 512 dots, giving 42.
- **58 mm** — handhelds and mobile printers. Typically 384 dots, 32 characters
  in Font A.

Spanish item descriptions run longer than their English equivalents, commonly by
a fifth or more. A description column sized from English test data will truncate
in production. Spanish also needs `ñ`, accented vowels and `¿ ¡`, all of which
require a code page beyond the US default — see the implementer notes.

## Languages used in retail

Spanish is the language of retail. Quechua and Aymara hold official status in
areas where they predominate, and are relevant to spoken interaction in parts of
the highlands, but commercial documents and POS interfaces are in Spanish.

**Back office in one language, till in another.** Peru has a long-established
Chinese commercial community, and Chinese-owned shops and wholesalers commonly run
the back office in Chinese while the till interface and every printed document
stay in Spanish. As elsewhere, the requirement is per-user interface language over
a single data set, with the print template language pinned to Spanish
independently of whatever the owner is reading.

Note the interaction with the document-type problem above: the cashier deciding
between a boleta and a factura is reading Spanish prompts, while the owner
reviewing the day's documents is reading Chinese. Both views describe the same
document set and must use consistent terminology — translating the document type
names loosely in the back office makes the two views impossible to reconcile in
conversation.

## Payment methods

| Method | Notes |
| --- | --- |
| Mobile wallets by QR | Widely used, including for small amounts. Yape and Plin are the services most often encountered, with interoperability between them — `TODO: verify` the current scope of that interoperability. The customer scans and pays; confirmation is visual at the counter. |
| Cash | Substantial. Small-coin rounding applies — see the currency section. |
| Cards | Visa and Mastercard through bank-supplied terminals, with more than one acquirer in common use. Terminal-to-POS integration varies by acquirer. |
| Bank transfer | Used for wholesale and account customers; the interbank account code is the reference customers supply. |

Record a reference for every non-cash tender and allow split tender across
methods. Wallet payments confirmed visually need the reference captured at the
till or the day's takings cannot be matched to the settlement report.

## Notes for POS implementers

**Design for the acceptance response, not just the print.** The document becomes
valid through registration with SUNAT, not through printing. The POS must store
what came back, keep documents that have not yet been accepted in a visible queue,
and surface rejections to someone who can act on them — a rejected document that
silently stays rejected is an unbilled sale.

**Sequential numbering is per series and cannot have gaps.** Series and
correlative numbering must be allocated so that a crashed transaction does not
consume a number invisibly. Decide whether a number is allocated at sale start or
at document generation, and make voided documents explicit rather than skipping
the number.

**Credit notes reference the original.** Refunds and corrections are issued as
their own documents pointing at the document they adjust. Negative-quantity sales
will not reconcile.

**The plastic bag line item.** Where the bag tax applies, a bag is a product with
a price and a distinct tax treatment, and the cashier has to ring it up. Build it
as catalogue data rather than as special-cased logic, so it can be switched off
when the levy changes.

**Time zone.** Peru Time, UTC−5, no daylight saving. Store timestamps with offset.
Make the business-day boundary configurable.

**Character encoding.** Spanish needs `ñ`, `á é í ó ú`, `ü`, and the inverted
punctuation `¿ ¡`. On a thermal printer these live outside the default code page,
so a code page covering Western European characters must be selected explicitly.
Symptoms of getting it wrong are mild enough to reach production unnoticed —
`ñ` printing as `n` or as a box — so test with a deliberately accented product
name rather than with clean ASCII test data. As with Vietnamese, raster rendering
avoids the problem entirely and is worth defaulting to where a Chinese-language
back office is also in play.


## Food service

Restaurants diverge from retail at the till, not just in the menu. Three things
change: the tax treatment can depend on where the food is eaten, service charge
and tips carry their own rules and their own tax questions, and the trading day
routinely runs past midnight. Peru is also the one country in this repository with a confirmed food-service tax rate of its own, which makes getting the segment right worth real money.

### Tax treatment

| Question | Answer | Source type |
| --- | --- | --- |
| Dine-in, takeaway and delivery taxed differently? | `TODO: verify` | unverified |
| Reduced rate or registration threshold for small food businesses? | **Yes — a reduced rate applies.** A temporary 10% rate (8% IGV + 2% IPM) applies to micro and small enterprises in restaurants, hotels and tourist lodging, subject to income and activity-mix conditions, **through 31 December 2026**, after which it reverts to 18%. | public-regulation |
| Alcoholic drinks taxed separately? | `TODO: verify` | unverified |

### Service charge and tips

| Question | Answer | Source type |
| --- | --- | --- |
| Service charge customary? At what rate? Mandatory? | `TODO: verify` | unverified |
| Is the service charge itself taxable? | `TODO: verify` | unverified |
| Do tips go through the POS, and are they recorded? | `TODO: verify` | unverified |
| Must the service charge be shown as its own receipt line? | `TODO: verify` | unverified |

### Receipt requirements specific to food service

| Question | Answer | Source type |
| --- | --- | --- |
| Must dine-in and takeaway be distinguished on the document? | `TODO: verify` | unverified |
| Must individual menu items be itemised? | `TODO: verify` | unverified |
| Are table number and guest count mandatory fields? | `TODO: verify` | unverified |

### Operating conventions

**Trading day and the midnight boundary.** `TODO: verify` whether any rule governs the accounting date of a sale rung up after midnight. Regardless of the answer, make the business-day boundary configurable per site — see the retail sections above.

**Trading hours.** `TODO: verify` typical local hours for the intended segment;
they drive shift handover, Z-report timing and staffing, and they differ sharply
between a bakery and a bar.

**Kitchen ticket language.** Chinese-owned restaurants are long established in Peru, and the chifa segment is the clearest case in this repository of a kitchen that reads one language while the dining room reads another. The kitchen ticket language must be settable independently of both the till language and the customer-facing document language.

### Notes for POS implementers

Four capabilities separate a food-service till from a retail one. They are worth
naming because a retail POS typically has none of them, and retrofitting them is
expensive:

- **Floor plan and table state** — a sale is attached to a table, not opened and
  closed in one pass.
- **Tab allocation** — one table's bill split across several payers, or one payer
  covering several tables. Splitting by item and splitting evenly are different
  operations and both get asked for.
- **Guest count** — needed for per-head reporting, and in some markets it appears
  on the document. See the receipt table above.
- **Tip adjustment** — the tip is frequently added *after* the card is
  authorised, so the recorded amount must be adjustable post-authorisation
  without reopening the sale.

**The reduced rate is a segment boundary, not a product boundary.** Qualification depends on the business and its income mix, not on what is being sold, so the rate cannot be attached to menu items alone. It also expires — a system carrying 10% into 2027 will be wrong on every line. Confirm eligibility with an accountant before configuring it.

**Order modifiers are not discounts.** "No coriander", "extra spicy", "sauce on
the side" attach to a line and must reach the kitchen ticket, sometimes with a
price delta and sometimes without. Modelling them as discounts or as separate
products both fail — the first corrupts the tax base, the second corrupts stock.

**Void before and after firing are different events.** Cancelling an item that
has not reached the kitchen is an edit; cancelling one already cooked is a loss
that has to be recorded as such, or waste and theft become indistinguishable.

_Last updated: 2026-08_

---

_Maintained by the MISAll team. Last updated: 2026-08_
