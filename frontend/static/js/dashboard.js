// Dashboard functionality

let currentUser = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    const authStatus = await checkAuthStatus();
    if (!authStatus) {
        window.location.href = '/login';
        return;
    }
    
    currentUser = authStatus;
    document.getElementById('userDisplay').textContent = `Welcome, ${authStatus.username}!`;
    
    // Setup tab switching
    setupTabSwitching();
    
    // Setup file upload
    setupFileUpload();
    
    // Setup other features
    setupRefreshButton();
    setupPasswordChange();
    
    // Load initial data
    loadDetectionHistory();
    loadStatistics();
});

// Tab switching
function setupTabSwitching() {
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');
            
            // Remove active class from all items and tabs
            menuItems.forEach(m => m.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Add active class to clicked item and corresponding tab
            item.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            // Reload data if needed
            if (tabName === 'results') {
                loadDetectionHistory();
            } else if (tabName === 'stats') {
                loadStatistics();
            }
        });
    });
}

// File upload handling
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary-color)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border-color)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border-color)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
    
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    // Validate file
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please upload a valid image file (JPEG, PNG, GIF, or BMP)');
        return;
    }
    
    // Check file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File size exceeds 16MB limit');
        return;
    }
    
    // Show loading status
    const uploadStatus = document.getElementById('uploadStatus');
    uploadStatus.className = 'upload-status loading';
    uploadStatus.textContent = 'Processing image... Please wait.';
    
    // Hide previous results
    document.getElementById('detectionResult').style.display = 'none';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);
        
        const response = await fetch('/api/detection/upload', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        console.log('Response status:', response.status);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (response.ok) {
            uploadStatus.className = 'upload-status success';
            uploadStatus.textContent = 'Image processed successfully!';
            
            // Display results
            displayDetectionResult(data, file);
            
            // Clear file input
            document.getElementById('fileInput').value = '';
            
            // Refresh history
            loadDetectionHistory();
            
            setTimeout(() => {
                uploadStatus.textContent = '';
                uploadStatus.className = 'upload-status';
            }, 3000);
        } else {
            console.error('Upload error:', data);
            showError(data.error || data.message || 'Detection failed');
        }
    } catch (error) {
        console.error('Upload exception:', error);
        showError('Upload failed: ' + error.message);
    }
}

function displayDetectionResult(result, file) {
    const resultDiv = document.getElementById('detectionResult');
    const reader = new FileReader();
    
    reader.onload = (e) => {
        document.getElementById('resultImage').src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    const isPredictionReal = result.prediction === 'REAL';
    const titleColor = isPredictionReal ? '#10b981' : '#ef4444';
    const title = isPredictionReal ? '✓ Real Image' : '⚠ Deepfake Detected';
    
    document.getElementById('resultTitle').textContent = title;
    document.getElementById('resultTitle').style.color = titleColor;
    document.getElementById('predictionText').textContent = result.prediction;
    document.getElementById('confidenceText').textContent = (result.confidence * 100).toFixed(2) + '%';
    document.getElementById('processingTimeText').textContent = result.processing_time;
    
    resultDiv.style.display = 'grid';
}

function showError(message) {
    const uploadStatus = document.getElementById('uploadStatus');
    uploadStatus.className = 'upload-status error';
    uploadStatus.textContent = message;
}

// Load detection history
async function loadDetectionHistory() {
    try {
        const response = await fetch('/api/detection/history?page=1&limit=20');
        const data = await response.json();
        
        const historyContainer = document.getElementById('historyContainer');
        const emptyState = document.getElementById('historyEmpty');
        
        if (data.detections && data.detections.length > 0) {
            historyContainer.innerHTML = '';
            emptyState.style.display = 'none';
            
            data.detections.forEach(detection => {
                const item = createHistoryItem(detection);
                historyContainer.appendChild(item);
            });
        } else {
            historyContainer.innerHTML = '';
            emptyState.style.display = 'block';
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function createHistoryItem(detection) {
    const div = document.createElement('div');
    const className = detection.prediction === 'REAL' ? 'real' : 'deepfake';
    const icon = detection.prediction === 'REAL' ? '✓' : '⚠';
    
    div.className = `history-item ${className}`;
    div.innerHTML = `
        <div class="history-header">
            <div class="history-filename">${icon} ${detection.filename}</div>
            <button class="history-delete" onclick="deleteDetection('${detection.id}')">🗑</button>
        </div>
        <div class="history-details">
            <p><strong>Result:</strong> ${detection.prediction}</p>
            <p><strong>Confidence:</strong> ${(detection.confidence * 100).toFixed(2)}%</p>
            <p><strong>Date:</strong> ${new Date(detection.created_at).toLocaleDateString()}</p>
        </div>
    `;
    
    return div;
}

async function deleteDetection(detectionId) {
    if (!confirm('Are you sure you want to delete this detection record?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/detection/delete/${detectionId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadDetectionHistory();
            alert('Detection deleted successfully');
        } else {
            alert('Failed to delete detection');
        }
    } catch (error) {
        console.error('Delete failed:', error);
    }
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/detection/stats');
        const data = await response.json();
        
        document.getElementById('totalDetections').textContent = data.total_detections;
        document.getElementById('realCount').textContent = data.real_images;
        document.getElementById('deepfakeCount').textContent = data.deepfake_images;
        document.getElementById('avgConfidence').textContent = 
            (data.average_confidence * 100).toFixed(2) + '%';
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

// Refresh button
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDetectionHistory);
    }
}

// Change password
function setupPasswordChange() {
    const form = document.getElementById('changePasswordForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const oldPassword = document.getElementById('oldPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmNewPassword = document.getElementById('confirmNewPassword').value;
        
        if (newPassword !== confirmNewPassword) {
            showPasswordMessage('error', 'New passwords do not match');
            return;
        }
        
        try {
            const response = await fetch('/api/auth/change-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    old_password: oldPassword,
                    new_password: newPassword,
                    confirm_password: confirmNewPassword
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showPasswordMessage('success', data.message);
                form.reset();
            } else {
                showPasswordMessage('error', data.error);
            }
        } catch (error) {
            showPasswordMessage('error', 'Failed to change password');
        }
    });
}

function showPasswordMessage(type, message) {
    const messageDiv = document.getElementById('settingsMessage');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.textContent = '';
            messageDiv.className = 'message';
        }, 3000);
    }
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', logoutUser);
