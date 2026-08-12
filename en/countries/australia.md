# Australia — Retail & POS Localization

**Australia is regulatorily light on receipts and heavy on consumer contract
rules.** There is no fiscalisation, no clearance model, and no accredited-device
regime: a tax invoice is required only on request, and not at all below a small
threshold. What does carry hard requirements is lay-by, which the Australian
Consumer Law defines precisely and requires in writing. GST is a flat 10% with no
expiry attached, which after Vietnam, Thailand and Peru is worth noting as the
exception rather than the norm.

> ### Verification status — partially verified, 2026-08
>
> Checked against secondary sources. Confirm against the ATO and the ACCC before
> relying on any of it.
>
> **Resolved this pass**
>
> - A tax invoice must be provided within **28 days of request**, except for sales
>   of **$82.50 (including GST) or less**.
> - For taxable sales **under $1,000**, a tax invoice must show: that the document
>   is intended to be a tax invoice; the seller's identity; the seller's **ABN**;
>   the date of issue; and a brief description of the items including quantity and
>   price.
> - Lay-by under the ACL: an agreement for the sale of goods, paid in **three or
>   more instalments** (including any deposit), goods **not supplied until paid in
>   full**, and **no interest** charged.
> - Lay-by agreements **must be in writing** with a copy provided to the customer
>   (electronic is acceptable), and must be transparent. Terms should cover the
>   goods, total price, deposit, payment schedule, termination rights and any
>   termination fee.
>
> **Still open — `TODO: verify`**
>
> 1. Additional tax invoice requirements for sales of **$1,000 or more**,
>    including buyer identity.
> 2. When GST is attributable on a lay-by sale — at deposit, at each instalment, or
>    on delivery. This determines what the BAS shows and cannot be guessed.
> 3. The permitted basis and cap for a lay-by termination fee.
> 4. Whether e-invoicing obligations apply to the business in question.
> 5. GST registration threshold.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `AUD` | official-authority |
| Symbol | `$` | official-authority |
| Symbol position | Prefix — `$1,234.56` | unverified |
| Decimal places | 2 | official-authority |
| Thousands separator | `,`; decimal separator `.` | unverified |
| Typical price magnitude | Roughly 2 to 500 AUD for everyday retail lines | unverified |

Cash rounding to the nearest 5 cents is standard practice, the 1 and 2 cent coins
having been withdrawn — `TODO: verify` whether this is mandatory. As elsewhere,
record the rounding as its own amount rather than adjusting a price.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| GST rate | **10%**, flat, with no scheduled expiry. GST-free and input-taxed categories exist — notably most basic food — and are defined by schedule. | public-regulation |
| Tax-inclusive or exclusive display | Consumer prices are quoted GST-inclusive. `TODO: verify` the legal basis. | unverified |
| Fiscal system name | ATO (Australian Taxation Office). **No fiscalisation or clearance obligation** for retail. Peppol-based e-invoicing exists for B2B and B2G contexts — `TODO: verify` whether it applies. | official-authority |

**GST-free food is the practical tax complexity.** Most basic food is GST-free
while prepared and packaged food generally is not, and the boundary is defined by
schedule rather than by intuition. For a grocery or convenience catalogue this
means per-product tax categories are unavoidable and must be editable — the same
requirement as Kenya, arrived at for a different reason.

## Receipt requirements

The obligation is demand-driven, which is unusual in this repository:

- A tax invoice must be provided **within 28 days of the customer requesting it**
- No tax invoice is required for sales of **$82.50 including GST or less**
- Under $1,000, the required content is the list in the verification block above
- `TODO: verify` the additional requirements at $1,000 and above

In practice a retailer prints a receipt for every sale regardless; the legal
requirement is a floor, not a description of normal practice. The design
consequence is that the POS must be able to produce a compliant **tax invoice**
on demand — including after the fact — rather than only the standard slip.

**Paper widths:** 80 mm (48 or 42 characters at Font A) and 58 mm (32).

## Lay-by

This is the regulated part of Australian retail, and the reason this file exists
alongside South Africa's. Under the ACL a lay-by is defined by four
characteristics together: sale of goods, three or more instalments including any
deposit, goods withheld until paid in full, and no interest.

What the software must support:

- A **written agreement** generated at the point of sale, with a copy to the
  customer — electronic delivery is acceptable. This is not optional and not
  satisfied by a receipt.
- The agreement content: goods, total price, deposit, payment schedule,
  termination rights, and any termination fee.
- Stock **reserved, not sold**, until final payment.
- Instalments recorded against the open agreement, each receipted.
- Termination and refund handling, including any fee — `TODO: verify` the
  permitted basis and cap.

**The GST timing question is the one to resolve early** — open item 2. When GST
becomes attributable on a lay-by determines what the business activity statement
reports, and getting it wrong produces a misstated return rather than a cosmetic
defect.

New Zealand and South Africa have comparable lay-by practices with their own
rules; do not carry Australian assumptions across without checking.

## Languages used in retail

English throughout — interface, receipts, documentation. Plain Latin script, no
thermal printing difficulty. Chinese-owned businesses commonly run a Chinese back
office against an English till, the simplest instance of the pattern documented
elsewhere in this repository.

## Payment methods

| Method | Notes |
| --- | --- |
| Cards | Strongly dominant, contactless by default, including for very small amounts. Terminal integration matters more than in cash or transfer-led markets. |
| Account-to-account | PayID and Osko for real-time transfers; more common in B2B and services than at a retail counter. |
| Cash | Declining; note the 5 cent rounding. |
| BNPL | Present in some retail segments; each provider settles and reconciles on its own terms, so treat each as a distinct tender type. |

## Notes for POS implementers

**Lay-by is the feature that decides fit.** In a market with no fiscalisation, no
device accreditation and a flat tax, lay-by is where a general-purpose POS most
often falls short — and modelling it as instalment payments against an ordinary
sale fails both the stock reservation and the written agreement requirements.

**Tax invoice on demand, after the fact.** Support reissuing a compliant tax
invoice for a past sale, including adding buyer details.

**Time zones — plural, with daylight saving.** Australia spans multiple zones and
some states observe daylight saving while others do not. A multi-store deployment
cannot assume one offset, and the business-day boundary must be per-store. This is
the most error-prone environmental detail in this file.


## Food service

Restaurants diverge from retail at the till, not just in the menu. Three things
change: the tax treatment can depend on where the food is eaten, service charge
and tips carry their own rules and their own tax questions, and the trading day
routinely runs past midnight. Australia has no fiscalisation to worry about, so the food-service questions here are about consumer law and GST categories rather than about the tax authority.

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

**GST-free food and prepared food are the boundary that matters.** Basic food is generally GST-free while prepared food generally is not, which means a venue selling both — a bakery, a cafe with a retail shelf — needs per-item tax categories and cannot apply one rate to the ticket. `TODO: verify` where the boundary falls for the intended menu.

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
