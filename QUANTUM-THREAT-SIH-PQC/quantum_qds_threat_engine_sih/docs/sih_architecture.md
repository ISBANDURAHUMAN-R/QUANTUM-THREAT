# SIH Architecture — Quantum-Safe Digital Signature Readiness

## Goal
Answer: **Is the digital-signature system safe today, and will it remain safe against future quantum threats?**

## Pipeline

1. **Cryptographic asset discovery** — identify signature/hash/certificate metadata.
2. **Integrity verification** — calculate SHA-256 and inspect signature/certificate status.
3. **Threat detection** — combine the existing QDS attack simulator with operational anomaly signals.
4. **Quantum risk assessment** — map RSA/ECDSA to Shor exposure and long-lived data to HNDL exposure.
5. **Risk scoring** — produce an explainable 0–100 score and LOW/MEDIUM/HIGH/CRITICAL level.
6. **Migration advisor** — recommend ML-DSA, with SLH-DSA as an alternative, while preserving crypto-agility.

## Real-world threat mapping

- **DigiNotar (2011):** certificate trust compromise.
- **SolarWinds (2020):** a valid signature alone does not guarantee benign software.
- **Harvest Now, Decrypt Later:** long-lived sensitive data creates future quantum exposure.
- **RSA/ECC + Shor:** sufficiently capable quantum computers threaten the underlying public-key assumptions.

## Scope discipline

The prototype does not attempt to build a cryptographically useful quantum computer or break RSA/ECDSA. Shor's algorithm is represented as a threat model, while the QDS simulator provides experimental quantum attack telemetry. PQC recommendations should be validated against organizational standards and current NIST guidance before production deployment.
