// AnomRadar Frontend - Reports Management

let currentScanId = null;

async function loadReportsForScan() {
    const scanIdInput = document.getElementById('report-scan-id');
    const scanId = scanIdInput.value.trim();
    
    if (!scanId) {
        showError('Please enter a scan ID');
        return;
    }
    
    currentScanId = scanId;
    
    const reportsSection = document.getElementById('reports-section');
    const reportsList = document.getElementById('reports-list');
    
    reportsSection.style.display = 'block';
    reportsList.innerHTML = '<p class="loading">Loading reports...</p>';
    
    try {
        const response = await apiRequest(`/reports/${scanId}`);
        const reports = response.data.reports;
        
        if (reports.length === 0) {
            reportsList.innerHTML = '<p>No reports available for this scan. Generate a report using the buttons above.</p>';
            return;
        }
        
        reportsList.innerHTML = reports.map(report => {
            const date = formatDate(report.generated_at);
            const size = formatFileSize(report.file_size);
            
            return `
                <div class="report-item">
                    <div>
                        <span class="report-type">${report.report_type}</span>
                        <p>
                            <strong>Generated:</strong> ${date}<br>
                            <strong>Size:</strong> ${size}
                        </p>
                    </div>
                    <button class="btn btn-primary" onclick="downloadReport('${scanId}', ${report.id})">
                        Download
                    </button>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        reportsList.innerHTML = `<p style="color: red;">Failed to load reports: ${error.message}</p>`;
    }
}

async function generateReport(type) {
    if (!currentScanId) {
        showError('Please load a scan first');
        return;
    }
    
    const reportsList = document.getElementById('reports-list');
    reportsList.innerHTML = '<p class="loading">Generating report...</p>';
    
    try {
        const response = await apiRequest(`/reports/${currentScanId}/${type}`, {
            method: 'POST',
        });
        
        showSuccess(`${type.toUpperCase()} report generated successfully`);
        
        // Reload reports list
        setTimeout(() => loadReportsForScan(), 1000);
        
    } catch (error) {
        showError(`Failed to generate ${type} report: ` + error.message);
        reportsList.innerHTML = '<p>Failed to generate report. Please try again.</p>';
    }
}

function downloadReport(scanId, reportId) {
    const downloadUrl = `${API_BASE_URL}/reports/${scanId}/download/${reportId}`;
    window.open(downloadUrl, '_blank');
}

function formatFileSize(bytes) {
    if (!bytes) return 'Unknown';
    
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }
    
    return `${size.toFixed(2)} ${units[unitIndex]}`;
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', () => {
    const loadReportsBtn = document.getElementById('load-reports');
    const generateHtmlBtn = document.getElementById('generate-html-report');
    const generatePdfBtn = document.getElementById('generate-pdf-report');
    
    if (loadReportsBtn) {
        loadReportsBtn.addEventListener('click', loadReportsForScan);
    }
    
    if (generateHtmlBtn) {
        generateHtmlBtn.addEventListener('click', () => generateReport('html'));
    }
    
    if (generatePdfBtn) {
        generatePdfBtn.addEventListener('click', () => generateReport('pdf'));
    }
    
    // Allow Enter key to load reports
    const scanIdInput = document.getElementById('report-scan-id');
    if (scanIdInput) {
        scanIdInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') loadReportsForScan();
        });
    }
});
