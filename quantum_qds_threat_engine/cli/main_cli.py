"""
Interactive Command-Line Interface for Quantum-Inspired Cyber Threat Detection.
"""

import sys
import os
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.qds_protocol import TeleportationQDSProtocol
from threat_detection.threat_detector import QuantumThreatDetector
from simulation.attack_simulator import QuantumAttackSimulator
from simulation.benchmark_engine import BenchmarkEngine

def print_banner():
    print(r"""
================================================================================
   ____                      _                                     ____  ____  ____  
  / __ \__  ______ _____  / /___  ______ ___                    / __ \/ __ \/ ___/  
 / / / / / / / __ `/ __ \/ __/ / / / __ `__ \   ______ ______  / / / / / / /\__ \   
/ /_/ / /_/ / /_/ / / / / /_/ /_/ / / / / / /  /_____/_____/  / /_/ / /_/ /___/ /   
\___\_\__,_/\__,_/_/ /_/\__/\__,_/_/ /_/ /_/                 /_____/_____//____/    
                                                                                    
  Quantum-Inspired Cyber Threat Detection for Digital Signature Security (ID: 26141)
  Egreen Quanta | Non-AI / Information-Theoretic Quantum Threat Defense Engine
================================================================================
""")

def display_threat_report(report: dict, attack_name: str):
    print("\n" + "-"*80)
    print(f"  SIMULATION RESULT: {attack_name.upper()}")
    print("-"*80)
    
    threat = report.get("threat_detected", False)
    status_str = "[!] THREAT DETECTED & NEUTRALIZED" if threat else "[OK] AUTHENTIC SIGNATURE ACCEPTED"
    print(f"Status:             {status_str}")
    print(f"Classification:     {report.get('threat_classification')}")
    print(f"Confidence Level:   {report.get('confidence_score', 0):.2f}% (Non-AI Quantum Statistical)")
    print(f"Signature Accepted: {report.get('is_signature_accepted')}")
    print(f"Summary:            {report.get('summary')}")
    print(f"Mitigation Action:  {report.get('mitigation_action')}")
    
    metrics = report.get("metrics", {})
    if "sig_qber" in metrics:
        print(f"Signature QBER:     {metrics['sig_qber']*100:.2f}% (Threshold ev: {metrics.get('verification_threshold_ev', 0.08)*100:.1f}%)")
    if "decoy_qber" in metrics:
        print(f"Decoy QBER:         {metrics['decoy_qber']*100:.2f}%")
    if metrics.get("chsh_metrics"):
        chsh = metrics["chsh_metrics"]
        print(f"Bell-CHSH Witness:  S = {chsh.get('mean_chsh_s', 0):.4f} (Max: 2.8284, Classical Bound: 2.0)")
        print(f"Entanglement Level: {chsh.get('entanglement_level')}")
    if metrics.get("arbitration_result"):
        arb = metrics["arbitration_result"]
        print(f"Dual-Verifier Delta QBER: {arb.get('delta_qber', 0)*100:.2f}% (Dispute ed: {arb.get('dispute_threshold', 0.18)*100:.1f}%)")
    print("-"*80 + "\n")

def run_interactive_cli():
    print_banner()
    protocol = TeleportationQDSProtocol(security_parameter_N=128)
    detector = QuantumThreatDetector()
    simulator = QuantumAttackSimulator(protocol=protocol, detector=detector)
    
    while True:
        print("\nSelect an Operation:")
        print("  1. Run Honest Legitimate Signature (Alice -> Bob & Charlie)")
        print("  2. Simulate Intercept-Resend Eavesdropping Attack")
        print("  3. Simulate CNOT Entanglement Probe Attack")
        print("  4. Simulate Quantum Man-in-the-Middle (MITM) Attack")
        print("  5. Simulate Existential Signature Forgery Attack")
        print("  6. Simulate Dishonest Receiver Forgery (Bob frames Alice)")
        print("  7. Simulate Replay Attack")
        print("  8. Simulate Quantum Channel Jamming")
        print("  9. Run Automated Monte Carlo Benchmark Suite & Export Visual Charts")
        print(" 10. Exit")
        
        choice = input("\nEnter choice [1-10]: ").strip()
        
        detector.anti_replay.reset()
        
        if choice == "1":
            print("\n>> Executing Honest Teleportation QDS Protocol...")
            res = simulator.execute_honest_protocol("CONFIDENTIAL_GOVERNMENT_DIRECTIVE_2026")
            display_threat_report(res["threat_report"], "Honest Transmission")
        elif choice == "2":
            print("\n>> Simulating Active Intercept-Resend Eavesdropping on Quantum Channel...")
            res = simulator.simulate_intercept_resend_attack()
            display_threat_report(res["threat_report"], "Intercept-Resend Eavesdropping")
        elif choice == "3":
            print("\n>> Simulating CNOT Ancilla Entanglement Probe Attack on Bell Pairs...")
            res = simulator.simulate_cnot_entanglement_probe()
            display_threat_report(res["threat_report"], "CNOT Entanglement Probe")
        elif choice == "4":
            print("\n>> Simulating Quantum Man-in-the-Middle (MITM) Attack...")
            res = simulator.simulate_quantum_mitm()
            display_threat_report(res["threat_report"], "Quantum MITM")
        elif choice == "5":
            print("\n>> Simulating Existential Signature Forgery by External Attacker...")
            res = simulator.simulate_existential_forgery()
            display_threat_report(res["threat_report"], "Existential Forgery")
        elif choice == "6":
            print("\n>> Simulating Dishonest Receiver Forgery (Malicious Bob framing Alice to Charlie)...")
            res = simulator.simulate_dishonest_receiver_forgery()
            display_threat_report(res["threat_report"], "Dishonest Receiver Forgery")
        elif choice == "7":
            print("\n>> Simulating Signature Replay Attack...")
            res = simulator.simulate_replay_attack()
            print("\n--- Round 1 (Legitimate First Signature) ---")
            display_threat_report(res["round_1_legitimate"], "Legitimate Original Signature")
            print("\n--- Round 2 (Replayed Signature) ---")
            display_threat_report(res["round_2_replayed"], "Replayed Signature Packet")
        elif choice == "8":
            print("\n>> Simulating Quantum Channel Jamming / Extreme Noise...")
            res = simulator.simulate_quantum_channel_jamming()
            display_threat_report(res["threat_report"], "Quantum Channel Jamming")
        elif choice == "9":
            print("\n>> Running Large-Scale Monte Carlo Benchmarks (N=128, 50 iterations/attack)...")
            bench = BenchmarkEngine(output_dir="benchmark_results")
            data = bench.run_multi_vector_evaluation(iterations_per_attack=50, security_parameter_N=128)
            sec_curves = bench.generate_security_curves()
            radar_path = bench.generate_roc_and_threat_radar(data)
            
            print("\n[+] Benchmark Completed Successfully!")
            print(f"    - Summary Data: {os.path.abspath('benchmark_results/benchmark_summary.json')}")
            print(f"    - Security Curves: {os.path.abspath(sec_curves['plot_saved_to'])}")
            print(f"    - Threat Radar & ROC: {os.path.abspath(radar_path)}")
            print(f"    - Honest Acceptance Rate: {data['summary']['honest_acceptance_rate']*100:.1f}%")
            print(f"    - Mean Latency: {data['summary']['mean_execution_latency_ms']:.2f} ms")
        elif choice == "10":
            print("\nExiting Quantum Threat Detection Framework. Goodbye.")
            break
        else:
            print("[!] Invalid option. Please select 1-10.")

if __name__ == "__main__":
    run_interactive_cli()
