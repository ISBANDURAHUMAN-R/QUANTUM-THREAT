"""
One-Click Master Simulation & Benchmark Runner.

Executes:
1. Full Monte Carlo evaluation across all 7 attack vectors & honest baseline.
2. Information-theoretic security scaling curve generation.
3. Attack detection radar & ROC curve visualization.
4. Launch of local interactive web dashboard on http://localhost:8080.
"""

import sys
import os
import time
import subprocess

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from simulation.benchmark_engine import BenchmarkEngine
from ui.dashboard_app import start_server

def main():
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
    output_dir = os.path.abspath("benchmark_results")
    print(f"[*] Initializing Monte Carlo Benchmark Engine (Output: {output_dir})...")
    
    bench = BenchmarkEngine(output_dir=output_dir, rng_seed=42)
    
    print("\n[Step 1/3] Running Large-Scale Attack Simulations (50 iterations/vector, N=128)...")
    t0 = time.perf_counter()
    data = bench.run_multi_vector_evaluation(iterations_per_attack=50, security_parameter_N=128)
    t1 = time.perf_counter()
    
    summary = data["summary"]
    print(f"    [+] Completed in {t1 - t0:.2f}s")
    print(f"    [+] Honest Baseline Acceptance Rate: {summary['honest_acceptance_rate']*100:.1f}%")
    print(f"    [+] Honest False Alarm Rate:         {summary['honest_false_alarm_rate']*100:.2f}%")
    print(f"    [+] Mean Execution Latency:          {summary['mean_execution_latency_ms']:.2f} ms")
    
    print("\n    Attack Vector Detection Rates (Non-AI Quantum Statistical Engine):")
    for attack, rate in summary["attack_detection_rates"].items():
        print(f"      - {attack:25s}: {rate*100:6.1f}% Detection")
        
    print("\n[Step 2/3] Generating Security Scaling Curves & ROC Radar Charts...")
    sec_curves = bench.generate_security_curves()
    radar_path = bench.generate_roc_and_threat_radar(data)
    print(f"    [+] Security Curves Plot: {sec_curves['plot_saved_to']}")
    print(f"    [+] Threat Radar Plot:    {radar_path}")
    print(f"    [+] Summary JSON Export:  {os.path.join(output_dir, 'benchmark_summary.json')}")
    
    print("\n[Step 3/3] Launching Cyber-Quantum Interactive Web Dashboard...")
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
        
    start_server(port=port)

if __name__ == "__main__":
    main()
