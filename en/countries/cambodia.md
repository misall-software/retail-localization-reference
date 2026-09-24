# Cambodia — Retail & POS Localization

**Cambodia prices in one currency, is paid in two, and wants the document in a
third form of both.** US dollars are commonly described as dominating retail
pricing and cash, with the riel (KHR) circulating alongside and used for change
below one dollar. The
rules point the other way: a Ministry of Commerce prakas requires price tags in
riel, and the invoice rules require the invoice total to be disclosed in riel at
the National Bank of Cambodia's daily rate. The second requirement is that
invoices be written in Khmer — and Khmer has no printer code page on any
platform, so the invoice rule settles the print path before any other decision is
made. The consumption tax is VAT at 10%, administered by the General Department of
Taxation (GDT).

> ### Verification status — partially verified, 2026-09
>
> Researched 2026-09-24. **Every item below was checked against secondary sources**
> — tax-practice publications, a legal database summary, and the central bank's
> own payment-system pages for KHQR. Only the KHQR items were read from the
> authority itself. Confirm everything else against the instrument or the GDT
> before relying on it.
>
> **Found — reconfirm before relying on it**
>
> - VAT **10%** standard rate; zero rate for exports and specified supplies.
> - Two invoice types for a registered taxpayer: a **tax invoice** to a registered
>   buyer, a **commercial invoice** to an end user. Small taxpayers issue
>   commercial invoices only. (Prakas No. 723 MEF, 2019-08-14; GDT Notification
>   No. 3218, 2020-02-06.)
> - Invoices in **Khmer**, with any foreign language **below** the Khmer text.
> - The invoice total must be **disclosed in riel** at the **NBC daily exchange
>   rate**; the previous day's rate may be used before working hours or on
>   non-working days.
> - Invoice numbers run sequentially **per year**, with separate series per
>   branch and per invoice type, and the rule is stated to apply to POS users.
> - Price tags must be in **riel**; foreign-currency pricing needs a permit valid
>   for one year (Prakas No. 172 MOC, 2017-07-07, amending Prakas No. 047).
> - **KHQR** is the national QR payment standard, administered by the National
>   Bank of Cambodia, and carries KHR or USD.
> - E-invoicing platform **CamInvoice** launched by Prakas No. 075 MEF,
>   2025-01-22. Mandatory for business-to-government only; business-to-business
>   voluntary; **business-to-consumer out of scope**.
>
> **Still open — `TODO: verify`**
>
> 1. The VAT rate and zero-rated list against the current Law on Taxation.
> 2. Whether a POS slip handed to a walk-in customer *is* a commercial invoice
>    under Prakas 723, or a separate document the prakas does not reach.
> 3. The complete mandatory field list for each invoice type, against the text of
>    Prakas 723 and Notification 3218 rather than a summary of them.
> 4. Whether the riel disclosure rule applies to commercial invoices as well as
>    tax invoices, and which rate date governs a sale rung up before the NBC
>    publishes that day's rate.
> 5. Whether Prakas 172 is still the operative price-tag instrument, the number and
>    date of the reported 2023 reiteration, and what enforcement looks like.
> 6. Whether any rule governs the rate a shop uses to give riel change on a dollar
>    sale, or whether the shop's own rate is lawful.
> 7. Whether any private-sector business-to-business mandate on CamInvoice took
>    effect in 2026, and when point-of-sale or consumer invoices come into scope.
> 8. Which body operates CamInvoice. The launching prakas names the General
>    Department of Digital Economy; secondary sources name the GDT.
> 9. Taxpayer identification number (TIN / VATTIN) format and validation.
> 10. The thresholds that classify a taxpayer as small, medium or large, which
>     decide whether the business may issue tax invoices at all.
> 11. The VAT registration thresholds.
> 12. Whether displayed consumer prices are legally required to be tax-inclusive.
> 13. Whether a retailer or restaurant reselling alcohol or tobacco must charge
>     Public Lighting Tax on its own invoice, and at what base.
> 14. Invoice retention periods.
> 15. Whether receipts are expected to carry Khmer digits or Western digits.
> 16. What the NBC requires of a merchant to accept KHQR, and whether a
>     merchant-presented dynamic code is required or customary.

---

## Currency

| Field | Value | Source type |
| --- | --- | --- |
| ISO 4217 code | `KHR` (numeric `116`). The US dollar, `USD` (`840`), is used alongside it in retail — see below. | official-authority |
| Symbol | `៛` — U+17DB KHMER CURRENCY SYMBOL RIEL. Whether shops print the sign, `KHR`, or the Khmer word is a convention `TODO: verify`. | unverified |
| Symbol position | `TODO: verify`. Both prefix and suffix forms are seen in printed material. | unverified |
| Decimal places | **0 in practice.** ISO 4217 lists a minor unit of 2; no subdivision circulates, and the KHQR specification accepts riel amounts as whole numbers only. `TODO: verify` the ISO figure. | unverified |
| Thousands separator | `,` in commercial use is common — `TODO: verify`. | unverified |
| Typical price magnitude | Riel: roughly 1,000 to 500,000 for everyday lines. Dollar: roughly 0.50 to 100. Order of magnitude only, given here to size fields. | unverified |

Confirm the code and denominations against the National Bank of Cambodia (NBC).

### Two currencies at one counter

The currency section in most files in this repository is about formatting. Here
it is about arithmetic. The pattern commonly described — and consistent with
the rules below, which exist because of it — is:

- The shelf price and the menu price are usually in **US dollars**.
- The customer pays in dollars, riel, or a mix of both.
- **Change below one dollar is given in riel**, because US coins do not
  circulate. The rate used at the counter is typically a round figure set by the
  shop rather than the NBC's daily rate. `TODO: verify` whether any rule
  governs it.

A till built for one currency cannot express this. The requirements are:

1. **Tender in two currencies on one sale**, with the amount received recorded
   per currency, not converted and summed.
2. **Change calculated in a currency different from the price**, with the
   remainder below one dollar converted to riel at a counter rate and rounded to
   the smallest riel note in practical use — `TODO: verify` which denomination
   that is; 100 riel is the smallest note commonly cited.
3. **Two rates held at once**: the counter rate used for change, and the NBC
   daily rate used on the invoice (see [Tax](#tax)). They differ, and conflating
   them makes either the drawer or the invoice wrong.
4. **Drawer counts per currency.** The shift close counts dollars and riel
   separately; a single converted drawer total hides every counting error behind
   the exchange rate.

**Riel price tags are required.** The Ministry of Commerce's Prakas No. 172 of
2017-07-07, amending Prakas No. 047, obliges traders, merchants and service
providers to tag prices in Khmer currency, with foreign-currency pricing allowed
for up to one year on approval — `public-regulation`, read from a legal database
summary, not from the Khmer text. Press reporting describes a 2023 reiteration
that requires any approved foreign-currency price to sit **below or after** the
riel price, and describes enforcement as weak. `TODO: verify` both. For a
system, the consequence is the same either way: **shelf labels and menus need a
riel price field that is maintained, not computed at print time from a dollar
price**, because a label printed at one rate and left on a shelf is a price
claim at that rate.

## Tax

| Field | Value | Source type |
| --- | --- | --- |
| VAT rate | **10%** standard. Zero rate for exports and specified supplies; a list of exempt supplies. | public-regulation |
| Tax-inclusive or exclusive display | The commercial invoice issued to an end user shows a **total inclusive of all taxes**; the tax invoice to a registered buyer shows the value exclusive of tax with each tax on its own line. `TODO: verify` whether inclusive *shelf* display is a legal requirement. | public-regulation |
| Other taxes that reach the invoice | **Specific Tax**, **Public Lighting Tax** (5% on alcohol and tobacco) and **Accommodation Tax** (2% of the accommodation fee) each have their own line on a tax invoice. `TODO: verify` which of them a retailer or restaurant has to charge rather than simply pay within its purchase price. | public-regulation |
| Invoice currency rule | The invoice total must also be shown **in riel**, converted at the **NBC daily exchange rate**; the previous day's rate may be used on non-working days or before working hours. | public-regulation |
| Fiscal system name | **CamInvoice** — the Cambodia E-Invoicing System, launched by Prakas No. 075 MEF of 2025-01-22. UBL XML, centralised validation. Mandatory for business-to-government invoicing only; business-to-business voluntary; **business-to-consumer not in scope**. No fiscal device or POS registration requirement identified — `TODO: verify`. | public-regulation |

**Who issues which invoice.** Per GDT Notification No. 3218 of 2020-02-06,
implementing Prakas No. 723 MEF of 2019-08-14:

| Issuer | To a registered buyer | To an end user |
| --- | --- | --- |
| Medium or large taxpayer | Tax invoice | Commercial invoice |
| Small taxpayer | Commercial invoice | Commercial invoice |

A medium or large buyer cannot claim input VAT on a purchase from a small
taxpayer. That makes the issuer's size class a sales question, not only a filing
question: a business supplying other businesses needs to know which class it is
in before it chooses a till, because a till that cannot issue tax invoices is
unusable for one class and irrelevant for the other. `TODO: verify` the
classification thresholds.

**The riel disclosure is not a display preference.** A dollar-priced sale
produces an invoice that has to carry a riel total at a rate the shop does not
set and that changes daily. The system needs the NBC rate as dated reference
data, stored against each invoice at issue, and reprinted from the stored value
— never recomputed from today's rate.

## Receipt requirements

### Mandatory fields

From a tax-practice summary of Notification 3218 — **not the text of the
prakas**, and `TODO: verify` in full.

**Tax invoice**

- Seller's name, address and TIN — `public-regulation`
- Sequential invoice number and date — `public-regulation`
- Buyer's name, address and TIN — `public-regulation`
- Description, quantity and price — `public-regulation`
- Total exclusive of taxes — `public-regulation`
- Each tax on its own line: Specific Tax, Public Lighting Tax, Accommodation Tax,
  VAT — `public-regulation`
- Signature and name — `public-regulation`
- Total in riel at the NBC daily rate — `public-regulation`

**Commercial invoice**

- Seller's name, address and TIN — `public-regulation`
- Sequential invoice number and date — `public-regulation`
- Buyer's name and address — `public-regulation` `TODO: verify` how this is met
  for an anonymous walk-in sale
- Description, quantity and price — `public-regulation`
- Total inclusive of all taxes — `public-regulation`
- Seller's signature and name — `public-regulation` `TODO: verify` how this is met
  on a printed POS slip
- Total in riel at the NBC daily rate — `public-regulation` `TODO: verify`
  whether this applies to commercial invoices

The two `TODO` items on signature and buyer name are the practical question for a
retail counter, and they are open item 2 at the top of this file.

### Language

**Khmer, with any foreign language below it** — `public-regulation`. GDT
Instruction No. 1127 of 2016 stated this for invoices, and Notification 3218
restated it in 2020. The 2016 instruction was reported as allowing English for
technical terms where a system could not render Khmer; `TODO: verify` whether
that allowance survives.

This is the requirement that decides the print path. **No code page exists for
Khmer** on any platform — see
[Khmer, Lao and Burmese](../languages/khmer-lao-burmese.md) — so a Khmer
invoice from a thermal printer is a raster image, rendered by the POS with a
shaping engine. A printer chosen for its code page support has chosen nothing
here.

### Numbering

- Sequential **per year** — `public-regulation`.
- A **separate series for each branch** and for the head office, and **separate
  series for tax invoices and commercial invoices** — `public-regulation`.
- Letter prefixes may distinguish branch series; they may **not** be used to
  split series by product, area or activity — `public-regulation`.
- Stated to apply to POS users — `public-regulation`.

Series is therefore a function of (branch, invoice type, year). A deployment
that allocates a series per terminal — common elsewhere — produces a structure
the rule does not describe. `TODO: verify` whether multiple terminals in one
branch may share a series or must.

### QR code

No QR obligation on a retail invoice identified. CamInvoice documents carry a
verification code, but consumer invoices are not in CamInvoice's scope —
`TODO: verify`.

### Common paper widths

- **80 mm** — fixed counters. Typically 576 dots at 203 dpi.
- **58 mm** — handhelds. Typically 384 dots.

Character-per-line counts do not apply to the Khmer text: it is raster, and its
width is measured in dots. A Khmer line with subscript consonants also needs
more vertical space than a Latin line — set line height from the rendered
Khmer, not from the Latin font.

## Languages used in retail

Khmer is the official language and the language of the invoice. English is
common in urban retail and in hospitality, and appears below the Khmer on
bilingual invoices. Chinese is widespread in Chinese-owned businesses in Phnom
Penh and Sihanoukville.

**Back office in one language, till in another — and the invoice in a third
layout.** The common split is a Chinese back office, a till that staff read in
Khmer or English, and an invoice that has to be Khmer-first with English below.
That is three independent settings:

- **Back office language**, per user.
- **Till interface language**, per user.
- **Invoice template**, pinned to Khmer-over-foreign regardless of either.

The product record needs a **Khmer name** that is stored and printed, not
translated at print time, alongside whatever names the owner and staff read.
A product catalogue imported from a Chinese supplier arrives without one; plan
for the data entry.

## Payment methods

| Method | Notes |
| --- | --- |
| KHQR | The national QR standard, administered by the NBC over its Bakong system and built on EMVCo; one code is accepted across participating banks and wallets. Carries **KHR or USD**. In the specification riel amounts are whole numbers and dollar amounts take two decimals. | 
| Cash | Dollars and riel, frequently both on one sale — see [Two currencies at one counter](#two-currencies-at-one-counter). |
| Cards | Present in urban retail and hospitality. `TODO: verify` terminal integration options. |

**A KHQR payment has a currency.** A dollar-denominated code settles in dollars,
and a riel-denominated code settles in riel. The tender record needs the currency
of the payment as well as the amount, and the daily settlement reconciles per
currency. A dollar-priced sale paid by a riel code is a conversion at the moment
of payment, at a rate the POS must record.

Record a reference for every non-cash tender; confirmation at the counter is
often visual.

## Food service

Restaurants share the retail problems above — two currencies, Khmer-first
invoices, riel disclosure — and add the usual ones.

### Tax treatment

| Question | Answer | Source type |
| --- | --- | --- |
| Dine-in, takeaway and delivery taxed differently? | `TODO: verify` | unverified |
| Reduced rate or registration threshold for small food businesses? | No reduced VAT rate for food service identified. Small taxpayers issue commercial invoices only — see [Tax](#tax). `TODO: verify`. | unverified |
| Alcoholic drinks taxed separately? | Public Lighting Tax applies to alcohol and tobacco at 5%. `TODO: verify` whether it is charged on a restaurant bill or only upstream. | public-regulation |

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
| Must individual menu items be itemised? | The commercial invoice requires description, quantity and price, which implies itemisation. `TODO: verify`. | public-regulation |
| Are table number and guest count mandatory fields? | `TODO: verify` | unverified |

### Operating conventions

**Trading day and the midnight boundary.** `TODO: verify` whether any rule
governs the accounting date of a sale after midnight. It interacts with the riel
disclosure rule: a sale at 00:30 is converted at *which* day's NBC rate? Make the
business-day boundary configurable, and record the rate date on the invoice
independently of the business day.

**Trading hours.** `TODO: verify` for the intended segment.

**Kitchen ticket language.** A Chinese-reading kitchen, a Khmer- or
English-reading floor, and a Khmer-first invoice is the expected configuration.
The kitchen ticket has no legal language requirement identified and can stay in
Chinese; it must be set independently of both the till and the invoice.

### Notes for POS implementers

Four capabilities separate a food-service till from a retail one:

- **Floor plan and table state** — a sale is attached to a table, not opened and
  closed in one pass.
- **Tab allocation** — split by item and split evenly are different operations,
  and both get asked for. In Cambodia each split can also be paid in a different
  currency.
- **Guest count** — per-head reporting, and `TODO: verify` whether any document
  requires it.
- **Tip adjustment** — the amount must be adjustable after card authorisation
  without reopening the sale.

**Split bills in two currencies.** One table, three payers, one pays in dollars,
one in riel, one by a riel KHQR code. Each part is a tender in its own currency
against one invoice, which has one riel disclosure at one NBC rate. A split
model that converts every payment to the bill currency at payment time loses
what was actually handed over.

**Order modifiers are not discounts**, and **void before and after firing are
different events** — as in every other food-service section of this repository.

## Notes for POS implementers

**Render Khmer as raster from the start.** It is required on the invoice and no
code page exists. Size the project on the printer's image throughput, and test
with a Khmer product name containing subscript consonants, read by someone who
reads Khmer.

**Model currency per amount, not per sale.** Price currency, tender currency,
change currency and invoice disclosure currency are four fields that can each
differ on one sale. A sale-level currency field cannot represent a normal
transaction here.

**Keep two rate tables and never merge them.** The NBC daily rate is reference
data with a date, used for the invoice disclosure and stored on each invoice.
The counter rate is a shop setting, used for change. Reporting that converts at
one rate will not reconcile against a drawer that was counted at the other.

**Riel rounding is a remainder, not a discount.** Converting the sub-dollar
remainder to riel and rounding to a practical note leaves a difference of a few
hundred riel. Record it as its own amount so the drawer and the sale agree.

**Invoice series keyed on branch, type and year.** Build it that way from the
first release; migrating a live numbering scheme is harder than any other change
in this file.

**Watch CamInvoice for a consumer phase.** Consumer invoices are out of scope
today, and the published roadmap describes wider business coverage in 2026–2027.
A POS that stores each invoice as structured data with seller TIN, buyer TIN,
lines, taxes and the riel total is already most of the way to a UBL document;
one that only stores print images is not.

**Time zone.** Indochina Time, UTC+7, no daylight saving. `Asia/Phnom_Penh`.

_Last updated: 2026-09_

---

_Maintained by the MISAll team. Last updated: 2026-08_
