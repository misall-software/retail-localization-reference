# Kenya — Retail & POS Localization

**Kenya runs a mandatory electronic tax invoice regime.** A retail POS in Kenya is
not a standalone device: the legal invoice number and the QR code on the receipt
originate from a control unit registered with the tax authority, not from the POS
software's own sequence. Currency is the Kenyan shilling (KES), printed receipts
are predominantly English, and mobile money is the dominant non-cash tender.

> ### Verification status — unverified draft
>
> Confirm every item below against a primary source before relying on this file.
>
> **Open items — `TODO: verify`**
>
> 1. Current standard VAT rate, and whether any reduced rate applies to retail goods.
> 2. Whether displayed consumer prices are legally required to be VAT-inclusive.
> 3. The full mandatory field list for an electronic tax invoice, against the
>    current text of the electronic tax invoice regulations.
> 4. What the receipt QR code must encode, and whether a verification URL is prescribed.
> 5. Whether the QR requirement applies to all sales or only to VAT-registered sellers.
> 6. The current name and status of the electronic invoicing system, and whether the
>    older register-based regime is still accepted anywhere.
> 7. The integration modes available for transmitting invoices to the authority.
> 8. The behaviour required when the connection to the tax authority is unavailable
>    at the moment of sale, and the permitted catch-up window.
> 9. Taxpayer PIN format and validation rules.
> 10. Whether small-denomination rounding at the till has any legal basis or is
>     purely a trade practice.
> 11. The operational differences between till-style and bill-style mobile money
>     merchant collection, including settlement timing and transaction costs.
> 12. The authority's current portal URL for each of the above.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `KES` | official-authority |
| Symbol | `KSh` | official-authority |
| Symbol position | Prefix — `KSh 1,250.00`. A trailing `/=` form (`1,250/=`) is also seen in informal and handwritten contexts. | unverified |
| Decimal places | 2 | official-authority |
| Thousands separator | `,` — decimal separator `.` | unverified |
| Typical price magnitude | Roughly 10 to 10,000 KES for everyday retail lines; supermarket baskets commonly in the low thousands. Order of magnitude only, given here to size fields and decide digit grouping. | unverified |

Confirm the code, symbol and subdivision against the Central Bank of Kenya.

**Formatting consequences.** Four to five integer digits plus grouping plus a
three-character prefix is the normal case, so an amount column needs room for
about `KSh 12,345.00` without wrapping. Cent values exist but small coins
circulate thinly, and rounding to the nearest shilling at the till is common
practice — see open item 10 before implementing any automatic rounding.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | Standard rate 16%. Zero-rated and exempt categories exist and are defined by schedule, not by product name. `TODO: verify` current standard rate and whether any reduced rate currently applies. | public-regulation |
| Tax-inclusive or exclusive display | Consumer-facing prices are quoted VAT-inclusive in ordinary retail practice. `TODO: verify` whether this is a legal display requirement or convention. | unverified |
| Fiscal system name | eTIMS — the electronic Tax Invoice Management System, administered by the Kenya Revenue Authority (KRA). It succeeded an earlier register-based regime built on ETR devices and control units. `TODO: verify` current system name, scope, and whether the predecessor remains valid anywhere. | official-authority |

**What this means for the POS.** VAT is calculated per line against a tax
category, not applied as a single rate to the basket total. A product record
therefore needs a tax-category field that maps to the statutory schedule, and the
schedule — not the software's default — decides whether an item is standard-rated,
zero-rated or exempt. Zero-rated and exempt are different states and must remain
distinguishable on the receipt and in reporting; collapsing them into "no tax"
loses information the return needs.

## Receipt requirements

### Mandatory fields

Fields commonly required on an electronic tax invoice. The list is a starting
point for verification, **not a confirmed specification** — `TODO: verify` the
complete list, the exact labelling, and which fields are conditional.

- Seller name and taxpayer PIN — `public-regulation`
- Invoice serial number — `public-regulation`
- Date and time of the transaction — `public-regulation`
- Buyer PIN, where the buyer intends to claim input tax — `public-regulation`
- Item description, quantity, unit price — `public-regulation`
- Taxable value, broken out per tax rate — `public-regulation`
- Tax rate and tax amount — `public-regulation`
- Gross total — `public-regulation`
- Control unit serial number — `public-regulation`
- Control unit invoice number — `public-regulation`

The control unit invoice number is the point implementers most often get wrong.
It is issued by the control unit, not by the POS. The POS may keep its own
internal receipt sequence, but the number that makes the document a tax invoice
comes back from the control unit and must be printed as returned.

### QR code

Required on the electronic tax invoice — `public-regulation`.
`TODO: verify` what the code must encode, whether the authority prescribes a
verification URL format, and whether the requirement extends to non-VAT-registered
sellers. Size the print area from the encoded payload, not from a fixed pixel
count; a URL carrying an invoice signature needs meaningfully more modules than a
short reference string, and an over-compressed QR on 58 mm paper fails to scan.

### Common paper widths

- **80 mm** — the default for fixed counters. Print area is typically 72 mm
  (576 dots at 203 dpi), giving 48 characters per line in Font A; some models
  print 512 dots, giving 42. Check the model before fixing a template width.
- **58 mm** — handhelds and mobile printers. Typically 384 dots, 32 characters
  in Font A.

An 80 mm template does not degrade gracefully to 58 mm. A Kenyan tax invoice
carries a control unit number, an invoice number, a QR code and a per-rate tax
breakdown, and at 32 characters per line those elements have to be stacked rather
than columned. Design the 58 mm layout separately.

## Languages used in retail

English and Kiswahili are both in everyday use. Printed commercial documents —
invoices, receipts, shelf labels, price lists — are predominantly in English.
Spoken interaction at the counter is commonly Kiswahili or a mix, and colloquial
Nairobi speech (Sheng) appears in informal signage but not on printed receipts.

For a POS this means the printed artefact and the interface do not have to share
a language. English is the safe default for receipt templates.

**Back office in one language, till in another.** Chinese-owned shops in Kenya
commonly run the administrative side — purchasing, stock, reports, margins — in
Chinese, while the till interface stays in English so that local cashiers can be
hired and trained without a language barrier. The pattern is one account set with
two interface languages resolved per user, not two systems. Anything a cashier
must read at speed (button labels, error text, prompts, the receipt) follows the
till language; anything the owner reads follows the back-office language.

The practical requirement is that language is a property of the logged-in user
and the print template, not a global installation setting.

## Payment methods

| Method | Notes |
| --- | --- |
| Mobile money — M-Pesa | The dominant non-cash tender. Merchant collection runs through till-style and bill-style shortcodes (commonly referred to as Buy Goods and Paybill), and the two settle and reconcile differently — `TODO: verify` the operational differences before choosing one. Capture the transaction reference the customer receives; it is the reconciliation key, and if the cashier does not enter it, that sale cannot be matched later. Other mobile money services also operate. |
| Cash | Still substantial. Small-coin scarcity makes till rounding a live question — see open item 10. |
| Cards | Visa and Mastercard, generally through a bank-supplied terminal. Terminal-to-POS integration is not universal; many sites key the amount into the terminal by hand, so the POS must accept a card tender without an authorisation code. |
| Bank transfer | Used for wholesale and account customers rather than counter retail. |

Split tender is normal — part mobile money, part cash — so the payment model must
allow multiple tenders against one sale, each with its own reference field.

## Notes for POS implementers

**Treat the tax authority link as an unreliable dependency.** Retail sites lose
connectivity, and a till that cannot sell while the link is down is not
deployable. The design question is what the customer is handed at that moment and
how the document is regularised afterwards — see open item 8, which must be
resolved from the regulation rather than by engineering preference.

**Do not let the POS mint the legal invoice number.** Keep the internal sequence
if it is useful operationally, but the number printed as the tax invoice number
must be the one returned by the control unit. Storing both, clearly separated, is
what makes later reconciliation with the authority's records possible at all.

**Store the control unit response, not just the printed output.** Whatever the
control unit returns — invoice number, unit serial, signature, QR payload —
belongs in the sale record. Reprints must reproduce the original values, not
regenerate them.

**Reprints are not reissues.** A reprint of an existing tax invoice and the
issuance of a new one are different acts with different consequences. Mark
reprints on the printed copy and log them.

**Credit notes are documents, not negative sales.** A refund that reverses a tax
invoice has to be issued as its own document referencing the original. Modelling
refunds as a sale with negative quantities will produce a VAT return that does
not reconcile.

**PIN capture at the till.** A business customer will ask for their PIN on the
invoice, sometimes after the sale has started. Decide up front whether that is a
mid-transaction edit or a reissue — retrofitting it is expensive. `TODO: verify`
the PIN format before adding client-side validation; rejecting a valid PIN at the
counter is worse than accepting an invalid one.

**Time zone.** East Africa Time, UTC+3, no daylight saving. Store timestamps with
offset and print local time. Z-report and business-day boundaries should be
configurable per site — shops that close after midnight will otherwise split one
trading day across two.

**Character set.** English and Kiswahili are both plain Latin script with no
diacritics in normal commercial use, so the default printer code page is
sufficient. Kenya has no analogue to the encoding problems documented in the
Vietnam and Arabic files.

---

_Last updated: 2026-08_
