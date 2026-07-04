document.addEventListener('DOMContentLoaded', () => {
    // --- State & DOM Elements ---
    const loadingState = document.getElementById('loading-state');
    const outputCard = document.getElementById('output-card');
    
    const generatedCopyEl = document.getElementById('generated-copy');
    const generatedImageEl = document.getElementById('generated-image');
    const downloadImageLink = document.getElementById('download-image');
    const outputToolBadge = document.getElementById('output-tool');
    const outputToneBadge = document.getElementById('output-tone');
    const copyBtn = document.getElementById('copyBtn');

    // Parse URL Parameters
    const urlParams = new URLSearchParams(window.location.search);
    const productInfo = urlParams.get('product') || '';
    const targetTool = urlParams.get('tool') || 'LinkedIn';
    const tone = urlParams.get('tone') || 'Professional';

    // Set badges
    outputToolBadge.textContent = targetTool;
    outputToneBadge.textContent = tone;

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

    // --- Generate Function ---
    async function generateCampaign() {
        if (!productInfo) {
            alert('Missing product information. Returning to home.');
            window.location.href = '/';
            return;
        }

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_info: productInfo,
                    target_tool: targetTool,
                    tone: tone
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate content');
            }

            const data = await response.json();

            // Render Output
            generatedCopyEl.textContent = data.copy;
            generatedImageEl.src = data.image_url;
            downloadImageLink.href = data.image_url;

            // Transition UI
            loadingState.style.opacity = '0';
            loadingState.style.pointerEvents = 'none';
            setTimeout(() => {
                loadingState.style.display = 'none';
                
                outputCard.classList.remove('hidden');
                // Trigger reflow
                void outputCard.offsetWidth;
                
                outputCard.classList.remove('opacity-0', 'translate-y-10');
                outputCard.classList.add('opacity-100', 'translate-y-0');
            }, 1000);

        } catch (error) {
            console.error(error);
            alert('An error occurred while generating the campaign. Please return to home and try again.');
            window.location.href = '/';
        }
    }

    // --- Event Listeners ---
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(generatedCopyEl.textContent)
            .then(() => {
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '✓ Copied!';
                setTimeout(() => copyBtn.innerHTML = originalText, 2000);
            })
            .catch(err => console.error('Failed to copy text: ', err));
    });

    // Start generation on load
    generateCampaign();
});
