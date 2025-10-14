// AnomRadar Frontend - Main Application

// API Base URL configuration
// Automatically detects environment and uses appropriate API endpoint
const API_BASE_URL = (() => {
    const hostname = window.location.hostname;
    
    // Development mode (localhost)
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:8080/api';
    }
    
    // Production on anomfin.fi
    if (hostname.includes('anomfin.fi')) {
        return '/api/radar';
    }
    
    // Default: relative path
    return '/api';
})();

// Navigation
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    loadInitialData();
});

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Show corresponding page
            const pageName = link.dataset.page;
            showPage(pageName);
        });
    });
}

function showPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // Load page-specific data
        switch(pageName) {
            case 'recon':
                loadScans();
                break;
            case 'whitelist':
                loadWhitelist();
                break;
        }
    }
}

function loadInitialData() {
    // Can add any initial data loading here
}

// API Helpers
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Utility Functions
function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert('Success: ' + message);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatRiskLevel(level) {
    return `<span class="risk-badge risk-${level}">${level.toUpperCase()}</span>`;
}

function formatStatus(status) {
    return `<span class="status-${status}">${status.toUpperCase()}</span>`;
}
