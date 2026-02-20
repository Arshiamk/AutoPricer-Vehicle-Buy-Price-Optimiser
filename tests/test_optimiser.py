from app.optimiser import compute_ev, optimise_offer, compute_expected_costs

def test_compute_ev_zero_win_prob():
    ev = compute_ev(offer=5000, p_win=0.0, e_sale=7000, e_costs=500, price_q10=6000)
    assert ev <= 0.0

def test_compute_ev_tail_penalty_reduces_ev():
    ev_no_penalty = compute_ev(offer=6500, p_win=0.5, e_sale=8000, e_costs=500, price_q10=7000, risk_lambda=0.0)
    ev_with_penalty = compute_ev(offer=6500, p_win=0.5, e_sale=8000, e_costs=500, price_q10=6000, risk_lambda=1.0)
    assert ev_with_penalty < ev_no_penalty

def test_optimise_offer_valid_range():
    # p_win is always 0.5 for simplicity
    result = optimise_offer(e_sale=10000, price_q10=8000, e_costs=500, predict_p_win_func=lambda off: 0.5)
    assert 0 < result["recommended_offer"] < 10000
    assert result["expected_value"] > 0
    assert "explanation" in result

def test_optimise_offer_no_profitable_margin():
    result = optimise_offer(e_sale=2000, price_q10=1800, e_costs=2000, predict_p_win_func=lambda off: 0.8)
    assert result["recommended_offer"] == 0.0
    assert result["expected_value"] == 0.0
