// Global variables
let currentTaskId = null;
let statusCheckInterval = null;
let outputFilename = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
});

// Initialize file upload functionality
function initializeUpload() {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('videoFile');
    
    // Click to upload
    uploadBox.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Drag and drop
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.classList.add('dragover');
    });
    
    uploadBox.addEventListener('dragleave', () => {
        uploadBox.classList.remove('dragover');
    });
    
    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
}

// Handle file selection
function handleFileSelect(file) {
    // Validate file type
    const allowedExtensions = ['.mp4', '.mov', '.mkv', '.avi', '.m4v'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        showError('Invalid file type. Please upload MP4, MOV, MKV, AVI, or M4V files.');
        return;
    }
    
    // Validate file size (500 MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File too large. Maximum size is 500 MB.');
        return;
    }
    
    // Show selected file
    const selectedFileDiv = document.getElementById('selectedFile');
    selectedFileDiv.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
    selectedFileDiv.classList.add('show');
    
    // Upload file
    uploadVideo(file);
}

// Upload video to server
function uploadVideo(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Show processing section
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('processingSection').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    
    updateProgress(0, 'Uploading video...');
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentTaskId = data.task_id;
            startStatusCheck();
        } else {
            showError(data.error || 'Upload failed');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showError('Failed to upload video: ' + error.message);
    });
}

// Start checking processing status
function startStatusCheck() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(() => {
        checkStatus();
    }, 2000); // Check every 2 seconds
    
    // Check immediately
    checkStatus();
}

// Check processing status
function checkStatus() {
    if (!currentTaskId) return;
    
    fetch(`/status/${currentTaskId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'processing') {
                updateProgress(data.progress || 0, data.message || 'Processing...');
            } else if (data.status === 'completed') {
                clearInterval(statusCheckInterval);
                showResults(data);
            } else if (data.status === 'error') {
                clearInterval(statusCheckInterval);
                showError(data.message || 'Processing failed');
            }
        })
        .catch(error => {
            console.error('Status check error:', error);
            // Don't show error on network issues, just retry
        });
}

// Update progress bar
function updateProgress(percent, message) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressPercent = document.getElementById('progressPercent');
    
    progressFill.style.width = percent + '%';
    progressText.textContent = message;
    progressPercent.textContent = Math.round(percent) + '%';
}

// Show results
function showResults(data) {
    document.getElementById('processingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    document.getElementById('errorSection').style.display = 'none';
    
    outputFilename = data.output_filename;
    
    document.getElementById('profanityCount').textContent = data.profanities_detected || 0;
    document.getElementById('resultStatus').textContent = 'Success';
    
    // Show profanity list if any
    if (data.profanity_list && data.profanity_list.length > 0) {
        const profanityList = document.getElementById('profanityList');
        const profanityListItems = document.getElementById('profanityListItems');
        
        profanityList.style.display = 'block';
        profanityListItems.innerHTML = '';
        
        data.profanity_list.forEach(item => {
            const li = document.createElement('li');
            li.textContent = `"${item.word}" at ${item.start.toFixed(2)}s - ${item.end.toFixed(2)}s`;
            profanityListItems.appendChild(li);
        });
    } else {
        document.getElementById('profanityList').style.display = 'none';
    }
}

// Download video
function downloadVideo() {
    if (!outputFilename) {
        showError('No file available for download');
        return;
    }
    
    window.location.href = `/download/${outputFilename}`;
}

// Show error
function showError(message) {
    document.getElementById('uploadSection').style.display = 'none';
    document.getElementById('processingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'block';
    
    document.getElementById('errorMessage').textContent = message;
    
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
}

// Reset form
function resetForm() {
    currentTaskId = null;
    outputFilename = null;
    
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    document.getElementById('videoFile').value = '';
    document.getElementById('selectedFile').classList.remove('show');
    
    document.getElementById('uploadSection').style.display = 'block';
    document.getElementById('processingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    
    updateProgress(0, '');
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}


