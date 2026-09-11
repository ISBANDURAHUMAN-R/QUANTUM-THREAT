"""
Quantum Cyber Threat Detection Dashboard Web Server.

Lightweight built-in HTTP server providing REST API endpoints and serving the Cyber-Quantum UI:
- POST /api/simulate (runs attack or honest protocol)
- GET /api/benchmark (retrieves benchmark metrics and plots)
- POST /api/reset (resets session replay memory)
- Static file serving (HTML5, CSS3, ES6 JS)
"""

import sys
import os
import json
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.qds_protocol import TeleportationQDSProtocol
from threat_detection.threat_detector import QuantumThreatDetector
from simulation.attack_simulator import QuantumAttackSimulator
from simulation.benchmark_engine import BenchmarkEngine

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
BENCHMARK_DIR = os.path.abspath('benchmark_results')

# Global protocol instances
global_protocol = TeleportationQDSProtocol(security_parameter_N=128)
global_detector = QuantumThreatDetector()
global_simulator = QuantumAttackSimulator(protocol=global_protocol, detector=global_detector)

class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/status':
            self._send_json({
                "status": "ONLINE",
                "security_parameter_N": global_protocol.N,
                "decoy_qubits": global_protocol.num_decoy,
                "total_qubits": global_protocol.total_qubits,
                "ev_threshold": global_protocol.ev,
                "ed_threshold": global_protocol.ed,
                "baseline_noise": global_detector.baseline_noise,
                "active_sessions_count": len(global_protocol.active_sessions),
                "recorded_incidents_count": len(global_detector.incident_history)
            })
        elif parsed_path.path == '/api/benchmark':
            bench_file = os.path.join(BENCHMARK_DIR, "benchmark_summary.json")
            if os.path.exists(bench_file):
                with open(bench_file, 'r') as f:
                    data = json.load(f)
                self._send_json({"status": "SUCCESS", "benchmark_data": data})
            else:
                # Run quick benchmark
                bench = BenchmarkEngine(output_dir=BENCHMARK_DIR)
                data = bench.run_multi_vector_evaluation(iterations_per_attack=25, security_parameter_N=128)
                bench.generate_security_curves()
                bench.generate_roc_and_threat_radar(data)
                self._send_json({"status": "SUCCESS", "benchmark_data": data["summary"]})
        elif parsed_path.path.startswith('/benchmark_images/'):
            # Serve generated benchmark images
            filename = parsed_path.path.replace('/benchmark_images/', '')
            img_path = os.path.join(BENCHMARK_DIR, filename)
            if os.path.exists(img_path):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(img_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Image not found")
        else:
            # Fall back to static files
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/simulate':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = json.loads(post_data) if post_data else {}
            
            attack_type = params.get('attack_type', 'honest')
            message = params.get('message', 'TRANSACTION_ORDER_REF_2026')
            
            global_detector.anti_replay.reset()
            
            if attack_type == 'honest':
                res = global_simulator.execute_honest_protocol(message=message)
            elif attack_type == 'intercept_resend':
                prob = float(params.get('intercept_prob', 1.0))
                res = global_simulator.simulate_intercept_resend_attack(message=message, intercept_probability=prob)
            elif attack_type == 'cnot_probe':
                theta = float(params.get('probe_theta', 0.785))
                res = global_simulator.simulate_cnot_entanglement_probe(message=message, probe_coupling_theta=theta)
            elif attack_type == 'mitm':
                res = global_simulator.simulate_quantum_mitm(message=message)
            elif attack_type == 'existential_forgery':
                res = global_simulator.simulate_existential_forgery(forged_message="FORGED_PAYLOAD_EVE")
            elif attack_type == 'dishonest_bob':
                res = global_simulator.simulate_dishonest_receiver_forgery(message=message)
            elif attack_type == 'replay':
                res = global_simulator.simulate_replay_attack(message=message)
                # Format replay payload
                res = {
                    "attack_type": "REPLAY_ATTACK",
                    "threat_report": res["round_2_replayed"],
                    "round_1_report": res["round_1_legitimate"]
                }
            elif attack_type == 'channel_jamming':
                noise = float(params.get('noise_level', 0.20))
                res = global_simulator.simulate_quantum_channel_jamming(message=message, noise_level=noise)
            else:
                res = global_simulator.execute_honest_protocol(message=message)
                
            # Serialize report
            sanitized_report = self._sanitize_for_json(res)
            self._send_json({"status": "SUCCESS", "result": sanitized_report})
            
        elif parsed_path.path == '/api/reset':
            global_detector.anti_replay.reset()
            global_protocol.active_sessions.clear()
            global_protocol.alice_private_states.clear()
            self._send_json({"status": "SUCCESS", "message": "State cache and nonces cleared."})
        else:
            self.send_error(404, "Endpoint not found")

    def _sanitize_for_json(self, obj):
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items() if k not in ("qubits_bob", "qubits_charlie", "bell_pairs_bob", "bell_pairs_charlie", "state_vec")}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(v) for v in obj]
        elif isinstance(obj, (int, float, str, bool)) or obj is None:
            return obj
        elif hasattr(obj, '__dict__'):
            return self._sanitize_for_json(obj.__dict__)
        else:
            return str(obj)

    def _send_json(self, data: dict):
        response_bytes = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', str(len(response_bytes)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_bytes)

def start_server(port: int = 8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    print(f"\n[+] Quantum Cyber Threat Detection Dashboard Server running at http://localhost:{port}")
    print("    Press Ctrl+C to terminate.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server shutdown requested.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_server(port)
