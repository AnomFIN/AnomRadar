// AnomRadar Frontend - Whitelist Management

async function loadWhitelist() {
    const whitelistList = document.getElementById('whitelist-list');
    whitelistList.innerHTML = '<p class="loading">Loading whitelist...</p>';
    
    try {
        const response = await apiRequest('/whitelist');
        const items = response.data.whitelist;
        
        if (items.length === 0) {
            whitelistList.innerHTML = '<p>No items in whitelist.</p>';
            return;
        }
        
        whitelistList.innerHTML = items.map(item => `
            <div class="whitelist-item">
                <div>
                    <span class="whitelist-type">${item.entity_type}</span>
                    <strong>${item.entity_value}</strong>
                    ${item.description ? `<br><small style="color: #6c757d;">${item.description}</small>` : ''}
                </div>
                <button class="btn btn-danger" onclick="removeFromWhitelist(${item.id})">Remove</button>
            </div>
        `).join('');
        
    } catch (error) {
        whitelistList.innerHTML = `<p style="color: red;">Failed to load whitelist: ${error.message}</p>`;
    }
}

async function addToWhitelist() {
    const type = document.getElementById('whitelist-type').value;
    const value = document.getElementById('whitelist-value').value.trim();
    const description = document.getElementById('whitelist-description').value.trim();
    
    if (!value) {
        showError('Please enter a value');
        return;
    }
    
    try {
        const payload = {
            entity_type: type,
            entity_value: value,
        };
        
        if (description) {
            payload.description = description;
        }
        
        await apiRequest('/whitelist', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        
        showSuccess('Added to whitelist');
        
        // Clear form
        document.getElementById('whitelist-value').value = '';
        document.getElementById('whitelist-description').value = '';
        
        // Reload whitelist
        loadWhitelist();
        
    } catch (error) {
        showError('Failed to add to whitelist: ' + error.message);
    }
}

async function removeFromWhitelist(id) {
    if (!confirm('Are you sure you want to remove this item from the whitelist?')) {
        return;
    }
    
    try {
        await apiRequest(`/whitelist/${id}`, {
            method: 'DELETE',
        });
        
        showSuccess('Removed from whitelist');
        loadWhitelist();
        
    } catch (error) {
        showError('Failed to remove from whitelist: ' + error.message);
    }
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('add-whitelist');
    
    if (addBtn) {
        addBtn.addEventListener('click', addToWhitelist);
    }
    
    // Allow Enter key to add
    const valueInput = document.getElementById('whitelist-value');
    if (valueInput) {
        valueInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addToWhitelist();
        });
    }
});
