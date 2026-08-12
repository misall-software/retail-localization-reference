# Philippines — Retail & POS Localization

**You cannot deploy an arbitrary POS in the Philippines.** The machine itself must
be registered with the Bureau of Internal Revenue before it may issue receipts,
and the software has to implement specific behaviours to qualify — sequential
numbering that cannot be reset, Z-reading, and statutory discount handling. Two
further things are unusual: senior citizen and person-with-disability discounts are
a legal entitlement that changes the tax computation, not a promotion; and BIR
accreditation and e-invoicing registration are separate obligations that do not
substitute for each other.

> ### Verification status — partially verified, 2026-08
>
> Checked against secondary sources. Confirm against BIR before relying on any of
> it — this is the market in this repository where getting it wrong stops you
> trading rather than merely producing a defective receipt.
>
> **Resolved this pass**
>
> - POS registration now proceeds via an **Acknowledgement Certificate**, which
>   replaced the former Permit to Use (PTU). Application through the eAccReg
>   system; BIR Form 1907 is the associated form.
> - Machines must support sequential numbering, Z-reading, and senior
>   citizen / PWD discount handling.
> - **EIS** (Electronic Invoicing System) compliance for Group 1 — taxpayers using
>   CAS or invoicing software — is due **31 December 2026** under RR 26-2025
>   (issued 2025-09-05), which extended RR 11-2025.
> - CAS accreditation and EIS compliance are **separate**; holding one does not
>   satisfy the other.
> - POS users are described as Group 2 with no confirmed e-invoicing deadline.
>
> **Still open — `TODO: verify`**
>
> 1. Whether the intended deployment falls in Group 1 or Group 2, which determines
>    whether the 2026-12-31 deadline applies.
> 2. The complete documentary requirements and current processing time for an
>    Acknowledgement Certificate.
> 3. The exact SC/PWD computation and its interaction with VAT, including the
>    order of operations and rounding.
> 4. What identifying details must be captured and printed for an SC/PWD sale.
> 5. Full mandatory receipt field list.
> 6. Current VAT rate and registration threshold, and the percentage tax
>    alternative for non-VAT taxpayers.
> 7. Whether reaccreditation is required after a software version change.
> 8. Taxpayer identification number (TIN) format and validation rules.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `PHP` | official-authority |
| Symbol | `₱` (U+20B1) | official-authority |
| Symbol position | Prefix — `₱ 1,250.00` | unverified |
| Decimal places | 2 | official-authority |
| Thousands separator | `,`; decimal separator `.` | unverified |
| Typical price magnitude | Roughly 20 to 5,000 PHP for everyday retail lines | unverified |

The peso sign is outside the default printer code page. Verify it prints on the
target hardware; fall back to `PHP` rather than shipping a box character.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | 12% standard. Non-VAT taxpayers below the registration threshold pay percentage tax instead. `TODO: verify` current rate and threshold. | public-regulation |
| Tax-inclusive or exclusive display | Consumer prices quoted VAT-inclusive in ordinary practice; the receipt must break out the VAT components. `TODO: verify` the required breakdown. | unverified |
| Fiscal system name | Bureau of Internal Revenue (BIR). POS registration via **Acknowledgement Certificate** (formerly Permit to Use) through eAccReg. **EIS** is the separate electronic invoicing system. | official-authority |

### Senior citizen and PWD discounts

This has no equivalent in most of the markets covered here, and it is not a
discount in the commercial sense. Qualifying customers are entitled by statute to
a discount **and** to VAT exemption on the qualifying portion. The consequences for
the POS:

- The sale is not simply reduced; the qualifying portion leaves the VAT base.
  A percentage discount applied on top of a normal VAT-inclusive line produces the
  wrong tax and the wrong reported sales.
- The customer's identifying details must be captured and appear on the receipt.
- The transaction must be separately reportable.

`TODO: verify` the computation, the order of operations against VAT, the rounding
rule, and exactly what must be captured and printed. **Do not implement this from
inference** — it is audited, and it is a common source of assessments.

## Receipt requirements

Behaviours the machine must support — `public-regulation`, `TODO: verify` the
complete current list:

- **Sequential numbering** that cannot be reset or reused
- **Z-reading** — the end-of-day reading, with accumulated totals retained
- **SC/PWD discount** handling and reporting as above
- Registration details of the machine printed on the receipt
- `TODO: verify` full mandatory field list

**Paper widths:** 80 mm (48 or 42 characters at Font A) and 58 mm (32).

## Languages used in retail

Filipino and English are both official; **commercial documents and POS interfaces
are in English**, and English is broadly understood by retail staff. This makes the
Philippines one of the easier markets for interface language: an English till
needs no translation work and creates no hiring barrier.

Chinese-owned businesses commonly run a Chinese back office with an English till
and English receipts. Both are plain Latin script, so there is no printer encoding
difficulty on the local-language side.

## Payment methods

| Method | Notes |
| --- | --- |
| E-wallets | GCash and Maya are the dominant non-cash rails, including for small amounts. Confirmation is typically visual at the counter. |
| Cash | Substantial. |
| Cards | Through bank terminals; POS-to-terminal integration varies. |
| Bank transfer | InstaPay and PESONet for account and wholesale customers, with different clearing behaviour. |

Capture a reference for every non-cash tender; support split tender.

## Notes for POS implementers

**Accreditation is a gating dependency with a lead time.** It is not a
post-deployment formality. Build the timeline around it, and confirm early whether
a software change requires reaccreditation — `TODO: verify` — because that
determines how you can ship updates to a live site.

**Z-reading is a persistence requirement, not a report.** Accumulated totals must
survive, and the numbering must not restart. This constrains how the system
handles reinstalls, database resets and hardware replacement — decide the answer
before a customer's machine dies rather than after.

**Model SC/PWD in the tax engine, not the discount engine.** Building it as a
promotional discount is the single most common way to get the Philippines wrong,
and the error surfaces at audit rather than at the till.

**Time zone.** UTC+8, no daylight saving.


## Food service

Restaurants diverge from retail at the till, not just in the menu. Three things
change: the tax treatment can depend on where the food is eaten, service charge
and tips carry their own rules and their own tax questions, and the trading day
routinely runs past midnight. The Philippines is the strictest market here for food service, because the statutory discounts and the machine accreditation both apply in full.

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

**SC/PWD discounts apply to restaurant bills and are harder there.** On a shared table only the qualifying diner's portion attracts the discount and the VAT exemption, which means the bill has to be apportioned before the discount is computed. `TODO: verify` the apportionment rule — this is a documented source of assessments and must not be implemented from inference.

**Accreditation covers the food-service machine too.** The sequential numbering and Z-reading obligations in the retail sections apply unchanged.

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
