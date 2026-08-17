/* ScamShield Scanner Engine Frontend JS */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Text Area Character Counters & Clear Buttons
    const textInputs = document.querySelectorAll('.scam-textarea');
    textInputs.forEach(input => {
        const counterId = input.getAttribute('data-counter');
        const counterEl = document.getElementById(counterId);
        
        input.addEventListener('input', () => {
            if (counterEl) {
                counterEl.textContent = `${input.value.length} chars`;
            }
        });
    });

    // 2. Demo Example Loader
    const demoButtons = document.querySelectorAll('.btn-load-demo');
    demoButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const demoId = btn.getAttribute('data-demo-id');
            loadDemoData(demoId);
        });
    });

    // 3. Screenshot Drag and Drop / OCR Handler
    const dropzone = document.getElementById('screenshotDropzone');
    const imageInput = document.getElementById('screenshotFileInput');
    
    if (dropzone && imageInput) {
        dropzone.addEventListener('click', () => imageInput.click());
        
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                imageInput.files = e.dataTransfer.files;
                handleScreenshotSelected(e.dataTransfer.files[0]);
            }
        });

        imageInput.addEventListener('change', () => {
            if (imageInput.files.length > 0) {
                handleScreenshotSelected(imageInput.files[0]);
            }
        });
    }
});

// Load Demo Examples
function loadDemoData(demoId) {
    fetch('/api/demo-examples')
        .then(res => res.json())
        .then(data => {
            const example = data.examples.find(item => item.id === demoId);
            if (!example) return;

            if (example.type === 'message') {
                const input = document.getElementById('messageText');
                if (input) {
                    input.value = example.content;
                    input.dispatchEvent(new Event('input'));
                    showToast(`Loaded "${example.title}"`, 'info');
                }
            } else if (example.type === 'url') {
                const input = document.getElementById('urlInput');
                if (input) {
                    input.value = example.content;
                    showToast(`Loaded "${example.title}"`, 'info');
                }
            } else if (example.type === 'call') {
                const input = document.getElementById('callTranscript');
                if (input) {
                    input.value = example.content;
                    input.dispatchEvent(new Event('input'));
                    showToast(`Loaded "${example.title}"`, 'info');
                }
            }
        })
        .catch(err => console.error(err));
}

// Screenshot Selection & OCR Processing Handler
function handleScreenshotSelected(file) {
    const previewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const ocrStatus = document.getElementById('ocrStatus');
    const ocrTextBox = document.getElementById('ocrExtractedText');
    const analyzeBtn = document.getElementById('btnAnalyzeScreenshot');

    if (!file.type.startsWith('image/')) {
        showToast('Please select a valid image file (PNG, JPG, WEBP)', 'error');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        showToast('File size exceeds 16MB limit', 'error');
        return;
    }

    // Show image preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);

    // Show OCR processing state
    ocrStatus.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Extracting text via OCR...';
    ocrStatus.style.display = 'block';
    if (ocrTextBox) ocrTextBox.value = '';

    const formData = new FormData();
    formData.append('image', file);

    fetch('/api/extract-ocr', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            ocrStatus.innerHTML = '<i class="fas fa-check-circle text-success"></i> Text Extracted! You can edit the text below before analysis:';
            if (ocrTextBox) {
                ocrTextBox.value = data.extracted_text;
                ocrTextBox.dispatchEvent(new Event('input'));
            }
            if (analyzeBtn) analyzeBtn.disabled = false;
            showToast('OCR Text Extracted successfully', 'success');
        } else {
            ocrStatus.innerHTML = `<i class="fas fa-exclamation-circle text-danger"></i> ${data.error || 'Failed to extract text'}`;
            showToast('OCR extraction failed', 'error');
        }
    })
    .catch(err => {
        ocrStatus.innerHTML = '<i class="fas fa-exclamation-circle text-danger"></i> Server error during OCR extraction';
        showToast('Server error during OCR', 'error');
    });
}

// SVG Risk Gauge Renderer
function renderRiskGauge(score, riskLevel) {
    const fillArc = document.getElementById('gaugeFillArc');
    const scoreText = document.getElementById('gaugeScoreText');
    if (!fillArc || !scoreText) return;

    // Arc length calculation for semi-circle gauge (r=45, dasharray ~ 141)
    const maxDash = 141;
    const offset = maxDash - (maxDash * (score / 100));
    
    fillArc.style.strokeDasharray = maxDash;
    fillArc.style.strokeDashoffset = offset;

    // Set stroke color based on level
    let strokeColor = '#10b981'; // SAFE
    if (riskLevel === 'NEEDS VERIFICATION') strokeColor = '#f59e0b';
    if (riskLevel === 'SUSPICIOUS') strokeColor = '#f97316';
    if (riskLevel === 'HIGH RISK') strokeColor = '#ef4444';

    fillArc.style.stroke = strokeColor;
    scoreText.textContent = `${score}/100`;
}
