# Delivery Risk Prioritization Methodology

## Purpose

This analysis turns delivery performance into an operational review queue. It
prioritizes combinations that affect more completed orders while preventing
very small samples from dominating the rankings.

The output is diagnostic. It identifies where investigation should start; it
does not prove that a seller, carrier, or route caused a delay.

## Population and unit of analysis

- Only delivered orders are included.
- State risk uses the customer's destination state.
- Seller risk uses one aggregated seller record.
- Seller-state actions use one seller-order per origin-state and destination-
  state combination. Multiple items from the same seller in one order are
  aggregated before order counts and rates are calculated.
- Merchandise GMV is item price and excludes freight.

## Minimum-volume guards

| Ranking | Minimum completed orders |
|---|---:|
| Customer state | 100 |
| Seller | 20 |
| Seller-state lane | 10 |

These thresholds are pragmatic operational safeguards. They reduce unstable
rankings from tiny denominators but are not confidence intervals, hypothesis
tests, or evidence of statistical significance.

Rows below the state or seller threshold remain in their metric tables with
`risk_ranking_eligible = False` and no risk rank. Seller-state lanes below the
threshold are excluded from the action list.

## Priority ranking

Eligible rows are ordered by:

1. late-order count, descending;
2. late-delivery rate, descending;
3. merchandise GMV, descending.

Late-order count leads because the first operational goal is to reduce the
largest number of affected orders. Rate and GMV resolve ties and add severity
and commercial context.

## Suggested investigation path

For each qualified seller-state lane:

- If average dispatch time is at least 35% of average delivery time, the
  suggested first review is `seller_dispatch_sla_review`.
- Otherwise, the suggested first review is
  `carrier_lane_capacity_review`.

The 35% split is a triage rule, not a causal model. Teams should validate stock
availability, seller handling, carrier handoff, route capacity, holidays,
distance, product mix, and data completeness before assigning responsibility.

## Output fields

`seller_state_delivery_actions.csv` includes the priority rank, seller ID,
seller origin state, customer destination state, completed and late orders,
merchandise and delayed GMV, dispatch and delivery times, review metrics,
dispatch share, recommended first review, and the applied order threshold.

Recalculate the list after each intervention window and evaluate both
late-order volume and customer review outcomes.
