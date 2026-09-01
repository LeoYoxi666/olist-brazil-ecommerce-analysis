# Olist Brazil E-commerce Operations Diagnosis

## Scope

This first-pass report uses delivered orders as completed transactions and
uses purchase month through `2018-08` for trend analysis.
The data does not contain campaign exposure, product cost, or commission data;
therefore, this report does not claim campaign causality, advertising ROI, or
accounting profit.
Risk rankings require at least 100 completed orders per
state, 20 per seller, and
10 per seller-state lane. These are operational
sample guards, not statistical-significance claims.

## Executive baseline

| Metric | Value |
|---|---:|
| Completed orders | 96,478 |
| Merchandise GMV | 13,221,498.11 |
| Active buyers | 93,358 |
| Average delivery days | 12.13 |
| Late delivery rate | 8.11% |
| Average review score | 4.16 / 5 |

## Executive decision priorities

| Rank | Priority area | Current signal | Historical scope | Merchandise GMV | Recommended next action |
|---:|---|---:|---:|---:|---|
| 1 | Retention Growth | 3.00% | 74,153 qualified target customers | 10,369,095.96 | run segmented retention holdout tests |
| 2 | Delivery Service | 8.11% | 7,826 late orders | 1,158,920.51 | execute lane and dispatch reviews |
| 3 | Category Experience | 4.01 / 5 | 6 top gmv below average categories | 4,984,859.38 | review quality and freight before growth |

Commercial value is historical merchandise GMV within the diagnostic scope;
it is not forecast uplift, recoverable revenue, or accounting profit.

## Initial findings

1. **Growth scaled materially during 2017.** The monthly GMV and order charts
   show a strong ramp-up, with the highest complete-month volume in November
   2017. This is a seasonal signal, not proof of a specific campaign effect.
2. **Retention is the clearest growth opportunity.** Weighted cohort retention
   is 0.48% in month 1, 0.26% in month 3,
   and 0.23% in month 6. 41
   cohort-RFM groups meet the volume and follow-up guards.
   The top target is the 2017-11 `at_risk` group, with 2,702 target customers and 719,732.08 in merchandise GMV.
3. **Late delivery is closely associated with poor satisfaction.** On-time
   orders average 4.29 points,
   versus 2.57 for late orders.
   The relationship is diagnostic, not a causal experiment.
4. **Delivery risk is concentrated enough for targeted action.**
   24 states and 804 sellers meet the minimum
   volume guards. The top qualified lane is seller `4a3ca9315b744ce9f8e9374361493884` (SP to SP), with 58 late orders across 800 completed orders.
5. **Category quality needs to be managed alongside sales.** The category
   output combines GMV, freight share, and ratings; high-volume, low-rating
   categories should not be optimized on sales alone.

## Recommended next actions

1. Work through `cohort_rfm_targets.csv` in priority order. Use the recommended
   journey as a test hypothesis, maintain a holdout group, and measure
   incremental repeat purchase and GMV rather than raw post-campaign totals.
2. Work through `seller_state_delivery_actions.csv` in priority order. Review
   seller dispatch SLA where dispatch consumes at least
   35% of delivery time; otherwise review
   carrier lane capacity and routing.
3. Review the top categories with low ratings or high freight share before
   proposing assortment or promotion changes.
4. Recalculate the action list after each intervention window and compare both
   late-order volume and customer review outcomes.

## Generated artifacts

- [Monthly GMV chart](analysis/monthly_gmv.svg)
- [Monthly orders chart](analysis/monthly_orders.svg)
- [Top categories chart](analysis/top_categories_gmv.svg)
- [State late-delivery chart](analysis/state_late_delivery.svg)
- [Customer cohort retention heatmap](analysis/cohort_retention.svg)
- [Cohort-RFM retention priorities](analysis/cohort_rfm_targets.svg)
- `executive_summary.csv`: three-row management decision summary
- `cohort_rfm_targets.csv`: volume- and follow-up-qualified retention queue
- `seller_state_delivery_actions.csv`: qualified lane-level action list

See `../docs/executive_summary_methodology.md`,
`../docs/cohort_rfm_targeting_methodology.md`, and
`../docs/delivery_risk_methodology.md` for ranking logic and interpretation
limits.
