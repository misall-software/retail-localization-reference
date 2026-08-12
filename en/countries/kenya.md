# Kenya — Retail & POS Localization

**Kenya runs a mandatory electronic tax invoice regime.** A retail POS in Kenya is
not a standalone device: the legal invoice number and the QR code on the receipt
originate from a control unit registered with the tax authority, not from the POS
software's own sequence. Currency is the Kenyan shilling (KES), printed receipts
are predominantly English, and mobile money is the dominant non-cash tender.

> ### Verification status — partially verified, 2026-08
>
> Several items have been checked against secondary sources and are recorded in
> the body. **Secondary sources are not primary sources**: confirm against the
> regulation text or KRA before relying on any of it.
>
> **Resolved this pass — reconfirm before publishing**
>
> - Standard VAT rate **16%**; active rates are 16% and 0%.
> - eTIMS is the current system; e-invoicing mandatory since 30 November 2022,
>   extended in **January 2024** beyond VAT-registered businesses to taxpayers
>   generally.
> - Mandatory field list expanded below, including the KRA **item classification
>   code** and the **Control Unit Invoice Number**.
> - QR code is system-generated and verifiable on KRA's portal.
>
> **Still open — `TODO: verify`**
>
> 1. Whether displayed consumer prices are legally required to be VAT-inclusive.
> 2. The mandatory field list against the current regulation text — the list below
>    is assembled from secondary sources and the labelling may differ.
> 3. The exact QR payload and whether a verification URL format is prescribed.
> 4. Electronic signature and five-year retention requirements, against the text.
> 5. Current penalty amounts for non-compliance.
> 6. The integration modes available for transmitting invoices to the authority.
> 7. The behaviour required when the connection to the tax authority is unavailable
>    at the moment of sale, and the permitted catch-up window.
> 8. Taxpayer PIN format and validation rules.
> 9. Whether small-denomination rounding at the till has any legal basis or is
>    purely a trade practice.
> 10. The operational differences between till-style and bill-style mobile money
>     merchant collection, including settlement timing and transaction costs.
> 11. The authority's current portal URL for each of the above.

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
| VAT rate | Standard rate **16%**. The two active rates are 16% and 0% for zero-rated supplies; exempt categories are separate again. Zero-rated and exempt are defined by schedule, not by product name. | public-regulation |
| Tax-inclusive or exclusive display | Consumer-facing prices are quoted VAT-inclusive in ordinary retail practice. `TODO: verify` whether this is a legal display requirement or convention. | unverified |
| Fiscal system name | **eTIMS** — the electronic Tax Invoice Management System, administered by the Kenya Revenue Authority (KRA), succeeding a register-based regime built on ETR control units. Electronic invoicing has been mandatory since 30 November 2022, and **since January 2024 the obligation extends beyond VAT-registered businesses to taxpayers generally**, including small traders and professionals. | official-authority |
| Consequence of non-compliance | An invoice issued without an eTIMS reference is not valid for tax purposes: the buyer cannot claim the expense and KRA can disallow the transaction on audit. `TODO: verify` current penalty amounts. | public-regulation |

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
- Invoice serial or reference number — `public-regulation`
- Date and time of issue — `public-regulation`
- Buyer PIN, where the buyer intends to claim the expense or input VAT — `public-regulation`
- **Item code per KRA's classification** — `public-regulation`. This one is easy to
  miss: it is a mandated classification code, not your own SKU, so the product
  record needs a field for it and someone has to populate it for every line.
- Description of goods or services, quantity and unit of measure, unit price — `public-regulation`
- Taxable amount, broken out per tax rate — `public-regulation`
- Tax rate and tax amount — `public-regulation`
- Total amount — `public-regulation`
- Control unit serial number — `public-regulation`
- Control Unit Invoice Number (CUIN), returned by KRA — `public-regulation`
- QR code — `public-regulation`

Two further obligations attach to the document rather than the print: invoices
must be **electronically signed**, and retained in digital form for **at least
five years** — `public-regulation`, `TODO: verify` both against the regulation
text. Retention is an archive requirement, not a print requirement, but it
constrains how the POS stores and exports transaction history.

The control unit invoice number is the point implementers most often get wrong.
It is issued by the control unit, not by the POS. The POS may keep its own
internal receipt sequence, but the number that makes the document a tax invoice
comes back from the control unit and must be printed as returned.

### QR code

Required on the electronic tax invoice — `public-regulation`. It is generated by
the system and encodes the invoice details; customers scan it to verify
authenticity against KRA's portal. Since the eTIMS obligation now reaches
taxpayers generally rather than only VAT-registered sellers, assume the QR
applies to your sales unless a specific exclusion is confirmed.

`TODO: verify` the exact encoded payload and whether a verification URL format is
prescribed. Size the print area from the payload, not from a fixed pixel count; a
URL carrying an invoice signature needs meaningfully more modules than a short
reference string, and an over-compressed QR on 58 mm paper fails to scan.

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


## Food service

Restaurants diverge from retail at the till, not just in the menu. Three things
change: the tax treatment can depend on where the food is eaten, service charge
and tips carry their own rules and their own tax questions, and the trading day
routinely runs past midnight. Kenya's eTIMS obligation applies to food service as it does to retail, so the questions here are mostly about what a restaurant document must additionally carry.

### Tax treatment

| Question | Answer | Source type |
| --- | --- | --- |
| Dine-in, takeaway and delivery taxed differently? | `TODO: verify` | unverified |
| Reduced rate or registration threshold for small food businesses? | `TODO: verify` | unverified |
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

**Trading day and the midnight boundary.** `TODO: verify` whether any rule governs the accounting date of a sale rung up after midnight. Regardless, make the business-day boundary configurable per site — a restaurant closing at 02:00 will otherwise split one night's trade across two reporting days.

**Trading hours.** `TODO: verify` typical local hours for the intended segment;
they drive shift handover, Z-report timing and staffing, and they differ sharply
between a bakery and a bar.

**Kitchen ticket language.** Chinese-owned restaurants commonly run a Chinese-reading kitchen, a local-language dining room and a Chinese back office. The kitchen ticket language must be settable independently of the till language and of the customer-facing document language — three settings, not one. `TODO: verify` nothing here; this is a deployment pattern, not a legal requirement.

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

**eTIMS still applies.** Everything in the retail sections about the control unit invoice number, the QR code and offline behaviour holds for a restaurant. `TODO: verify` whether a food-service document has any additional mandatory field, and how a table left open across a connectivity outage should be handled.

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
