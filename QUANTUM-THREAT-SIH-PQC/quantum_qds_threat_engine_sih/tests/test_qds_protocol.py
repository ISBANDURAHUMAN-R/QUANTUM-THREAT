"""
Unit tests for QDS Protocol lifecycle, arbitration, and signature verification.
"""

from core.qds_protocol import TeleportationQDSProtocol

def test_qds_honest_verification_deterministic():
    """Verify that honest signatures are deterministically verified and accepted by both Bob and Charlie."""
    protocol = TeleportationQDSProtocol(security_parameter_N=64, rng_seed=123)
    sig_pkg, telemetry = protocol.sign_message("BLOCKCHAIN_TRANSACTION_#001")
    
    # Bob verifies
    res_bob = protocol.verify_signature(sig_pkg, verifier="Bob")
    assert res_bob.is_valid is True
    assert abs(res_bob.qber_signature - 0.0) < 1e-5
    assert abs(res_bob.qber_decoy - 0.0) < 1e-5
    
    # Charlie verifies
    res_charlie = protocol.verify_signature(sig_pkg, verifier="Charlie")
    assert res_charlie.is_valid is True
    assert abs(res_charlie.qber_signature - 0.0) < 1e-5
    
    # Arbitration
    arb = protocol.dispute_arbitration(res_bob, res_charlie)
    assert arb["arbitration_passed"] is True
    assert arb["status"] == "MUTUAL_ACCEPTANCE"

def test_qds_wrong_session_nonce_rejected():
    """Verify that a forged or altered session nonce is immediately rejected."""
    protocol = TeleportationQDSProtocol(security_parameter_N=32, rng_seed=456)
    sig_pkg, _ = protocol.sign_message("MESSAGE_ALPHA")
    
    sig_pkg.session_nonce = "INVALID_TAMPERED_NONCE"
    res = protocol.verify_signature(sig_pkg, verifier="Bob")
    assert res.is_valid is False
