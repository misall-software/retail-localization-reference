# Peru — Retail & POS Localization

**Peru's electronic receipt regime distinguishes the document type by who the
customer is.** A sale to a consumer and a sale to a business are different legal
documents with different required data, and the cashier has to know which one to
issue at the moment of sale. Currency is the sol (PEN), the consumption tax is
IGV, and the tax authority is SUNAT.

> ### Verification status — unverified draft
>
> Confirm every item below against a primary source before relying on this file.
>
> **Open items — `TODO: verify`**
>
> 1. Current IGV rate and its composition.
> 2. Whether displayed consumer prices are legally required to be tax-inclusive.
> 3. The amount threshold above which a consumer receipt must carry the customer's
>    identity document number, and the exact rule for which document types are
>    accepted.
> 4. The full mandatory field list for each electronic document type.
> 5. What the QR code on the printed representation must encode.
> 6. Which transmission routes are currently available for registering documents,
>    and any obligation to use an authorised intermediary.
> 7. The deadline for transmitting a document after the sale, and what is permitted
>    when the connection is unavailable.
> 8. Whether the plastic bag tax is currently levied, its per-unit amount for the
>    current year, and how it must appear on the receipt.
> 9. Whether selective consumption tax applies to any goods in the intended
>    catalogue, and at what rates.
> 10. Taxpayer identifier (RUC) and consumer identity document formats and
>     validation rules.
> 11. Whether cash rounding to the nearest ten céntimos has a legal basis.
> 12. The current scope of interoperability between the major mobile wallet
>     services, and what each requires of a merchant.
> 13. The authority's current portal URL for each of the above.

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
| VAT rate | IGV at 18%, conventionally understood as a 16% IGV component plus a 2% municipal promotion component, quoted and printed as a single 18% figure. `TODO: verify` the current rate and composition. | public-regulation |
| Tax-inclusive or exclusive display | Consumer-facing retail prices are quoted tax-inclusive in ordinary practice; business-to-business documents commonly show the net amount and IGV separately. `TODO: verify` whether inclusive display is a legal requirement. | unverified |
| Fiscal system name | Electronic payment vouchers — Comprobantes de Pago Electrónicos (CPE) — administered by SUNAT (Superintendencia Nacional de Aduanas y de Administración Tributaria). Documents are generated as structured XML and registered with SUNAT, which returns an acceptance response. `TODO: verify` current system naming, document catalogue, and transmission routes. | official-authority |

**Additional levies that reach the receipt.** Two are worth checking against the
intended product catalogue before assuming a single tax rate is enough:

- A per-unit tax on plastic bags, which appears as its own line rather than being
  folded into the item price — `public-regulation` `TODO: verify` current status
  and amount. Where levied it is charged per bag, so the till needs a bag as a
  sellable line item with its own tax treatment.
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
| Boleta de venta electrónica | Consumers | Customer identity document required above an amount threshold — `TODO: verify` the threshold. |
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

Required on the printed representation of an electronic voucher —
`public-regulation`. `TODO: verify` the exact encoded content and field
separator format. Reserve the print area on the template from the start; a QR
added late to a finished 80 mm layout tends to push the total off the visible
area or shrink below reliable scanning size.

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

---

_Last updated: 2026-08_
