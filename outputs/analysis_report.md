# Olist Brazil E-commerce Operations Diagnosis

## Scope

This first-pass report uses delivered orders as completed transactions and
uses purchase month through `2018-08` for trend analysis.
The data does not contain campaign exposure, product cost, or commission data;
therefore, this report does not claim campaign causality, advertising ROI, or
accounting profit.

## Executive baseline

| Metric | Value |
|---|---:|
| Completed orders | 96,478 |
| Merchandise GMV | 13,221,498.11 |
| Active buyers | 93,358 |
| Average delivery days | 12.13 |
| Late delivery rate | 8.11% |
| Average review score | 4.16 / 5 |

## Initial findings

1. **Growth scaled materially during 2017.** The monthly GMV and order charts
   show a strong ramp-up, with the highest complete-month volume in November
   2017. This is a seasonal signal, not proof of a specific campaign effect.
2. **Retention is the clearest growth opportunity.** The RFM output should be
   used to target repeat purchase journeys because the historical buyer base
   is dominated by low-frequency customers.
3. **Late delivery is closely associated with poor satisfaction.** On-time
   orders average 4.29 points,
   versus 2.57 for late orders.
   The relationship is diagnostic, not a causal experiment.
4. **Demand and service are regionally uneven.** The state output ranks both
   transaction value and delivery risk so that logistics interventions can be
   prioritized by impact.
5. **Category quality needs to be managed alongside sales.** The category
   output combines GMV, freight share, and ratings; high-volume, low-rating
   categories should not be optimized on sales alone.

## Recommended next actions

1. Use `rfm_segments.csv` to define a first retention test for new-active,
   loyal, champions, and at-risk users.
2. Use `state_metrics.csv` and `seller_metrics.csv` to create a late-delivery
   action list by state and seller.
3. Review the top categories with low ratings or high freight share before
   proposing assortment or promotion changes.
4. Add cohort retention and seller-volume minimums before turning these
   baseline signals into operational targets.

## Generated artifacts

- [Monthly GMV chart](analysis/monthly_gmv.svg)
- [Monthly orders chart](analysis/monthly_orders.svg)
- [Top categories chart](analysis/top_categories_gmv.svg)
- [State late-delivery chart](analysis/state_late_delivery.svg)
