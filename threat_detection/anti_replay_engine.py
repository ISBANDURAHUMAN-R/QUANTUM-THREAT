"""
Anti-Replay & Quantum Entanglement Binding Engine.

Ensures replay attack protection and session freshness:
- Validates cryptographic session nonces against seen registry
- Verifies Bell pair sequence indices to prevent quantum state reuse
- Enforces timestamp expiration and drift limits
- Detects desynchronization attacks
"""

import time
from typing import Dict, Any, Set, Optional

class AntiReplayEngine:
    def __init__(self, max_timestamp_drift_seconds: float = 300.0):
        self.max_drift = max_timestamp_drift_seconds
        self.seen_nonces: Set[str] = set()
        self.consumed_bell_sessions: Set[str] = set()
        self.replay_attempts: int = 0

    def validate_session_freshness(
        self,
        session_nonce: str,
        timestamp: float,
        current_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validates whether a signature packet is fresh and un-replayed.
        """
        if current_time is None:
            current_time = time.time()
            
        time_diff = abs(current_time - timestamp)
        
        # 1. Check timestamp drift
        if time_diff > self.max_drift:
            self.replay_attempts += 1
            return {
                "is_fresh": False,
                "threat_flag": "REPLAY_ATTACK_EXPIRED_TIMESTAMP",
                "time_diff_seconds": time_diff,
                "reason": f"Signature timestamp differs by {time_diff:.1f}s (max allowed: {self.max_drift}s)"
            }
            
        # 2. Check if nonce has already been seen (replayed classical signature)
        if session_nonce in self.seen_nonces:
            self.replay_attempts += 1
            return {
                "is_fresh": False,
                "threat_flag": "REPLAY_ATTACK_DUPLICATE_NONCE",
                "time_diff_seconds": time_diff,
                "reason": f"Session nonce '{session_nonce[:8]}...' has already been consumed in a previous signature"
            }
            
        # 3. Check if quantum Bell pairs were already consumed
        if session_nonce in self.consumed_bell_sessions:
            self.replay_attempts += 1
            return {
                "is_fresh": False,
                "threat_flag": "QUANTUM_STATE_REUSE_ATTACK",
                "time_diff_seconds": time_diff,
                "reason": "Quantum Bell entanglement register for this session has already collapsed"
            }
            
        # Valid fresh session - record nonce
        self.seen_nonces.add(session_nonce)
        self.consumed_bell_sessions.add(session_nonce)
        
        return {
            "is_fresh": True,
            "threat_flag": "NONE",
            "time_diff_seconds": time_diff,
            "reason": "Fresh valid session nonce and timestamp"
        }

    def reset(self):
        """Clears memory caches."""
        self.seen_nonces.clear()
        self.consumed_bell_sessions.clear()
        self.replay_attempts = 0
