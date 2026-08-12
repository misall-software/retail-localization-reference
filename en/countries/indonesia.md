# Indonesia — Retail & POS Localization

**Indonesia's VAT looks like 11% and is legislated as 12%.** Since January 2025
the statutory PPN rate is 12%, but non-luxury goods and services are taxed on an
adjusted base of 11/12 of the selling price, producing an effective 11%. A POS
that simply applies 11% will usually agree to the cent and occasionally will not —
the calculation has to follow the prescribed form, not the shortcut. Currency is
the rupiah, whose amounts run to six and seven figures on ordinary retail lines.

> ### Verification status — partially verified, 2026-08
>
> Rates checked against secondary sources. Confirm against the Directorate General
> of Taxes before relying on any of it.
>
> **Resolved this pass**
>
> - Statutory PPN 12%; effective 11% on non-luxury via an 11/12 base adjustment
>   under PMK No. 131 of 2024. Luxury goods taxed at a full 12%.
>
> **Still open — `TODO: verify`**
>
> 1. The exact rounding and presentation rule for the adjusted base — whether the
>    receipt must show the adjusted base, the 12% rate, or the effective 11%.
> 2. Which goods fall under luxury treatment for an ordinary retail catalogue.
> 3. Whether e-Faktur obligations reach retail B2C sales or only B2B.
> 4. The current status of the tax administration's system modernisation and what
>    it requires of a POS.
> 5. Whether displayed consumer prices are legally required to be tax-inclusive.
> 6. Mandatory receipt fields for a B2C retail sale.
> 7. Taxpayer identifier (NPWP) format and validation rules.
> 8. Local network stability and outage frequency at the intended location.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `IDR` | official-authority |
| Symbol | `Rp` | official-authority |
| Symbol position | Prefix — `Rp 150.000` | unverified |
| Decimal places | 0 in practice | unverified |
| Thousands separator | `.` (period); decimal separator `,` (comma) | unverified |
| Typical price magnitude | Roughly 5,000 to 5,000,000 IDR for everyday retail lines | unverified |

**Formatting consequences.** This is the same field-width problem as Vietnam, and
the same inverted separators. Six and seven digit amounts are routine, grouping
uses the period, and a formatter left on English defaults will render `Rp 150,000`
or `Rp 150.000,00` — both wrong. Group by three, no decimals, period as the
group separator. Digit grouping is a correctness feature here, not decoration: an
ungrouped seven-digit number is genuinely misread at the counter.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | **Statutory 12%**, effective **11%** for non-luxury goods and services via a tax base of 11/12 of the selling price (PMK No. 131 of 2024). Luxury goods subject to PPnBM are taxed at a full 12% on the unadjusted base. | public-regulation |
| Tax-inclusive or exclusive display | Consumer prices quoted tax-inclusive in ordinary practice. `TODO: verify` legal basis. | unverified |
| Fiscal system name | e-Faktur, administered by the Directorate General of Taxes (Direktorat Jenderal Pajak). `TODO: verify` scope for retail B2C. | official-authority |

**Implement the base adjustment, not the shortcut.** The prescribed computation is
12% applied to 11/12 of the price. Applying 11% directly gives the same answer in
most cases and a different one in some, depending on where rounding lands. For a
high-volume till the discrepancy accumulates into a reconciliation problem that
is tedious to diagnose after the fact. Model it as the regulation states, with the
adjusted base as an explicit intermediate value the system can show.

This also means the tax engine needs a per-product notion of luxury versus
non-luxury, because the two use different bases — not merely different rates.
`TODO: verify` which catalogue items that reaches.

## Receipt requirements

`TODO: verify` the mandatory field list for a B2C retail sale — this file does not
yet have a confirmed list, and the e-Faktur obligations documented for B2B do not
automatically describe what a shop must hand a walk-in customer.

**Paper widths:** 80 mm (typically 48 or 42 characters at Font A) and 58 mm
(32 characters). Indonesian item names are long and the amounts are wide; at
58 mm, plan for the name and the amount on separate lines.

## Languages used in retail

Bahasa Indonesia is the working language of retail. It is Latin script with no
diacritics in commercial use, so unlike Vietnamese it presents no thermal printer
encoding difficulty — the default code page is sufficient.

**Back office in one language, till in another.** Chinese-owned shops and
wholesalers commonly run purchasing, stock and reporting in Chinese with the
cashier interface and printed receipt in Bahasa Indonesia. One data set, interface
language resolved per user, print template language set independently. Products
need two names: an internal one the owner recognises and an Indonesian one that
prints on the receipt and shelf label.

## Payment methods

| Method | Notes |
| --- | --- |
| QRIS | The national interoperable QR standard. One merchant QR accepts payment from any participating wallet or bank app, which simplifies acceptance considerably compared with markets where each wallet needs its own integration. Settlement is not instant to the POS; the sale closes on confirmation. |
| E-wallets | Several major wallets, most reachable through QRIS rather than needing separate merchant integrations. |
| Cash | Substantial, particularly outside major cities. |
| Cards | Debit and credit through bank terminals; POS-to-terminal integration is not universal. |
| Bank transfer | Wholesale and account customers. |

Record a reference for every non-cash tender and support split tender.

## Notes for POS implementers

**Amount width and grouping first.** Everything else is downstream of getting
seven-digit rupiah amounts rendering correctly in the till, on the receipt, on the
customer display, in reports and in the tendered-amount field — commonly five
different formatters.

**Keep the tax base visible.** Because the effective rate arises from a base
adjustment rather than a rate, store the adjusted base alongside the tax amount.
Auditing a discrepancy later without it is guesswork.

**Time zones — plural.** Indonesia spans three: WIB (UTC+7), WITA (UTC+8) and
WIT (UTC+9). A chain with stores in different zones cannot use one server-side
local time. Store timestamps with offset and make the business-day boundary a
per-store setting.

**Character set.** No special handling required. Where a Chinese-language back
office is also in play, raster receipt rendering remains the simplest way to keep
one print path for both scripts.


## Food service

Restaurants diverge from retail at the till, not just in the menu. Three things
change: the tax treatment can depend on where the food is eaten, service charge
and tips carry their own rules and their own tax questions, and the trading day
routinely runs past midnight. Indonesia's food-service tax is worth checking separately, because restaurant and hotel services are commonly handled under a regional levy rather than the national VAT covered above.

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

**Do not assume the retail VAT treatment carries over.** `TODO: verify` whether food service falls under a regional restaurant tax rather than PPN, which authority administers it, and what that means for the receipt. If it is a separate levy, the 11/12 base adjustment documented in the retail sections does not apply, and reusing it would be wrong.

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
