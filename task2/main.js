document.addEventListener('DOMContentLoaded', () => {
    // --- Data ---
    const tools = ['Instagram', 'LinkedIn', 'Email'];
    const tones = ['Professional', 'Witty', 'Urgent', 'Empathetic'];

    // --- State ---
    let selectedTool = tools[0];
    let selectedTone = tones[0];
    let isGenerating = false;

    // --- DOM Elements ---
    const toolContainer = document.getElementById('tool-container');
    const toneContainer = document.getElementById('tone-container');
    const productInfoInput = document.getElementById('productInfo');
    const generateBtn = document.getElementById('generateBtn');
    const btnText = document.getElementById('btn-text');


    // --- Background Elements (Antigravity Feel) ---
    const bgContainer = document.getElementById('bg-elements-container');
    for (let i = 0; i < 6; i++) {
        const el = document.createElement('div');
        el.className = 'bg-element';
        
        const isBlue = i % 2 === 0;
        el.style.backgroundColor = isBlue ? 'var(--color-glow-blue)' : 'var(--color-glow-purple)';
        
        const size = Math.random() * 400 + 200;
        el.style.width = `${size}px`;
        el.style.height = `${size}px`;
        
        el.style.top = `${Math.random() * 100}%`;
        el.style.left = `${Math.random() * 100}%`;
        
        const animDuration = Math.random() * 5 + 5;
        el.style.animation = `float ${animDuration}s ease-in-out infinite alternate`;
        
        bgContainer.appendChild(el);
    }

    // --- Render Buttons ---
    function renderTools() {
        toolContainer.innerHTML = '';
        tools.forEach(tool => {
            const btn = document.createElement('button');
            btn.className = `option-btn ${selectedTool === tool ? 'active-tool' : ''}`;
            btn.textContent = tool;
            btn.addEventListener('click', () => {
                selectedTool = tool;
                renderTools();
            });
            toolContainer.appendChild(btn);
        });
    }

    function renderTones() {
        toneContainer.innerHTML = '';
        tones.forEach(tone => {
            const btn = document.createElement('button');
            btn.className = `option-btn tone-btn ${selectedTone === tone ? 'active-tone' : ''}`;
            btn.textContent = tone;
            btn.addEventListener('click', () => {
                selectedTone = tone;
                renderTones();
            });
            toneContainer.appendChild(btn);
        });
    }

    // --- Input Validation ---
    productInfoInput.addEventListener('input', () => {
        if (productInfoInput.value.trim().length > 0 && !isGenerating) {
            generateBtn.removeAttribute('disabled');
        } else {
            generateBtn.setAttribute('disabled', 'true');
        }
    });

    // --- Generate Function ---
    function handleGenerate() {
        const productInfo = productInfoInput.value.trim();
        if (!productInfo) return;

        // Redirect to the new output page with URL parameters
        const urlParams = new URLSearchParams({
            product: productInfo,
            tool: selectedTool,
            tone: selectedTone
        });
        
        window.location.href = `/output?${urlParams.toString()}`;
    }

    // --- Event Listeners ---
    generateBtn.addEventListener('click', handleGenerate);

    // --- Initialization ---
    renderTools();
    renderTones();
});
