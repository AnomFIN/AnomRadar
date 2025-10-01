// AnomRadar Frontend - Search/Scan Management

document.addEventListener('DOMContentLoaded', () => {
    const startScanBtn = document.getElementById('start-scan');
    const companyNameInput = document.getElementById('company-name');
    const businessIdInput = document.getElementById('business-id');
    
    startScanBtn.addEventListener('click', startScan);
    
    // Allow Enter key to start scan
    companyNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') startScan();
    });
});

async function startScan() {
    const companyName = document.getElementById('company-name').value.trim();
    const businessId = document.getElementById('business-id').value.trim();
    
    if (!companyName) {
        showError('Please enter a company name');
        return;
    }
    
    const statusBox = document.getElementById('scan-status');
    const statusMessage = document.getElementById('status-message');
    
    // Show loading
    statusBox.style.display = 'block';
    statusMessage.textContent = 'Starting scan...';
    
    try {
        const payload = {
            company_name: companyName,
        };
        
        if (businessId) {
            payload.business_id = businessId;
        }
        
        const response = await apiRequest('/scans', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        
        const scanId = response.data.scan_id;
        statusMessage.innerHTML = `
            Scan initiated successfully!<br>
            <strong>Scan ID:</strong> ${scanId}<br>
            <br>
            <button class="btn btn-primary" onclick="viewScan('${scanId}')">View Scan</button>
        `;
        
        // Clear form
        document.getElementById('company-name').value = '';
        document.getElementById('business-id').value = '';
        
    } catch (error) {
        statusMessage.innerHTML = `
            <span style="color: red;">Failed to start scan: ${error.message}</span><br>
            <button class="btn btn-secondary" onclick="document.getElementById('scan-status').style.display='none'">Close</button>
        `;
    }
}

function viewScan(scanId) {
    // Switch to reconnaissance page and highlight the scan
    const reconLink = document.querySelector('[data-page="recon"]');
    reconLink.click();
    
    // After a short delay, load the specific scan
    setTimeout(() => {
        loadScanDetails(scanId);
    }, 500);
}

async function loadScanDetails(scanId) {
    try {
        const response = await apiRequest(`/scans/${scanId}`);
        const scan = response.data;
        
        // Display scan details (could open a modal or expand inline)
        alert(`Scan Details:\n\nCompany: ${scan.company_name}\nRisk Score: ${scan.risk_score}\nRisk Level: ${scan.risk_level}\nStatus: ${scan.status}\nFindings: ${scan.findings.length}`);
        
    } catch (error) {
        showError('Failed to load scan details: ' + error.message);
    }
}

// Reconnaissance Page Functions
async function loadScans() {
    const scansList = document.getElementById('scans-list');
    const filterStatus = document.getElementById('filter-status').value;
    
    scansList.innerHTML = '<p class="loading">Loading scans...</p>';
    
    try {
        let endpoint = '/scans?limit=50';
        if (filterStatus) {
            endpoint += `&status=${filterStatus}`;
        }
        
        const response = await apiRequest(endpoint);
        const scans = response.data.scans;
        
        if (scans.length === 0) {
            scansList.innerHTML = '<p>No scans found.</p>';
            return;
        }
        
        scansList.innerHTML = scans.map(scan => `
            <div class="scan-item" onclick="viewScan('${scan.scan_id}')">
                <h3>
                    ${scan.company_name}
                    ${formatRiskLevel(scan.risk_level)}
                </h3>
                <p class="scan-meta">
                    <strong>Scan ID:</strong> ${scan.scan_id}<br>
                    <strong>Status:</strong> ${formatStatus(scan.status)}<br>
                    <strong>Risk Score:</strong> ${scan.risk_score}/100<br>
                    <strong>Created:</strong> ${formatDate(scan.created_at)}
                </p>
            </div>
        `).join('');
        
    } catch (error) {
        scansList.innerHTML = `<p style="color: red;">Failed to load scans: ${error.message}</p>`;
    }
}

// Set up event listeners for reconnaissance page
document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.getElementById('refresh-scans');
    const filterStatus = document.getElementById('filter-status');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadScans);
    }
    
    if (filterStatus) {
        filterStatus.addEventListener('change', loadScans);
    }
});
