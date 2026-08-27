// AEGIS-QDS Cyber Defense Terminal Controller (Problem 26141)

let currentSelectedAttack = 'honest';

document.addEventListener('DOMContentLoaded', () => {
    initCrimsonParticleCanvas();
    startClock();
    initAttackSelection();
    loadSystemStatus();
});

// 1. Crimson Matrix Particle Animation Canvas
function initCrimsonParticleCanvas() {
    const canvas = document.getElementById('quantum-bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const count = 40;
    const glyphs = ['|0\u27E9', '|1\u27E9', '|+\u27E9', '|-\u27E9', '|\u03A6+\u27E9', '|\u03A8+\u27E9', '\u03C3_z', '\u03C3_x', '0x1F', '0x7A'];

    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.35,
            vy: (Math.random() - 0.5) * 0.35,
            glyph: glyphs[Math.floor(Math.random() * glyphs.length)],
            size: 10 + Math.random() * 5,
            opacity: 0.12 + Math.random() * 0.2,
            color: Math.random() > 0.3 ? '#ff003c' : '#ffffff'
        });
    }

    function render() {
        ctx.clearRect(0, 0, width, height);

        // Draw laser connections
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 130) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(255, 0, 60, ${0.08 * (1 - dist / 130)})`;
                    ctx.lineWidth = 0.7;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }

        // Draw glyphs
        for (const p of particles) {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0) p.x = width;
            if (p.x > width) p.x = 0;
            if (p.y < 0) p.y = height;
            if (p.y > height) p.y = 0;

            ctx.font = `${p.size}px 'JetBrains Mono', monospace`;
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.opacity;
            ctx.fillText(p.glyph, p.x, p.y);
        }
        ctx.globalAlpha = 1.0;

        requestAnimationFrame(render);
    }
    render();
}

// 2. Real-time Clock
function startClock() {
    const el = document.getElementById('live-clock');
    setInterval(() => {
        const now = new Date();
        if (el) el.innerText = now.toUTCString().split(' ')[4] + ' UTC';
    }, 1000);
}

// 3. Selection
function initAttackSelection() {
    const buttons = document.querySelectorAll('.attack-btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active-attack'));
            btn.classList.add('active-attack');
            currentSelectedAttack = btn.getAttribute('data-attack');
        });
    });
}

function selectAttack(type) {
    currentSelectedAttack = type;
    const buttons = document.querySelectorAll('.attack-btn');
    buttons.forEach(btn => {
        if (btn.getAttribute('data-attack') === type) {
            btn.classList.add('active-attack');
        } else {
            btn.classList.remove('active-attack');
        }
    });
    executeCurrentSimulation();
}

async function loadSystemStatus() {
    try {
        await fetch('/api/status');
    } catch (e) {
        console.warn("Status error:", e);
    }
}

// 4. Run Simulation
async function executeCurrentSimulation() {
    const runBtn = document.getElementById('btn-run-sim');
    const msgInput = document.getElementById('input-message');
    const msg = msgInput ? msgInput.value : "DEFAULT_TRANSACTION";

    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = '<span class="blink-dot"></span> SIMULATING QUANTUM CHANNELS...';
    }

    try {
        const res = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                attack_type: currentSelectedAttack,
                message: msg
            })
        });

        const data = await res.json();
        if (data.status === "SUCCESS") {
            renderTelemetry(data.result);
        }
    } catch (err) {
        console.error("Simulation error:", err);
    } finally {
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.innerHTML = '<span>&#9654; EXECUTE QUANTUM VERIFICATION</span>';
        }
    }
}

// 5. Render HUD Updates
function renderTelemetry(result) {
    const report = result.threat_report || {};
    const metrics = report.metrics || {};
    const isThreat = report.threat_detected;

    // CHSH
    const chshMetrics = metrics.chsh_metrics || {};
    const meanChsh = chshMetrics.mean_chsh_s !== undefined ? chshMetrics.mean_chsh_s : 2.8284;
    const chshEl = document.getElementById('val-chsh');
    const chshBadge = document.getElementById('badge-chsh');
    const chshBar = document.getElementById('bar-chsh');

    if (chshEl) chshEl.innerText = meanChsh.toFixed(4);
    if (chshBadge) {
        if (meanChsh >= 2.70) {
            chshBadge.className = "badge-status status-safe";
            chshBadge.innerText = "MAXIMAL";
        } else if (meanChsh > 2.0) {
            chshBadge.className = "badge-status status-stealth";
            chshBadge.innerText = "PROBED";
        } else {
            chshBadge.className = "badge-status status-danger";
            chshBadge.innerText = "SEPARABLE";
        }
    }
    if (chshBar) {
        const pct = Math.min(Math.max((meanChsh / 2.8284) * 100, 0), 100);
        chshBar.style.width = `${pct}%`;
    }

    // Payload QBER
    const sigQber = metrics.sig_qber !== undefined ? metrics.sig_qber : 0.0;
    const sigQberEl = document.getElementById('val-qber');
    const sigQberBadge = document.getElementById('badge-qber');
    const sigQberBar = document.getElementById('bar-qber');

    if (sigQberEl) sigQberEl.innerText = `${(sigQber * 100).toFixed(1)}%`;
    if (sigQberBadge) {
        if (sigQber <= 0.08) {
            sigQberBadge.className = "badge-status status-safe";
            sigQberBadge.innerText = "PASS";
        } else {
            sigQberBadge.className = "badge-status status-danger";
            sigQberBadge.innerText = "ALARM";
        }
    }
    if (sigQberBar) {
        sigQberBar.style.width = `${Math.min(sigQber * 200, 100)}%`;
    }

    // Decoy QBER
    const decoyQber = metrics.decoy_qber !== undefined ? metrics.decoy_qber : 0.0;
    const decoyQberEl = document.getElementById('val-decoy');
    const decoyQberBadge = document.getElementById('badge-decoy');
    const decoyQberBar = document.getElementById('bar-decoy');

    if (decoyQberEl) decoyQberEl.innerText = `${(decoyQber * 100).toFixed(1)}%`;
    if (decoyQberBadge) {
        if (decoyQber <= 0.08) {
            decoyQberBadge.className = "badge-status status-safe";
            decoyQberBadge.innerText = "PRISTINE";
        } else {
            decoyQberBadge.className = "badge-status status-danger";
            decoyQberBadge.innerText = "COLLAPSED";
        }
    }
    if (decoyQberBar) {
        decoyQberBar.style.width = `${Math.min(decoyQber * 200, 100)}%`;
    }

    // Threat Alert Banner
    const masterBadge = document.getElementById('badge-master-threat');
    const alertBox = document.getElementById('threat-alert-box');
    const alertIcon = document.getElementById('alert-icon');
    const alertTitle = document.getElementById('alert-title');
    const alertDesc = document.getElementById('alert-desc');
    const alertMit = document.getElementById('alert-mitigation');
    const alertConf = document.getElementById('alert-conf');

    if (isThreat) {
        if (masterBadge) {
            masterBadge.className = "badge-status status-danger";
            masterBadge.innerText = report.threat_classification || "THREAT DETECTED";
        }
        if (alertBox) alertBox.className = "threat-banner banner-danger";
        if (alertIcon) alertIcon.innerHTML = "&#9888;";
        if (alertTitle) alertTitle.innerText = `ATTACK IDENTIFIED: ${report.threat_classification || "MALICIOUS INTRUSION"}`;
    } else {
        if (masterBadge) {
            masterBadge.className = "badge-status status-safe";
            masterBadge.innerText = "PRISTINE // ACCEPTED";
        }
        if (alertBox) alertBox.className = "threat-banner banner-safe";
        if (alertIcon) alertIcon.innerHTML = "&check;";
        if (alertTitle) alertTitle.innerText = "AUTHENTIC SIGNATURE DETERMINISTICALLY ACCEPTED";
    }

    if (alertDesc) alertDesc.innerText = report.summary || "No anomalies detected.";
    if (alertMit) alertMit.innerText = report.mitigation_action || "None.";
    if (alertConf) alertConf.innerText = `CONFIDENCE: ${(report.confidence_score || 99.9).toFixed(1)}%`;

    // Mathematical Proofs
    const decoyAnalysis = metrics.decoy_analysis || {};
    const sigStat = decoyAnalysis.sig_stat || {};
    const pval = sigStat.p_value !== undefined ? sigStat.p_value : (isThreat ? 1.4e-11 : 1.0);
    const hoeff = sigStat.hoeffding_bound !== undefined ? sigStat.hoeffding_bound : 2.4e-6;

    const pvalEl = document.getElementById('proof-pval');
    const hoeffEl = document.getElementById('proof-hoeffding');
    if (pvalEl) pvalEl.innerText = pval < 0.001 ? `${pval.toExponential(2)} (REJECT H0)` : `${pval.toFixed(4)} (Safe)`;
    if (hoeffEl) hoeffEl.innerText = `\u2264 ${hoeff.toExponential(2)}`;

    // Arbitration
    const arb = metrics.arbitration_result;
    const bobQberEl = document.getElementById('arb-bob-qber');
    const charlieQberEl = document.getElementById('arb-charlie-qber');
    const bobStatus = document.getElementById('arb-bob-status');
    const charlieStatus = document.getElementById('arb-charlie-status');

    if (bobQberEl) bobQberEl.innerText = `${(sigQber * 100).toFixed(1)}%`;
    if (bobStatus) {
        bobStatus.className = sigQber <= 0.08 ? "badge-status status-safe" : "badge-status status-danger";
        bobStatus.innerText = sigQber <= 0.08 ? "ACCEPTED" : "REJECTED";
    }

    if (arb && charlieQberEl) {
        charlieQberEl.innerText = `${(arb.charlie_qber * 100).toFixed(1)}%`;
        if (charlieStatus) {
            charlieStatus.className = arb.charlie_qber <= 0.08 ? "badge-status status-safe" : "badge-status status-danger";
            charlieStatus.innerText = arb.charlie_qber <= 0.08 ? "ACCEPTED" : "REJECTED";
        }
    }
}

// 6. Tabs
function switchTab(tabId, btn) {
    const tabs = document.querySelectorAll('.tab-view');
    const buttons = document.querySelectorAll('.tab-btn');

    tabs.forEach(t => t.classList.remove('active'));
    buttons.forEach(b => b.classList.remove('active'));

    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');
    if (btn) btn.classList.add('active');
}

async function resetSystemState() {
    try {
        await fetch('/api/reset', { method: 'POST' });
        alert("Quantum state memory & nonces cleared.");
    } catch (e) {
        console.error("Reset failed:", e);
    }
}


// SIH Crypto Readiness / Post-Quantum Migration
let selectedCrypto = 'RSA';
function selectCrypto(algorithm) {
    selectedCrypto = algorithm;
    document.querySelectorAll('[data-crypto]').forEach(btn => btn.classList.toggle('active-attack', btn.dataset.crypto === algorithm));
}

async function runCryptoAssessment() {
    const payload = {
        name: document.getElementById('crypto-name')?.value || 'company_update.exe',
        algorithm: selectedCrypto,
        key_size: selectedCrypto === 'ECDSA' ? 256 : 2048,
        certificate_status: 'valid',
        signature_status: 'valid',
        sensitive: true,
        data_lifetime_years: Number(document.getElementById('crypto-lifetime')?.value || 10),
        suspicious_activity: Number(document.getElementById('crypto-anomaly')?.value || 0),
        certificate_issuer_trusted: true,
        payload: document.getElementById('crypto-payload')?.value || ''
    };
    try {
        const response = await fetch('/api/crypto-assess', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
        const data = await response.json();
        const r = data.result || {};
        document.getElementById('crypto-risk-score').innerText = `${r.risk_score ?? '--'}/100`;
        document.getElementById('crypto-classical').innerText = r.classical_security || '--';
        document.getElementById('crypto-quantum').innerText = r.quantum_risk || '--';
        document.getElementById('crypto-target').innerText = r.recommendation?.target || '--';
        document.getElementById('crypto-risk-title').innerText = `${r.risk_level || 'UNKNOWN'} // ${r.normalized_algorithm || selectedCrypto}`;
        document.getElementById('crypto-risk-desc').innerText = (r.reasons || []).slice(0,3).join(' ');
        document.getElementById('crypto-risk-mitigation').innerText = r.recommendation?.action || 'Manual review required.';
        const box = document.getElementById('crypto-result-box');
        box.className = r.risk_level === 'LOW' ? 'threat-banner banner-safe' : 'threat-banner banner-danger';
    } catch (e) {
        document.getElementById('crypto-risk-desc').innerText = `Assessment failed: ${e.message}`;
    }
}
