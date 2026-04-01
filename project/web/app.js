document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const sampleSelect = document.getElementById('sampleSelect');
    const toggleDirectionBtn = document.getElementById('toggleDirectionBtn');
    const convertBtn = document.getElementById('convertBtn');
    const leftInput = document.getElementById('leftInput');
    const rightOutput = document.getElementById('rightOutput');
    const leftTitle = document.getElementById('leftTitle');
    const rightTitle = document.getElementById('rightTitle');
    const statsPanel = document.getElementById('statsPanel');
    const loadingState = document.getElementById('loadingState');

    // State
    let mode = 'encode'; // 'encode' = JSON->TOON, 'decode' = TOON->JSON
    let samplesData = {};

    // Initialization
    fetchSamples();

    // Event Listeners
    toggleDirectionBtn.addEventListener('click', toggleDirection);
    convertBtn.addEventListener('click', handleConversion);
    sampleSelect.addEventListener('change', loadSample);

    // Functions
    async function fetchSamples() {
        try {
            const res = await fetch('/api/samples');
            const data = await res.json();
            samplesData = data;
            
            Object.keys(data).forEach(filename => {
                const opt = document.createElement('option');
                opt.value = filename;
                opt.textContent = filename;
                sampleSelect.appendChild(opt);
            });
        } catch (e) {
            console.error("Failed to load samples", e);
        }
    }

    function loadSample() {
        const val = sampleSelect.value;
        if (val && samplesData[val]) {
            if (mode === 'encode') {
                leftInput.value = samplesData[val];
                rightOutput.value = "";
                statsPanel.classList.add('hidden');
            } else {
                // If in TOON mode, load JSON and convert it instantly
                toggleDirection();
                leftInput.value = samplesData[val];
                handleConversion();
            }
        }
    }

    function toggleDirection() {
        if (mode === 'encode') {
            mode = 'decode';
            leftTitle.textContent = 'Input (TOON)';
            rightTitle.textContent = 'Output (JSON)';
            // Swap texts if possible
            const temp = leftInput.value;
            leftInput.value = rightOutput.value;
            rightOutput.value = temp;
        } else {
            mode = 'encode';
            leftTitle.textContent = 'Input (JSON)';
            rightTitle.textContent = 'Output (TOON)';
            // Swap texts if possible
            const temp = leftInput.value;
            leftInput.value = rightOutput.value;
            rightOutput.value = temp;
        }
        statsPanel.classList.add('hidden');
    }

    async function handleConversion() {
        const inputVal = leftInput.value.trim();
        if (!inputVal) return;

        // Show loading
        document.querySelector('#rightPanel .panel-footer').classList.add('hidden');
        loadingState.classList.remove('hidden');
        rightOutput.value = "";
        statsPanel.classList.add('hidden');

        try {
            const endpoint = mode === 'encode' ? '/api/encode' : '/api/decode';
            const payload = mode === 'encode' ? { jsonText: inputVal } : { toonText: inputVal };

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (data.success) {
                rightOutput.value = data.resultText;
                if (mode === 'encode' && data.stats) {
                    renderStats(data.stats);
                }
            } else {
                rightOutput.value = `Error:\n${data.error}`;
            }
        } catch (e) {
            rightOutput.value = `Network/Server Error:\n${e.message}`;
        } finally {
            // Hide loading
            document.querySelector('#rightPanel .panel-footer').classList.remove('hidden');
            loadingState.classList.add('hidden');
        }
    }

    function renderStats(stats) {
        const prettyPct  = stats.tokenSavingsPct;
        const compactPct = stats.tokenSavingsPctVsCompact;

        const colorClass = (pct) => pct > 0 ? 'success' : (pct < 0 ? 'error' : '');
        const sign       = (pct) => pct > 0 ? '+' : '';

        statsPanel.innerHTML = `
            <div class="stat-box">
                <div class="stat-label">vs JSON Pretty</div>
                <div class="stat-value ${colorClass(prettyPct)}">
                    ${sign(prettyPct)}${prettyPct}%
                </div>
                <div class="stat-sub">${stats.inputTokens} → ${stats.outputTokens} tokens</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">vs JSON Compact</div>
                <div class="stat-value ${colorClass(compactPct)}">
                    ${sign(compactPct)}${compactPct}%
                </div>
                <div class="stat-sub">${stats.compactTokens} → ${stats.outputTokens} tokens</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Payload Size</div>
                <div class="stat-value ${colorClass(stats.byteSavingsPct)}">
                    ${sign(stats.byteSavingsPct)}${stats.byteSavingsPct}%
                </div>
                <div class="stat-sub">${stats.inputBytes}b → ${stats.outputBytes}b</div>
            </div>
            <div class="progress-bar-container">
                <div class="stat-label" style="display:flex; justify-content:space-between;">
                    <span>JSON Pretty (${stats.inputTokens})</span>
                    <span>Compact (${stats.compactTokens})</span>
                    <span>TOON (${stats.outputTokens})</span>
                </div>
                <div class="progress-bar-bg" style="position:relative; height:14px; border-radius:7px; background:#1e293b; margin-top:6px;">
                    <div style="position:absolute; left:0; top:0; height:100%; width:${(stats.compactTokens/stats.inputTokens*100).toFixed(1)}%; background:#64748b; border-radius:7px;" title="JSON Compact"></div>
                    <div style="position:absolute; left:0; top:0; height:100%; width:${(stats.outputTokens/stats.inputTokens*100).toFixed(1)}%; background:linear-gradient(90deg,#6366f1,#8b5cf6); border-radius:7px;" title="TOON"></div>
                </div>
                <div class="stat-label" style="margin-top:4px; font-size:0.7rem; color:#64748b;">■ Purple = TOON &nbsp; ■ Grey = JSON Compact &nbsp; (baseline = JSON Pretty)</div>
            </div>
        `;
        statsPanel.classList.remove('hidden');
    }
});
