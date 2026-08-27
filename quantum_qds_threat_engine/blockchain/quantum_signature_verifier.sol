// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title QuantumDigitalSignatureVerifier
 * @notice On-chain verification and dispute arbitration for Teleportation-based Quantum Digital Signatures (QDS).
 * @dev Problem Statement 26141 - Egreen Quanta (Blockchain & Cybersecurity).
 */
contract QuantumDigitalSignatureVerifier {
    // Quantum Physical & Statistical Thresholds (scaled by 10,000 for basis point precision)
    uint256 public constant VERIFICATION_THRESHOLD_EV = 800;  // 8.00% (800 bps)
    uint256 public constant DISPUTE_THRESHOLD_ED = 1800;     // 18.00% (1800 bps)
    uint256 public constant CHSH_MIN_THRESHOLD = 27000;      // 2.7000 (scaled by 10,000)

    enum SignatureStatus { PENDING, ACCEPTED, REJECTED, DISPUTED, REPUDIATED }

    struct QDSCertificate {
        bytes32 messageHash;
        bytes32 sessionNonce;
        address signer;
        address verifierBob;
        address verifierCharlie;
        uint256 bobQBER;           // in basis points (0 - 10,000)
        uint256 charlieQBER;       // in basis points (0 - 10,000)
        uint256 decoyQBER;         // in basis points (0 - 10,000)
        uint256 chshWitnessS;      // scaled by 10,000 (e.g., 28284 for 2.8284)
        uint256 timestamp;
        SignatureStatus status;
    }

    // Registry of consumed session nonces to prevent replay attacks on-chain
    mapping(bytes32 => bool) public consumedNonces;
    mapping(bytes32 => QDSCertificate) public certificates;

    event SignatureSubmitted(bytes32 indexed sessionNonce, bytes32 indexed messageHash, address indexed signer);
    event SignatureVerified(bytes32 indexed sessionNonce, SignatureStatus status, string decisionReason);
    event ThreatDetected(bytes32 indexed sessionNonce, string threatType, uint256 observedMetric);

    error NonceAlreadyConsumed(bytes32 sessionNonce);
    error InvalidTimestampDrift(uint256 submittedTime, uint256 blockTime);
    error EntanglementViolation(uint256 chshWitness);

    /**
     * @notice Submits and verifies a Teleportation-based QDS multi-verifier certificate on-chain.
     */
    function verifyAndRecordQDSSignature(
        bytes32 messageHash,
        bytes32 sessionNonce,
        address signer,
        address verifierBob,
        address verifierCharlie,
        uint256 bobQBER,
        uint256 charlieQBER,
        uint256 decoyQBER,
        uint256 chshWitnessS,
        uint256 timestamp
    ) external returns (SignatureStatus) {
        // 1. Anti-Replay Verification
        if (consumedNonces[sessionNonce]) {
            emit ThreatDetected(sessionNonce, "REPLAY_ATTACK_DUPLICATE_NONCE", 0);
            revert NonceAlreadyConsumed(sessionNonce);
        }
        consumedNonces[sessionNonce] = true;

        // 2. Timestamp Freshness Window (300 seconds)
        if (block.timestamp > timestamp + 300 || timestamp > block.timestamp + 300) {
            emit ThreatDetected(sessionNonce, "REPLAY_ATTACK_TIMESTAMP_DRIFT", timestamp);
            return SignatureStatus.REJECTED;
        }

        // 3. Entanglement Health Verification (Bell-CHSH)
        if (chshWitnessS < 20000) { // Classical bound S <= 2.0000
            emit ThreatDetected(sessionNonce, "QUANTUM_MAN_IN_THE_MIDDLE_BROKEN_ENTANGLEMENT", chshWitnessS);
            return SignatureStatus.REJECTED;
        }
        if (chshWitnessS < CHSH_MIN_THRESHOLD) {
            emit ThreatDetected(sessionNonce, "CNOT_ENTANGLEMENT_PROBE", chshWitnessS);
            return SignatureStatus.REJECTED;
        }

        // 4. Decoy State Disturbance Check
        if (decoyQBER > VERIFICATION_THRESHOLD_EV) {
            emit ThreatDetected(sessionNonce, "INTERCEPT_RESEND_EAVESDROPPING", decoyQBER);
            return SignatureStatus.REJECTED;
        }

        // 5. Signature Payload QBER Checks
        bool bobAccepted = (bobQBER <= VERIFICATION_THRESHOLD_EV);
        bool charlieAccepted = (charlieQBER <= VERIFICATION_THRESHOLD_EV);

        // 6. Dual-Verifier Arbitration & Non-Repudiation Check
        uint256 deltaQBER = bobQBER > charlieQBER ? (bobQBER - charlieQBER) : (charlieQBER - bobQBER);

        SignatureStatus finalStatus;
        if (bobAccepted && charlieAccepted) {
            finalStatus = SignatureStatus.ACCEPTED;
            emit SignatureVerified(sessionNonce, finalStatus, "Deterministic multi-verifier acceptance.");
        } else if (!bobAccepted && !charlieAccepted) {
            finalStatus = SignatureStatus.REJECTED;
            emit ThreatDetected(sessionNonce, "EXISTENTIAL_SIGNATURE_FORGERY", bobQBER);
            emit SignatureVerified(sessionNonce, finalStatus, "Mutual rejection: High quantum error rate.");
        } else {
            // Asymmetric acceptance: Check dispute threshold
            if (deltaQBER > (DISPUTE_THRESHOLD_ED - VERIFICATION_THRESHOLD_EV)) {
                finalStatus = SignatureStatus.REPUDIATED;
                emit ThreatDetected(sessionNonce, "SIGNER_REPUDIATION_ATTACK", deltaQBER);
                emit SignatureVerified(sessionNonce, finalStatus, "Arbitration failed: Signer repudiation detected.");
            } else {
                finalStatus = SignatureStatus.DISPUTED;
                emit SignatureVerified(sessionNonce, finalStatus, "Arbitration inconclusive: Marginal noise.");
            }
        }

        certificates[sessionNonce] = QDSCertificate({
            messageHash: messageHash,
            sessionNonce: sessionNonce,
            signer: signer,
            verifierBob: verifierBob,
            verifierCharlie: verifierCharlie,
            bobQBER: bobQBER,
            charlieQBER: charlieQBER,
            decoyQBER: decoyQBER,
            chshWitnessS: chshWitnessS,
            timestamp: timestamp,
            status: finalStatus
        });

        emit SignatureSubmitted(sessionNonce, messageHash, signer);
        return finalStatus;
    }

    /**
     * @notice Retrieves verified certificate details by session nonce.
     */
    function getCertificate(bytes32 sessionNonce) external view returns (QDSCertificate memory) {
        return certificates[sessionNonce];
    }
}
