"""Classical cryptographic asset and post-quantum readiness assessment.

This module complements the existing quantum/QDS simulator.  It is intentionally
usable without a live PKI: an asset can be assessed from metadata, a payload can
be hashed with SHA-256, and the engine produces an explainable 0-100 risk score.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


CLASSICAL = {"RSA", "ECDSA"}
PQC = {"ML-DSA", "SLH-DSA"}


@dataclass
class CryptoAsset:
    name: str = "demo-artifact.bin"
    algorithm: str = "RSA"
    key_size: int = 2048
    certificate_status: str = "valid"
    signature_status: str = "valid"
    sensitive: bool = True
    data_lifetime_years: int = 10
    suspicious_activity: float = 0.0
    certificate_issuer_trusted: bool = True


class CryptoReadinessEngine:
    """Explainable assessment engine for SIH crypto-migration workflows."""

    def hash_sha256(self, payload: str | bytes) -> str:
        data = payload.encode("utf-8") if isinstance(payload, str) else payload
        return hashlib.sha256(data).hexdigest()

    def assess(self, asset: CryptoAsset, payload: Optional[str | bytes] = None) -> Dict[str, Any]:
        algorithm = asset.algorithm.upper().replace("_", "-")
        reasons = []
        score = 0.0

        # Classical signature quantum exposure.
        if algorithm in CLASSICAL:
            score += 45
            reasons.append(f"{algorithm} is vulnerable to Shor's algorithm in a sufficiently capable quantum computer.")
            if asset.data_lifetime_years >= 5:
                score += 15
                reasons.append("Long-lived data increases harvest-now-decrypt-later / future migration exposure.")
        elif algorithm in PQC:
            score += 5
            reasons.append(f"{algorithm} is a post-quantum signature family; quantum exposure is substantially reduced.")
        else:
            score += 25
            reasons.append("Signature algorithm is unknown to the readiness policy and requires manual review.")

        if algorithm == "RSA" and asset.key_size < 2048:
            score += 10
            reasons.append("RSA key size is below the recommended 2048-bit baseline.")
        if algorithm == "ECDSA" and asset.key_size < 256:
            score += 10
            reasons.append("ECDSA curve strength is below the common 256-bit baseline.")

        if asset.certificate_status.lower() != "valid":
            score += 20
            reasons.append("Certificate validation failed or is not currently trusted.")
        if not asset.certificate_issuer_trusted:
            score += 15
            reasons.append("Certificate issuer is outside the configured trust policy.")
        if asset.signature_status.lower() != "valid":
            score += 25
            reasons.append("Digital signature verification failed.")
        if asset.suspicious_activity > 0:
            score += min(20, asset.suspicious_activity * 20)
            reasons.append("Suspicious activity/anomaly telemetry increased the operational risk.")
        if asset.sensitive:
            score += 5
            reasons.append("Asset is marked sensitive, so cryptographic migration has higher priority.")

        score = round(min(100.0, score), 1)
        if score >= 75:
            level = "CRITICAL"
        elif score >= 50:
            level = "HIGH"
        elif score >= 25:
            level = "MEDIUM"
        else:
            level = "LOW"

        recommendation = self._recommendation(algorithm, level, asset.data_lifetime_years)
        digest = self.hash_sha256(payload) if payload is not None else None

        return {
            "asset": asdict(asset),
            "normalized_algorithm": algorithm,
            "sha256": digest,
            "classical_security": "PASS" if asset.signature_status.lower() == "valid" and asset.certificate_status.lower() == "valid" else "FAIL",
            "quantum_risk": "HIGH" if algorithm in CLASSICAL else ("LOW" if algorithm in PQC else "UNKNOWN"),
            "risk_score": score,
            "risk_level": level,
            "recommendation": recommendation,
            "reasons": reasons,
            "threat_mapping": {
                "diginotar": "certificate_trust_compromise",
                "solarwinds": "valid_signature_does_not_guarantee_safe_software",
                "harvest_now_decrypt_later": asset.data_lifetime_years >= 5,
                "shors_algorithm": algorithm in CLASSICAL,
            },
        }

    def _recommendation(self, algorithm: str, level: str, lifetime: int) -> Dict[str, str]:
        if algorithm == "RSA" or algorithm == "ECDSA":
            target = "ML-DSA"
            if level == "CRITICAL" or lifetime >= 10:
                action = "Prioritize immediate PQC migration and use crypto-agility/hybrid deployment during transition."
            else:
                action = "Plan migration to ML-DSA and inventory all dependent certificates, keys and signatures."
            return {"target": target, "alternative": "SLH-DSA", "action": action}
        if algorithm in PQC:
            return {"target": algorithm, "alternative": "SLH-DSA" if algorithm == "ML-DSA" else "ML-DSA", "action": "Maintain PQC key rotation, certificate lifecycle controls and algorithm-agility testing."}
        return {"target": "ML-DSA", "alternative": "SLH-DSA", "action": "Identify the signature primitive and perform a manual cryptographic inventory before migration."}


def demo_assessment(**kwargs: Any) -> Dict[str, Any]:
    asset = CryptoAsset(**kwargs)
    return CryptoReadinessEngine().assess(asset, payload=kwargs.get("payload"))
