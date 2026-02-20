# Pricing Policy: Expected Value Optimisation

## 1. What Expected Value (EV) Optimises

Our system does not simply predict what a car will sell for. A perfect price prediction is useless if we never win the car, or if we overpay and lose money.

Instead, we optimise for **Expected Value (Profit)**:

```
EV(offer) = P(win|offer) × (Expected Sale Price − offer − Expected Costs)
```

- A low offer means high margin, but low total profit because `P(win)` drops to near zero.
- A high offer means high `P(win)`, but low or negative margin.
- The optimiser finds the exact point on the curve that maximises the `EV(offer)` rectangle.

## 2. Deterministic Cost Modeling

We calculate `Expected Costs` transparently:

- Base cost: £250/vehicle.
- Damage penalty: +£500 if reported.
- Channel cost: Dealer (£100), Private (£200), Fleet (£50).
- Region Risk: Adds up to +£100 based on historical regional variances.

This ensures the EV calculation accounts for the total cost of acquisition.

## 3. The Tail-Risk Penalty

Using the average `E(sale)` is dangerous for high-variance vehicles (e.g., old luxury cars). To protect the downside, we subtract a penalty using the 10th percentile (`q10`) of the sale price distribution.

```
tail_penalty = max(0, offer_price - expected_price_q10)
```

If our offer exceeds the pessimistic `q10` scenario, we penalise the EV by `λ * tail_penalty`. This naturally lowers our offers on highly uncertain vehicles, protecting the business from catastrophic margin losses.

## 4. Volume vs Margin Trade-off

By adjusting `λ` (the risk penalty) or setting a minimum acceptable margin threshold in the optimiser:

- **Aggressive Growth**: Set `λ=0`, accept lower margins to win volume.
- **Cash Preservation**: Set `λ=1` or `min_margin=£500` to win fewer, highly profitable cars.
