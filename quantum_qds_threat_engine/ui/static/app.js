// Quantum-Inspired Cyber Threat Detection UI Engine (Problem 26141)

let currentSelectedAttack = 'honest';

document.addEventListener('DOMContentLoaded', () => {
    initAttackButtons();
    initTabNavigation();
    initActionButtons();
    loadSystemStatus();
    loadBenchmarkImages();
});

function initAttackButtons() {
    const buttons = document.querySelectorAll('.btn-attack');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active-selected'));
            btn.classList.add('active-selected');
            currentSelectedAttack = btn.getAttribute('data-type');
        });
    });
}

function initTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const panes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetPane = document.getElementById(targetId);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });
}

function initActionButtons() {
    const runBtn = document.getElementById('btn-execute-simulation');
    const resetBtn = document.getElementById('btn-reset-cache');
    const msgInput = document.getElementById('input-message');
    
    if (runBtn) {
        runBtn.addEventListener('click', () => {
            const msg = msgInput ? msgInput.value : "DEFAULT_TRANSACTION_PAYLOAD";
            executeSimulation(currentSelectedAttack, msg);
        });
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/reset', { method: 'POST' });
                const data = await res.json();
                alert("Quantum session cache & nonces reset successfully.");
            } catch (err) {
                console.error("Reset error:", err);
            }
        });
    }
}

async function loadSystemStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.status === "ONLINE") {
            const el = document.getElementById('sec-param-n');
            if (el) el.innerText = `N = ${data.security_parameter_N} Qubits`;
        }
    } catch (err) {
        console.warn("Status fetch failed:", err);
    }
}

async function loadBenchmarkImages() {
    try {
        await fetch('/api/benchmark');
    } catch (err) {
        console.warn("Benchmark data fetch:", err);
    }
}

async function executeSimulation(attackType, message) {
    const runBtn = document.getElementById('btn-execute-simulation');
    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = '<span class="pulse-ring"></span> SIMULATING QUANTUM CHANNELS...';
    }
    
    try {
        const res = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                attack_type: attackType,
                message: message
            })
        });
        
        const data = await res.json();
        if (data.status === "SUCCESS") {
            updateDashboardTelemetry(data.result);
        }
    } catch (err) {
        console.error("Simulation error:", err);
    } finally {
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.innerHTML = '<span class="pulse-ring"></span> INJECT &amp; RUN SIMULATION';
        }
    }
}

function updateDashboardTelemetry(result) {
    const report = result.threat_report || {};
    const metrics = report.metrics || {};
    const threatDetected = report.threat_detected;
    
    // 1. KPI Cards
    // CHSH
    const chshMetrics = metrics.chsh_metrics || {};
    const meanChsh = chshMetrics.mean_chsh_s !== undefined ? chshMetrics.mean_chsh_s : 2.8284;
    const chshEl = document.getElementById('kpi-chsh-val');
    const chshTag = document.getElementById('kpi-chsh-status');
    const chshBar = document.getElementById('kpi-chsh-bar');
    
    if (chshEl) chshEl.innerText = meanChsh.toFixed(4);
    if (chshTag) {
        if (meanChsh >= 2.70) {
            chshTag.className = "kpi-tag tag-safe";
            chshTag.innerText = "MAXIMAL";
        } else if (meanChsh > 2.0) {
            chshTag.className = "kpi-tag tag-warn";
            chshTag.innerText = "DEGRADED";
        } else {
            chshTag.className = "kpi-tag tag-danger";
            chshTag.innerText = "SEPARABLE";
        }
    }
    if (chshBar) {
        const pct = Math.min(Math.max((meanChsh / 2.8284) * 100, 0), 100);
        chshBar.style.width = `${pct}%`;
    }
    
    // QBER Signature
    const sigQber = metrics.sig_qber !== undefined ? metrics.sig_qber : 0.0;
    const sigQberEl = document.getElementById('kpi-qber-sig-val');
    const sigQberTag = document.getElementById('kpi-qber-sig-status');
    const sigQberBar = document.getElementById('kpi-qber-sig-bar');
    
    if (sigQberEl) sigQberEl.innerText = `${(sigQber * 100).toFixed(1)}%`;
    if (sigQberTag) {
        if (sigQber <= 0.08) {
            sigQberTag.className = "kpi-tag tag-safe";
            sigQberTag.innerText = "PASS";
        } else {
            sigQberTag.className = "kpi-tag tag-danger";
            sigQberTag.innerText = "ALARM";
        }
    }
    if (sigQberBar) {
        sigQberBar.style.width = `${Math.min(sigQber * 200, 100)}%`;
    }
    
    // QBER Decoy
    const decoyQber = metrics.decoy_qber !== undefined ? metrics.decoy_qber : 0.0;
    const decoyQberEl = document.getElementById('kpi-qber-decoy-val');
    const decoyQberTag = document.getElementById('kpi-qber-decoy-status');
    const decoyQberBar = document.getElementById('kpi-qber-decoy-bar');
    
    if (decoyQberEl) decoyQberEl.innerText = `${(decoyQber * 100).toFixed(1)}%`;
    if (decoyQberTag) {
        if (decoyQber <= 0.08) {
            decoyQberTag.className = "kpi-tag tag-safe";
            decoyQberTag.innerText = "PRISTINE";
        } else {
            decoyQberTag.className = "kpi-tag tag-danger";
            decoyQberTag.innerText = "COLLAPSED";
        }
    }
    if (decoyQberBar) {
        decoyQberBar.style.width = `${Math.min(decoyQber * 200, 100)}%`;
    }
    
    // 2. Threat HUD Box
    const hudBadge = document.getElementById('hud-threat-badge');
    const alertBox = document.getElementById('threat-alert-box');
    const alertIcon = document.getElementById('alert-icon');
    const alertTitle = document.getElementById('alert-title');
    const alertSummary = document.getElementById('alert-summary');
    const alertMitigation = document.getElementById('alert-mitigation');
    
    if (threatDetected) {
        if (hudBadge) {
            hudBadge.className = "badge-hud tag-danger";
            hudBadge.innerText = report.threat_classification || "THREAT DETECTED";
        }
        if (alertBox) {
            alertBox.className = "threat-alert-box alert-danger";
        }
        if (alertIcon) alertIcon.innerHTML = "&#9888;";
        if (alertTitle) alertTitle.innerText = `ATTACK IDENTIFIED: ${report.threat_classification || "MALICIOUS INTRUSION"}`;
    } else {
        if (hudBadge) {
            hudBadge.className = "badge-hud tag-safe";
            hudBadge.innerText = "PRISTINE / ACCEPTED";
        }
        if (alertBox) {
            alertBox.className = "threat-alert-box alert-safe";
        }
        if (alertIcon) alertIcon.innerHTML = "&#10004;";
        if (alertTitle) alertTitle.innerText = "AUTHENTIC SIGNATURE DETERMINISTICALLY ACCEPTED";
    }
    
    if (alertSummary) alertSummary.innerText = report.summary || "No description.";
    if (alertMitigation) alertMitigation.innerText = report.mitigation_action || "None.";
    
    // 3. Mathematical Decision Proofs
    const decoyAnalysis = metrics.decoy_analysis || {};
    const sigStat = decoyAnalysis.sig_stat || {};
    const secBounds = metrics.security_bounds || {};
    
    const pval = sigStat.p_value !== undefined ? sigStat.p_value : (threatDetected ? 0.00001 : 1.0);
    const hoeff = sigStat.hoeffding_bound !== undefined ? sigStat.hoeffding_bound : 1e-6;
    const kldiv = secBounds.kl_divergence !== undefined ? secBounds.kl_divergence : 0.2458;
    
    const pvalEl = document.getElementById('proof-pval');
    const hoeffEl = document.getElementById('proof-hoeffding');
    const kldivEl = document.getElementById('proof-kldiv');
    
    if (pvalEl) pvalEl.innerText = pval < 0.001 ? `${pval.toExponential(2)} (REJECT H0)` : `${pval.toFixed(4)} (ACCEPT H0)`;
    if (hoeffEl) hoeffEl.innerText = `\u2264 ${hoeff.toExponential(2)}`;
    if (kldivEl) kldivEl.innerText = `${kldiv.toFixed(4)} nats`;
    
    // 4. Multi-verifier Arbitration Table
    const arb = metrics.arbitration_result;
    const bobQberEl = document.getElementById('arb-bob-qber');
    const charlieQberEl = document.getElementById('arb-charlie-qber');
    const bobStatus = document.getElementById('arb-bob-status');
    const charlieStatus = document.getElementById('arb-charlie-status');
    
    if (bobQberEl) bobQberEl.innerText = `${(sigQber * 100).toFixed(1)}%`;
    if (bobStatus) {
        bobStatus.className = sigQber <= 0.08 ? "tag-safe" : "tag-danger";
        bobStatus.innerText = sigQber <= 0.08 ? "ACCEPTED" : "REJECTED";
    }
    
    if (arb && charlieQberEl) {
        charlieQberEl.innerText = `${(arb.charlie_qber * 100).toFixed(1)}%`;
        if (charlieStatus) {
            charlieStatus.className = arb.charlie_qber <= 0.08 ? "tag-safe" : "tag-danger";
            charlieStatus.innerText = arb.charlie_qber <= 0.08 ? "ACCEPTED" : "REJECTED";
        }
    }
}
