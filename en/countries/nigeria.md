# Nigeria — Retail & POS Localization

**Nigeria is moving to a clearance model on a phased schedule.** FIRS operates
e-invoicing through the Merchant-Buyer Solution: an invoice is submitted for
validation *before* it goes to the buyer, and comes back with an Invoice Reference
Number and a cryptographic stamp. Large taxpayers were brought in from November
2025, with medium and small businesses following on a staged timetable through
2027. VAT is 7.5%, the lowest headline rate in this repository. Bank transfer, not
card and not cash, is the tender the counter has to handle well.

> ### Verification status — partially verified, 2026-08
>
> Checked against secondary sources. Confirm against FIRS before relying on any of
> it — a clearance model rollout in progress is exactly where secondary reporting
> goes stale fastest.
>
> **Resolved this pass**
>
> - VAT rate **7.5%**.
> - E-invoicing runs through the FIRS **Merchant-Buyer Solution (FIRSMBS)**, a
>   clearance model: invoices are submitted for validation before being provided
>   to the buyer and receive an **Invoice Reference Number (IRN)** and a
>   cryptographic stamp.
> - Large taxpayers from **2025-11-01**. Reporting on the subsequent phases is
>   inconsistent: mandatory compliance for remaining VAT-registered businesses is
>   described both as **2026-01-01** and, in a staged form, as medium businesses
>   by **July 2026** and small businesses by **July 2027**.
>
> **Still open — `TODO: verify`**
>
> 1. **The phase dates and which one applies to the business in question.** The
>    sources conflict; this must be resolved against FIRS directly.
> 2. Whether the obligation covers B2C retail sales or only B2B and B2G, and
>    whether B2C is handled by reporting rather than clearance.
> 3. What must be printed on a customer receipt, and whether the IRN and stamp
>    must appear on it.
> 4. Behaviour permitted when clearance is unavailable at the moment of sale.
> 5. Whether displayed consumer prices are legally required to be VAT-inclusive.
> 6. Taxpayer identification number (TIN) format and validation rules.
> 7. Local power and connectivity conditions at the intended location.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `NGN` | official-authority |
| Symbol | `₦` (U+20A6) | official-authority |
| Symbol position | Prefix — `₦12,500.00` | unverified |
| Decimal places | 2 nominally; kobo rarely used in practice | unverified |
| Thousands separator | `,`; decimal separator `.` | unverified |
| Typical price magnitude | Wide, and moving. Everyday retail lines commonly run four to six figures. | unverified |

Two practical notes. The naira sign is outside the default printer code page —
verify it prints, and fall back to `NGN` rather than a box character. And because
the currency has moved substantially in recent years, price lists change more often
than in most markets: bulk price updating and price-change history are worth more
here than a static catalogue import.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | **7.5%** | public-regulation |
| Tax-inclusive or exclusive display | `TODO: verify`. | unverified |
| Fiscal system name | FIRS (Federal Inland Revenue Service), **Merchant-Buyer Solution (FIRSMBS)** — a clearance model returning an IRN and cryptographic stamp. | official-authority |

**Clearance changes the sale flow, not just the reporting.** In a clearance model
the document is not valid until the authority has validated it, which means the
POS is waiting on a response before it can hand the customer a compliant invoice.
Whether that applies at a retail counter — where waiting is not acceptable —
depends on whether B2C is in scope, which is open item 2 and the single most
important thing to resolve before designing the flow.

Do not assume the Kenyan or Peruvian answer transfers. Those are different models
with different offline tolerances.

## Receipt requirements

`TODO: verify` — this file does not yet have a confirmed field list for a customer
receipt, nor confirmation of whether the IRN and cryptographic stamp must be
printed.

**Paper widths:** 80 mm (48 or 42 characters at Font A) and 58 mm (32).

## Languages used in retail

English is the official language and the language of commerce, commercial
documents and POS interfaces. Hausa, Yoruba and Igbo are widely spoken and
regionally dominant in conversation, but printed retail material is English.

Plain Latin script, no thermal printing difficulty. Chinese-owned businesses run
the usual split: Chinese back office, English till and English receipts.

## Payment methods

| Method | Notes |
| --- | --- |
| Bank transfer | The dominant non-cash tender, including for small amounts. The customer transfers and shows confirmation; settlement is not instant to the POS, so the sale closes on visual confirmation. Capture the reference — it is the reconciliation key. |
| USSD | Feature-phone and no-data transfers, widely used. Produces a transaction reference in the same way. |
| Cards | Domestic and international schemes through terminals. |
| Cash | Substantial. |
| Agent networks | Widely used for cash-in and cash-out; relevant to how customers obtain cash rather than to till design directly. |

The reconciliation pattern matters more here than the acceptance pattern: a day's
takings arrive as many small transfers into a bank account, and matching them back
to sales depends entirely on references captured at the till. Make the reference
field mandatory for transfer tenders and editable afterwards.

## Notes for POS implementers

**Resolve the phase and the B2C question before anything else.** Both are open,
both change the architecture, and neither can be inferred.

**Assume power and connectivity interruptions.** Offline selling with a documented
catch-up path is a baseline requirement, not a differentiator — but note that in a
clearance model the legally permitted catch-up behaviour is a compliance question,
not an engineering choice. See open item 4.

**Build for price volatility.** Bulk repricing, effective-dated prices and a
change history are more valuable here than in stable-currency markets.

**Time zone.** UTC+1, no daylight saving.

---

_Last updated: 2026-08_
