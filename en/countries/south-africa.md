# South Africa — Retail & POS Localization

**Two things shape a South African deployment, and neither is the tax rate.**
First, power. Scheduled and unscheduled outages are a structural feature of trading
here, which makes offline capability and battery-backed hardware a baseline
requirement rather than a resilience nicety. Second, lay-by is a regulated consumer
contract under the Consumer Protection Act, not an informal arrangement — if the
shop offers it, the software has to model it properly. VAT itself is stable at 15%
after the 2025 increases were reversed.

> ### Verification status — partially verified, 2026-08
>
> Checked against secondary sources. Confirm against SARS before relying on any of
> it.
>
> **Resolved this pass**
>
> - VAT remains **15%**. The proposed increases to 15.5% (2025-05-01) and 16%
>   (2026-04-01) were reversed by the Rates and Monetary Amounts Bill introduced
>   2025-04-24, and the 2026 Budget confirmed 15% for 2026/27.
> - The compulsory VAT registration threshold rises from **R1 million to
>   R2.3 million**, reported effective **2026-04-01**.
>
> **Still open — `TODO: verify`**
>
> 1. Full tax invoice versus abridged tax invoice — the value threshold that
>    separates them and the fields each requires.
> 2. Whether any mandatory e-invoicing or fiscalisation obligation now applies, and
>    the current state of SARS's modernisation programme.
> 3. Lay-by requirements under the Consumer Protection Act: deposit handling,
>    cancellation and refund rules, and what the customer document must state.
> 4. Whether displayed consumer prices are legally required to be VAT-inclusive.
> 5. Number formatting convention for commercial documents — separator and decimal
>    marker.
> 6. VAT vendor number format and validation rules.
> 7. Local outage schedule and connectivity at the intended location.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `ZAR` | official-authority |
| Symbol | `R` | official-authority |
| Symbol position | Prefix — `R1 234,56` | unverified |
| Decimal places | 2 | official-authority |
| Thousands separator | Space is the formal convention, with comma as the decimal marker; the Anglo form `R1,234.56` is also widely seen. `TODO: verify` which to use on commercial documents. | unverified |
| Typical price magnitude | Roughly 10 to 5,000 ZAR for everyday retail lines | unverified |

The separator ambiguity is worth settling explicitly at configuration time rather
than inheriting a locale default — the two conventions invert each other's
meaning, and `1 234,56` versus `1,234.56` is the kind of difference that survives
testing and fails in front of a customer.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | **15%**, unchanged. The 2025 proposal to raise it to 15.5% and then 16% was reversed. | public-regulation |
| Registration threshold | Rising from R1 million to **R2.3 million**, reported effective 2026-04-01. Relevant to small retailers who may fall out of the VAT net. | public-regulation |
| Tax-inclusive or exclusive display | Consumer prices quoted VAT-inclusive in ordinary practice. `TODO: verify` legal basis. | unverified |
| Fiscal system name | SARS (South African Revenue Service). No clearance-model e-invoicing mandate identified for retail; a modernisation programme is under way. `TODO: verify` current obligations. | official-authority |

**Full versus abridged tax invoice.** South Africa distinguishes a full tax invoice
— which carries the recipient's details — from an abridged one usable below a
value threshold. This is the same shape of problem as Peru's boleta/factura split:
the cashier needs to know which document the customer needs, and capturing
recipient details after the fact is rework. `TODO: verify` the threshold and the
required fields for each.

## Receipt requirements

`TODO: verify` the field lists per invoice type. Paper widths: 80 mm (48 or 42
characters at Font A) and 58 mm (32).

## Lay-by

Lay-by is common in South African retail and is **regulated under the Consumer
Protection Act** — `TODO: verify` the detailed requirements. What the software must
support, at minimum:

- A held item that is not delivered until paid in full, with stock reserved rather
  than sold
- A payment schedule against an open agreement, with each instalment receipted
- Cancellation and refund handling, which is where the statutory rules bite
- A customer-facing document stating the terms

Modelling lay-by as a sequence of unrelated part-payments loses the agreement, the
stock reservation and the audit trail. It has to be its own object.

## Languages used in retail

South Africa has twelve official languages. **English dominates commercial
documentation** — receipts, price lists, invoices — while spoken interaction at the
counter varies by region and community, commonly isiZulu, isiXhosa, Afrikaans,
Sesotho or Setswana.

For POS purposes English is the safe default for both the till interface and the
printed receipt, and all the relevant languages are Latin script with no thermal
printing difficulty. Chinese-owned businesses follow the usual pattern: Chinese
back office, English till and receipts.

## Payment methods

| Method | Notes |
| --- | --- |
| Cards | Dominant. South Africa is a card-heavy market by regional standards, with contactless standard and card present in a large share of retail transactions. Terminal integration is correspondingly more important here than in mobile-money markets. |
| Cash | Substantial, particularly in township and informal retail. |
| QR wallets | Present alongside cards. |
| EFT | Account and wholesale customers. |
| Lay-by | Not a payment method as such, but it drives a receivable and a payment schedule — see above. |

## Notes for POS implementers

**Design for power loss first.** This is the defining local constraint. Offline
selling, battery-backed terminals and printers, and a resume path after an abrupt
shutdown are baseline requirements. An abrupt power cut mid-transaction must not
corrupt the day's totals or lose the sequence — test that specific failure, not
just network loss.

**Card terminal integration earns its keep here.** In a market where most
transactions are card, manual amount entry into a standalone terminal is a real
source of error and a real reconciliation cost.

**Settle the number format explicitly.**

**Time zone.** UTC+2, no daylight saving.

---

_Last updated: 2026-08_
