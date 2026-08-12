# Malaysia — Retail & POS Localization

**Malaysia is mid-rollout, and the phase you fall into decides what you must do.**
LHDN's MyInvois e-invoicing has arrived in turnover-banded waves; Phase 4 went live
1 January 2026 for businesses between RM1 million and RM5 million turnover, and
businesses below RM1 million are exempt. Separately, from 1 January 2026 a
transaction above RM10,000 can no longer be folded into a consolidated invoice —
which is the rule that actually reaches the till. Note also that Malaysia levies
SST, not VAT: the tax model is different in kind from most of this repository.

> ### Verification status — partially verified, 2026-08
>
> Phase structure checked against secondary sources. Confirm against LHDN before
> relying on any of it.
>
> **Resolved this pass**
>
> - Phase 1 from 2024-08-01 (turnover above RM100m); Phase 2 from 2025-01-01
>   (RM25m–RM100m); Phase 3 from 2025-07-01 (RM5m–RM25m); Phase 4 from
>   **2026-01-01** (RM1m–RM5m), with a relaxation period reported to run to
>   2027-12-31.
> - Exemption threshold raised from RM500,000 to **RM1,000,000** effective
>   2026-01-01.
> - From **2026-01-01**, individual e-invoices are required for transactions
>   above **RM10,000**; consolidation is no longer permitted for those.
>
> **Still open — `TODO: verify`**
>
> 1. Current sales tax and service tax rates, and which apply to the intended
>    catalogue. SST is not a single rate.
> 2. Whether the business in question is registered for sales tax, service tax,
>    both or neither, and what that requires on the receipt.
> 3. What a consolidated e-invoice must contain and how often it must be submitted.
> 4. The exact treatment of a walk-in retail sale below RM10,000 that the customer
>    does not request an invoice for.
> 5. What the relaxation period permits in practice and its precise end date.
> 6. Mandatory receipt fields, and whether a QR or validation link is required on
>    the printed slip.
> 7. Whether cash rounding to the nearest 5 sen is mandatory or optional.
> 8. Taxpayer identifier (TIN) format and validation rules.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `MYR` | official-authority |
| Symbol | `RM` | official-authority |
| Symbol position | Prefix — `RM 125.50` | unverified |
| Decimal places | 2 | official-authority |
| Thousands separator | `,`; decimal separator `.` | unverified |
| Typical price magnitude | Roughly 1 to 500 MYR for everyday retail lines | unverified |

**Cash rounding to 5 sen.** Malaysia rounds cash totals to the nearest 5 sen while
card and wallet payments settle to the exact sen — `TODO: verify` whether this is
mandatory. As in Peru, the rounding difference must be recorded as its own amount
on the sale rather than by adjusting a price, or cash takings will not reconcile
against recorded sales and it will look like till shrinkage.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| Consumption tax model | **SST — Sales Tax and Service Tax**, not a VAT. Sales tax applies to goods, service tax to prescribed services, at rates that differ by category. There is no input-tax credit chain of the kind VAT systems use. `TODO: verify` current rates and scope. | public-regulation |
| Tax-inclusive or exclusive display | `TODO: verify`. | unverified |
| Fiscal system name | **MyInvois**, the e-invoicing platform operated by LHDN (Inland Revenue Board). Turnover-banded rollout, Phase 4 live 2026-01-01. | official-authority |

**SST is not VAT, and the difference matters to the data model.** A tax engine
built around a VAT credit chain will model things Malaysia does not have and miss
things it does. Sales tax is typically levied at the manufacturer or import stage
rather than at each sale, so a retailer's obligation may be quite different from
the VAT-style per-line output tax assumed elsewhere in this repository.
`TODO: verify` what the specific business is actually registered for before
designing the tax setup — this is the item most likely to be got wrong by
assumption.

## Receipt requirements

**The RM10,000 rule is the one that reaches the till.** From 1 January 2026, a
transaction above that value needs its own individual e-invoice and cannot be
swept into a consolidated submission. In practice the POS must decide, at the
moment of sale, whether this sale requires buyer details captured for an
individual e-invoice — which means the cashier may need to ask for a TIN
mid-transaction. Design that path deliberately rather than retrofitting it.

Below the threshold, consolidated submission has been the mechanism for B2C
retail — `TODO: verify` its current form, contents and frequency.

`TODO: verify` mandatory printed fields and whether a validation QR is required.

**Paper widths:** 80 mm (48 or 42 characters at Font A) and 58 mm (32).

## Languages used in retail

Malay (Bahasa Malaysia) is the national language; **English is widely used in
commerce**, and Chinese is in everyday commercial use in a way that is unusual
among the markets in this repository. Tamil is also present.

This changes the usual pattern. Elsewhere a Chinese-language back office is paired
with a local-language till out of necessity; in Malaysia a Chinese-owned business
may legitimately run a Chinese till interface as well, depending on who it hires
and serves. The requirement is therefore not "Chinese back office, local till" but
genuine per-user language selection across a wider set — Malay, English and
Chinese all plausible for either role, with the print template set independently.

Malay and English are plain Latin script with no thermal printing difficulty.
Chinese on the receipt needs the same treatment as any CJK output — raster
rendering is the reliable path.

## Payment methods

| Method | Notes |
| --- | --- |
| DuitNow QR | The national interoperable QR standard; one merchant code accepts participating wallets and bank apps. |
| E-wallets | Several major wallets, largely reachable through DuitNow QR rather than individual integrations. |
| Cards | Widely used; contactless is standard. |
| Cash | Still present; note the 5 sen rounding. |
| Bank transfer | Wholesale and account customers. |

## Notes for POS implementers

**Establish the phase and the registration status before anything else.** Turnover
band determines the e-invoicing obligation and date; SST registration determines
the tax treatment. Both are facts about the specific business, not about Malaysia,
and both change what the software must do.

**Build for the threshold decision at the till.** A sale crossing RM10,000 changes
the document required. If that decision only exists in back-office logic, the
cashier will discover it after the customer has left.

**Time zone.** UTC+8, no daylight saving.

**Rounding as data.** Record the 5 sen rounding as its own amount, as above.

---

_Last updated: 2026-08_
