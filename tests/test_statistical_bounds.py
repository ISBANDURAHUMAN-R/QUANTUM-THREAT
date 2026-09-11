"""
Unit tests for statistical confidence bounds, Hoeffding inequality, and Binomial tests.
"""

import numpy as np
from threat_detection.statistical_bounds import (
    compute_kl_divergence, hoeffding_upper_bound,
    binomial_tail_pvalue, calculate_forgery_probability_bound,
    evaluate_statistical_confidence
)

def test_kl_divergence_non_negative():
    """Verify D_KL(p || q) >= 0 with equality iff p = q."""
    assert abs(compute_kl_divergence(0.08, 0.08) - 0.0) < 1e-6
    assert compute_kl_divergence(0.08, 0.18) > 0.0
    assert compute_kl_divergence(0.18, 0.08) > 0.0

def test_hoeffding_upper_bound():
    """Verify Hoeffding probability decays exponentially with sample size N."""
    p_small_N = hoeffding_upper_bound(32, 0.1)
    p_large_N = hoeffding_upper_bound(256, 0.1)
    assert p_small_N > p_large_N
    assert p_large_N <= np.exp(-2.0 * 256 * 0.01)

def test_binomial_tail_pvalue():
    """Verify p-value is near 1 for normal noise and near 0 for anomalous errors."""
    # Under H0 (p0 = 0.05): 2 errors out of 100 is normal
    p_normal = binomial_tail_pvalue(k_observed=2, N=100, p0_null=0.05)
    assert p_normal > 0.80
    
    # 25 errors out of 100 is highly anomalous (p < 1e-8)
    p_attack = binomial_tail_pvalue(k_observed=25, N=100, p0_null=0.05)
    assert p_attack < 1e-8

def test_forgery_probability_scaling():
    """Verify information-theoretic security bound shrinks exponentially with N."""
    b_64 = calculate_forgery_probability_bound(64, ev=0.08, ed=0.18)
    b_256 = calculate_forgery_probability_bound(256, ev=0.08, ed=0.18)
    assert b_256["p_forgery_bound"] < b_64["p_forgery_bound"]
    assert b_256["security_bits"] > b_64["security_bits"]
