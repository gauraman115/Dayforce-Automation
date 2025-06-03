document.addEventListener('DOMContentLoaded', function() {
    const inputCount = document.getElementById('inputCount');
    const generateFieldsBtn = document.getElementById('generateFieldsBtn');
    const inputFieldsContainer = document.getElementById('inputFieldsContainer');
    const generateBtn = document.getElementById('generateBtn');
    const outputElement = document.getElementById('output');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const fileInput = document.getElementById('excel_file');
    const fileNameElement = document.getElementById('fileName');
    const uploadArea = document.getElementById('uploadArea');

    // Generate input fields based on count
    generateFieldsBtn.addEventListener('click', function() {
        const count = parseInt(inputCount.value);
        if (count < 1) return;
        
        inputFieldsContainer.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const fieldGroup = document.createElement('div');
            fieldGroup.className = 'input-field-group';
            fieldGroup.innerHTML = `
                <div class="input-row">
                    <div class="input-col">
                        <label>Field Name ${i + 1}</label>
                        <input type="text" name="input_name_${i}" placeholder="e.g., ProductID" required>
                    </div>
                    <div class="input-col">
                        <label>Position (Row, Column)</label>
                        <input type="text" name="input_pos_${i}" placeholder="e.g., 1, A" required>
                    </div>
                </div>
            `;
            inputFieldsContainer.appendChild(fieldGroup);
        }
    });

    // File upload handling
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            fileNameElement.textContent = e.target.files[0].name;
        }
    });

    // Drag and drop for file upload
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#4361ee';
        this.style.backgroundColor = '#f0f4ff';
    });

    uploadArea.addEventListener('dragleave', function() {
        this.style.borderColor = '#ddd';
        this.style.backgroundColor = '#fafafa';
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#ddd';
        this.style.backgroundColor = '#fafafa';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            fileNameElement.textContent = e.dataTransfer.files[0].name;
        }
    });

    // Generate XSLT
    generateBtn.addEventListener('click', async function() {
        outputElement.textContent = 'Generating XSLT...';
        outputElement.style.color = '#f8f8f2';
        
        const form = document.getElementById('xsltForm');
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                outputElement.textContent = data.output;
                outputElement.style.color = '#f8f8f2';
            } else {
                outputElement.textContent = 'Error: ' + data.error;
                outputElement.style.color = '#ff6b6b';
            }
        } catch (error) {
            outputElement.textContent = 'Network error: ' + error.message;
            outputElement.style.color = '#ff6b6b';
        }
    });

    // Copy to clipboard
    copyBtn.addEventListener('click', function() {
        const textArea = document.createElement('textarea');
        textArea.value = outputElement.textContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Show feedback
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    });

    // Download XSLT
    downloadBtn.addEventListener('click', function() {
        const content = outputElement.textContent;
        if (!content || content === 'Generated XSLT will appear here...') {
            alert('No XSLT content to download');
            return;
        }
        
        const blob = new Blob([content], { type: 'application/xslt+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'generated.xslt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
});