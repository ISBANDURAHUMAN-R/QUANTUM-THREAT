import unittest
from crypto_readiness import CryptoAsset, CryptoReadinessEngine

class TestCryptoReadiness(unittest.TestCase):
    def setUp(self):
        self.engine = CryptoReadinessEngine()

    def test_sha256(self):
        self.assertEqual(self.engine.hash_sha256('abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')

    def test_rsa_quantum_risk(self):
        r = self.engine.assess(CryptoAsset(algorithm='RSA', key_size=2048, data_lifetime_years=10))
        self.assertEqual(r['quantum_risk'], 'HIGH')
        self.assertEqual(r['recommendation']['target'], 'ML-DSA')
        self.assertGreaterEqual(r['risk_score'], 50)

    def test_ecdsa_quantum_risk(self):
        r = self.engine.assess(CryptoAsset(algorithm='ECDSA', key_size=256, data_lifetime_years=3))
        self.assertEqual(r['quantum_risk'], 'HIGH')
        self.assertIn("Shor", ' '.join(r['reasons']))

    def test_pqc_low_quantum_risk(self):
        r = self.engine.assess(CryptoAsset(algorithm='ML-DSA', data_lifetime_years=10))
        self.assertEqual(r['quantum_risk'], 'LOW')
        self.assertEqual(r['risk_level'], 'LOW')

    def test_invalid_signature_raises_risk(self):
        r = self.engine.assess(CryptoAsset(algorithm='RSA', signature_status='invalid', certificate_status='invalid'))
        self.assertEqual(r['classical_security'], 'FAIL')
        self.assertGreaterEqual(r['risk_score'], 50)

if __name__ == '__main__':
    unittest.main()
