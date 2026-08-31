# Cohort Retention Methodology

## Purpose

Monthly cohort retention measures whether customers return after their first
completed purchase. It complements the overall repeat-buyer rate and RFM
segments by showing how repeat activity changes across acquisition months and
customer age.

## Population

- Include orders where `order_status = 'delivered'`.
- Use `customer_unique_id` as the stable customer key.
- Use `order_purchase_timestamp` as the activity date.
- Include activity only through `2018-08`, the last complete trend month.
- Exclude records with a missing customer key or invalid purchase timestamp.

## Definitions

- `cohort_month`: month of the customer's first completed purchase.
- `month_number`: whole calendar months between the activity month and the
  cohort month. The acquisition month is month 0.
- `cohort_size`: unique customers active in month 0.
- `active_buyers`: unique cohort customers purchasing in the specified month.
- `retention_rate`: `active_buyers / cohort_size`.

Each customer is counted at most once in each activity month, even if the
customer places multiple completed orders in that month.

## Interpretation

Month 1, month 3, and month 6 rates measure activity in those exact months;
they are not cumulative survival rates. Recent cohorts have fewer observable
follow-up months, so blank future cells are expected and must not be converted
to zero.

The SVG heatmap displays the most recent 18 cohorts and up to 12 months of
follow-up. The version-controlled CSV retains every observed cohort-month cell.
