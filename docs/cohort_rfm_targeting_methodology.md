# Cohort and RFM Targeting Methodology

## Purpose

This analysis combines acquisition timing with current customer value and
lifecycle state. It creates an aggregate retention-planning queue without
publishing customer identifiers or claiming causal campaign impact.

## Customer snapshot

- Use delivered orders and `customer_unique_id`.
- Use August 2018 as the complete observation cutoff.
- `cohort_month` is the month of the first completed purchase.
- `observable_followup_months` is the number of complete calendar months from
  acquisition to the cutoff. Month 3 evaluation requires at least three
  observable follow-up months.

## Tie-stable RFM scoring

Recency and monetary value use percentile bands from 1 to 5. Equal input values
receive the same score. Higher recency scores mean a more recent purchase;
higher monetary scores mean more merchandise GMV.

Frequency is not forced into percentile bands because most buyers placed only
one order. It uses completed order count capped at 5:

```text
f_score = min(completed_order_count, 5)
```

This prevents identical one-time buyers from being arbitrarily split across
frequency scores.

Segments are mutually exclusive and assigned in this order:

1. `champions`: recent repeat buyers with high monetary value;
2. `at_risk`: stale repeat buyers or stale high-value buyers;
3. `loyal`: remaining repeat buyers;
4. `high_value`: remaining high-monetary buyers;
5. `new_active`: recent one-time buyers;
6. `standard`: all remaining buyers.

## Cohort-RFM target groups

The output contains one row per `cohort_month` and `rfm_segment`. It reports
buyers, target customers, repeat buyers, completed orders, merchandise GMV,
target-customer GMV, recency, review score, cohort shares, and follow-up time.

For `new_active`, `high_value`, and `standard`, the target pool is one-time
buyers. For `at_risk`, `loyal`, and `champions`, the full segment is retained
for win-back, loyalty, or advocacy planning.

Priority ranking requires:

- at least 100 buyers in the cohort-segment group;
- at least three observable follow-up months;
- at least one target customer.

Eligible groups rank first by strategic tier, then target-customer count, then
target-customer GMV. The tiers and suggested journeys are:

| Tier | Segment | Suggested journey |
|---:|---|---|
| 1 | `at_risk` | Win-back and service recovery |
| 1 | `high_value` | High-value second-purchase offer |
| 2 | `new_active` | Early second-purchase nudge |
| 2 | `loyal` | Loyalty reinforcement |
| 3 | `champions` | VIP and advocacy |
| 3 | `standard` | Category replenishment nurture |

The tiers are planning rules, not predicted uplift. Any campaign test should
use a holdout group and report incremental repeat purchase, GMV, and customer
experience rather than raw post-campaign totals.
