"""
Quantum Digital Signature (QDS) Blockchain Oracle Bridge.

Bridges quantum teleportation measurement outcomes, multi-verifier arbitration records,
and threat detection telemetry into Ethereum / EVM-compatible ABI transaction payloads.
"""

import hashlib
import time
import json
from typing import Dict, Any, Tuple
from core.qds_protocol import QDSSignaturePackage, QDSVerificationResult
from threat_detection.threat_detector import QuantumThreatDetector

class QDSBlockchainOracleBridge:
    def __init__(self, contract_address: str = "0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7"):
        self.contract_address = contract_address

    def format_onchain_payload(
        self,
        sig_package: QDSSignaturePackage,
        res_bob: QDSVerificationResult,
        res_charlie: QDSVerificationResult,
        chsh_witness_s: float = 2.8284,
        signer_address: str = "0xAlice11111111111111111111111111111111111",
        bob_address: str = "0xBob2222222222222222222222222222222222222",
        charlie_address: str = "0xCharlie3333333333333333333333333333333333"
    ) -> Dict[str, Any]:
        """
        Encodes QDS signature and multi-verifier metrics into Solidity contract call arguments:
        - messageHash: bytes32
        - sessionNonce: bytes32
        - signer, verifierBob, verifierCharlie: address
        - bobQBER, charlieQBER, decoyQBER: uint256 (basis points)
        - chshWitnessS: uint256 (scaled by 10,000)
        - timestamp: uint256
        """
        msg_hash_bytes32 = "0x" + hashlib.sha256(sig_package.message.encode('utf-8')).hexdigest()
        session_nonce_bytes32 = "0x" + hashlib.sha256(sig_package.session_nonce.encode('utf-8')).hexdigest()
        
        bob_qber_bps = int(round(res_bob.qber_signature * 10000))
        charlie_qber_bps = int(round(res_charlie.qber_signature * 10000))
        decoy_qber_bps = int(round(res_bob.qber_decoy * 10000))
        chsh_scaled = int(round(chsh_witness_s * 10000))
        
        return {
            "target_contract": self.contract_address,
            "function_name": "verifyAndRecordQDSSignature",
            "abi_parameters": {
                "messageHash": msg_hash_bytes32,
                "sessionNonce": session_nonce_bytes32,
                "signer": signer_address,
                "verifierBob": bob_address,
                "verifierCharlie": charlie_address,
                "bobQBER": bob_qber_bps,
                "charlieQBER": charlie_qber_bps,
                "decoyQBER": decoy_qber_bps,
                "chshWitnessS": chsh_scaled,
                "timestamp": int(sig_package.timestamp)
            },
            "status_preview": "ACCEPTED" if (bob_qber_bps <= 800 and charlie_qber_bps <= 800 and chsh_scaled >= 27000) else "REJECTED"
        }
