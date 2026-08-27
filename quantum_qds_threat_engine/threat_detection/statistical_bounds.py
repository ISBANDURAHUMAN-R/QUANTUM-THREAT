"""
Statistical Bounds & Information-Theoretic Security Proofs.

Provides non-AI statistical test methods:
- Exact Binomial hypothesis testing (p-values)
- Hoeffding's inequality confidence bounds
- Chernoff bounds for anomaly confidence
- Kullback-Leibler (KL) divergence
- Information-theoretic upper bounds on forgery and repudiation probabilities
"""

import numpy as np
import math
from typing import Dict, Any, Tuple

def compute_kl_divergence(p: float, q: float) -> float:
    """
    Computes binary Kullback-Leibler divergence:
    D_KL(p || q) = p * ln(p/q) + (1-p) * ln((1-p)/(1-q)).
    """
    p = min(max(p, 1e-12), 1.0 - 1e-12)
    q = min(max(q, 1e-12), 1.0 - 1e-12)
    
    term1 = p * np.log(p / q)
    term2 = (1.0 - p) * np.log((1.0 - p) / (1.0 - q))
    return float(term1 + term2)

def hoeffding_upper_bound(N: int, epsilon: float) -> float:
    """
    Calculates Hoeffding's probability bound for sample deviation:
    P(e - e_0 >= epsilon) <= exp(-2 * N * epsilon^2).
    """
    if N <= 0 or epsilon <= 0.0:
        return 1.0
    exponent = -2.0 * N * (epsilon ** 2)
    # Prevent underflow
    if exponent < -700.0:
        return 0.0
    return float(np.exp(exponent))

def binomial_tail_pvalue(k_observed: int, N: int, p0_null: float = 0.05) -> float:
    """
    Computes exact one-tailed Binomial p-value under Null Hypothesis H0 (benign channel):
    P(K >= k_observed | N, p0).
    """
    if k_observed <= 0:
        return 1.0
    if k_observed > N:
        return 0.0
    if p0_null <= 0.0:
        return 0.0 if k_observed > 0 else 1.0
    if p0_null >= 1.0:
        return 1.0
        
    # Sum binomial terms in log-space for numerical stability
    log_p = math.log(p0_null)
    log_1mp = math.log(1.0 - p0_null)
    
    prob_sum = 0.0
    for k in range(k_observed, N + 1):
        log_comb = math.lgamma(N + 1) - math.lgamma(k + 1) - math.lgamma(N - k + 1)
        log_term = log_comb + k * log_p + (N - k) * log_1mp
        prob_sum += math.exp(log_term)
        
    return min(max(prob_sum, 0.0), 1.0)

def calculate_forgery_probability_bound(
    N: int,
    ev: float = 0.08,
    ed: float = 0.18
) -> Dict[str, float]:
    """
    Computes the information-theoretic upper bound on forgery probability:
    P_forge <= exp(-N * D_KL(ev || ed)).
    """
    kl_div = compute_kl_divergence(ev, ed)
    exponent = -float(N) * kl_div
    
    if exponent < -700.0:
        p_forge_bound = 0.0
    else:
        p_forge_bound = float(np.exp(exponent))
        
    return {
        "security_parameter_N": float(N),
        "ev_threshold": ev,
        "ed_threshold": ed,
        "kl_divergence": kl_div,
        "p_forgery_bound": p_forge_bound,
        "security_bits": float(N * kl_div / np.log(2.0))
    }

def evaluate_statistical_confidence(
    errors_observed: int,
    total_qubits: int,
    baseline_noise: float = 0.03,
    detection_threshold: float = 0.08
) -> Dict[str, Any]:
    """
    Performs full non-AI statistical evaluation of observed error rate:
    - Observed QBER
    - Exact p-value against baseline noise null hypothesis
    - Hoeffding confidence margin
    - Anomaly confidence level (%)
    """
    if total_qubits == 0:
        return {"qber": 0.0, "p_value": 1.0, "confidence": 0.0, "is_anomaly": False}
        
    qber = float(errors_observed / total_qubits)
    p_val = binomial_tail_pvalue(errors_observed, total_qubits, p0_null=baseline_noise)
    
    epsilon = max(0.0, qber - baseline_noise)
    hoeffding_p = hoeffding_upper_bound(total_qubits, epsilon)
    
    # Non-AI decision: Is this statistically anomalous beyond 99.9% confidence?
    is_anomaly = (p_val < 1e-3) or (qber > detection_threshold)
    confidence_pct = (1.0 - p_val) * 100.0
    
    return {
        "qber": qber,
        "p_value": p_val,
        "hoeffding_bound": hoeffding_p,
        "epsilon_deviation": epsilon,
        "confidence_percentage": min(max(confidence_pct, 0.0), 100.0),
        "is_anomaly": is_anomaly
    }
