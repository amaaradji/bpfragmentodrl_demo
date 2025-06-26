// JavaScript for BPFragmentODRL Demo Tool

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const downloadBtn = document.getElementById('downloadBtn');
    
    let currentResultsDir = null;

    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        
        // Show loading, hide other sections
        showLoading();
        hideResults();
        hideError();
        
        // Submit form data
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.success) {
                displayResults(data);
                showResults();
            } else {
                showError(data.error || 'An unknown error occurred');
            }
        })
        .catch(error => {
            hideLoading();
            showError('Network error: ' + error.message);
        });
    });

    // Handle download button
    downloadBtn.addEventListener('click', function() {
        if (currentResultsDir) {
            window.location.href = `/download/${currentResultsDir}`;
        }
    });

    function showLoading() {
        loadingSection.style.display = 'block';
        loadingSection.classList.add('fade-in');
    }

    function hideLoading() {
        loadingSection.style.display = 'none';
        loadingSection.classList.remove('fade-in');
    }

    function showResults() {
        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');
    }

    function hideResults() {
        resultsSection.style.display = 'none';
        resultsSection.classList.remove('fade-in');
    }

    function showError(message) {
        document.getElementById('errorMessage').textContent = message;
        errorSection.style.display = 'block';
        errorSection.classList.add('fade-in');
    }

    function hideError() {
        errorSection.style.display = 'none';
        errorSection.classList.remove('fade-in');
    }

    function displayResults(data) {
        currentResultsDir = data.results_dir;
        
        // Update process information
        document.getElementById('processFile').textContent = data.filename;
        document.getElementById('processName').textContent = data.bp_model.name;
        document.getElementById('processApproach').textContent = capitalizeFirst(data.approach);
        document.getElementById('processFragmentation').textContent = capitalizeFirst(data.fragmentation_strategy) + '-based';
        
        // Update model statistics
        document.getElementById('modelActivities').textContent = data.bp_model.activities;
        document.getElementById('modelGateways').textContent = data.bp_model.gateways;
        document.getElementById('modelEvents').textContent = data.bp_model.events;
        
        // Update metrics
        const metrics = data.metrics;
        document.getElementById('totalFragments').textContent = metrics.total_fragments || 0;
        document.getElementById('totalRules').textContent = metrics.total_rules || 0;
        document.getElementById('totalPermissions').textContent = metrics.permissions || 0;
        document.getElementById('totalProhibitions').textContent = metrics.prohibitions || 0;
        document.getElementById('totalObligations').textContent = metrics.obligations || 0;
        document.getElementById('totalConflicts').textContent = metrics.conflicts || 0;
        
        // Display fragments
        displayFragments(data.fragments);
        
        // Display policies
        displayPolicies(data.fragment_activity_policies);
    }

    function displayFragments(fragments) {
        const container = document.getElementById('fragmentsContainer');
        container.innerHTML = '';
        
        if (!fragments || fragments.length === 0) {
            container.innerHTML = '<p class="text-muted">No fragments generated.</p>';
            return;
        }
        
        fragments.forEach(fragment => {
            const fragmentCard = document.createElement('div');
            fragmentCard.className = 'fragment-card';
            
            const activities = fragment.activities || [];
            const activitiesHtml = activities.map(activity => 
                `<div class="activity-item">
                    <strong>${activity.id}</strong>: ${activity.name || 'Unnamed Activity'}
                    <span class="badge bg-secondary ms-2">${activity.type || 'task'}</span>
                </div>`
            ).join('');
            
            fragmentCard.innerHTML = `
                <div class="fragment-header">
                    <i class="fas fa-puzzle-piece me-2"></i>
                    Fragment ${fragment.id}
                </div>
                <div class="fragment-activities">
                    <h6>Activities (${activities.length}):</h6>
                    ${activitiesHtml || '<p class="text-muted">No activities in this fragment.</p>'}
                </div>
            `;
            
            container.appendChild(fragmentCard);
        });
    }

    function displayPolicies(fragmentPolicies) {
        const container = document.getElementById('policiesContainer');
        container.innerHTML = '';
        
        if (!fragmentPolicies || Object.keys(fragmentPolicies).length === 0) {
            container.innerHTML = '<p class="text-muted">No policies generated.</p>';
            return;
        }
        
        Object.entries(fragmentPolicies).forEach(([fragmentId, policies]) => {
            const policyCard = document.createElement('div');
            policyCard.className = 'policy-card';
            
            const policiesHtml = policies.map(policy => {
                const policyClass = `policy-${policy.rule_type}`;
                const iconClass = getPolicyIcon(policy.rule_type);
                
                return `
                    <div class="policy-item ${policyClass}">
                        <div class="policy-type">
                            <i class="${iconClass} me-1"></i>
                            ${policy.rule_type}
                        </div>
                        <div class="policy-details">
                            <strong>Target:</strong> ${policy.target_activity_id}<br>
                            <strong>Action:</strong> ${policy.action}<br>
                            <strong>Assignee:</strong> ${policy.assignee}<br>
                            ${policy.constraints && policy.constraints.length > 0 ? 
                                `<strong>Constraints:</strong> ${formatConstraints(policy.constraints)}` : ''}
                        </div>
                    </div>
                `;
            }).join('');
            
            policyCard.innerHTML = `
                <div class="policy-header">
                    <i class="fas fa-shield-alt me-2"></i>
                    Fragment ${fragmentId} Policies (${policies.length})
                </div>
                <div class="policies-list">
                    ${policiesHtml}
                </div>
            `;
            
            container.appendChild(policyCard);
        });
    }

    function getPolicyIcon(ruleType) {
        switch (ruleType) {
            case 'permission':
                return 'fas fa-check-circle';
            case 'prohibition':
                return 'fas fa-times-circle';
            case 'obligation':
                return 'fas fa-exclamation-circle';
            default:
                return 'fas fa-circle';
        }
    }

    function formatConstraints(constraints) {
        if (!constraints || constraints.length === 0) {
            return 'None';
        }
        
        return constraints.map(constraint => {
            return `${constraint.constraint_type}: ${constraint.operator} ${constraint.value}`;
        }).join(', ');
    }

    function capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // Load available approaches on page load
    fetch('/api/approaches')
        .then(response => response.json())
        .then(data => {
            // Update approach descriptions if needed
            const approachSelect = document.getElementById('approach');
            const fragmentationSelect = document.getElementById('fragmentation_strategy');
            
            // Add tooltips or help text based on the API response
            if (data.approaches) {
                data.approaches.forEach(approach => {
                    const option = approachSelect.querySelector(`option[value="${approach.value}"]`);
                    if (option) {
                        option.title = approach.description;
                    }
                });
            }
            
            if (data.fragmentation_strategies) {
                data.fragmentation_strategies.forEach(strategy => {
                    const option = fragmentationSelect.querySelector(`option[value="${strategy.value}"]`);
                    if (option) {
                        option.title = strategy.description;
                    }
                });
            }
        })
        .catch(error => {
            console.warn('Could not load approach descriptions:', error);
        });
});

