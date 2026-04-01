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
        statsPanel.innerHTML = `
            <div class="stat-box">
                <div class="stat-label">LLM Token Savings</div>
                <div class="stat-value ${stats.tokenSavingsPct > 0 ? 'success' : 'error'}">
                    ${stats.tokenSavingsPct > 0 ? '+' : ''}${stats.tokenSavingsPct}%
                </div>
                <div class="stat-sub">${stats.tokenSavings} tokens saved</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Payload Weight</div>
                <div class="stat-value ${stats.byteSavingsPct > 0 ? 'success' : 'error'}">
                    ${stats.byteSavingsPct > 0 ? '+' : ''}${stats.byteSavingsPct}%
                </div>
                <div class="stat-sub">${stats.inputBytes}b ➔ ${stats.outputBytes}b</div>
            </div>
            <div class="progress-bar-container">
                <div class="stat-label" style="display:flex; justify-content:space-between;">
                    <span>JSON (${stats.inputTokens} toks)</span>
                    <span>TOON (${stats.outputTokens} toks)</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${100 - stats.tokenSavingsPct}%"></div>
                </div>
            </div>
        `;
        statsPanel.classList.remove('hidden');
    }
});
