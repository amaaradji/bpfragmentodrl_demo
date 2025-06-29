// JavaScript for BPFragmentODRL Demo Tool

document.addEventListener('DOMContentLoaded', function() {
    // Handle BP policy source radio buttons
    const bpPolicyRadios = document.querySelectorAll('input[name="bp_policy_source"]');
    const bpTemplateSection = document.getElementById('bp_template_section');
    const bpUploadSection = document.getElementById('bp_upload_section');
    
    bpPolicyRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'generate') {
                bpTemplateSection.style.display = 'block';
                bpUploadSection.style.display = 'none';
            } else if (this.value === 'upload') {
                bpTemplateSection.style.display = 'none';
                bpUploadSection.style.display = 'block';
            } else {
                bpTemplateSection.style.display = 'none';
                bpUploadSection.style.display = 'none';
            }
        });
    });

    // Handle form submission
    const form = document.getElementById('bpmnForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const technique = formData.get('approach');
        
        // Show loading section with technique indicator
        document.getElementById('loadingSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';
        
        // Update technique indicator
        const techniqueDisplay = technique === 'llm' ? 'LLM-based' : 'Template-based';
        document.getElementById('currentTechnique').textContent = techniqueDisplay;
        
        // Scroll to loading section
        document.getElementById('loadingSection').scrollIntoView({ behavior: 'smooth' });
        
        // Submit form
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('loadingSection').style.display = 'none';
            
            if (data.success) {
                displayResults(data);
            } else {
                displayError(data.error || 'An unknown error occurred');
            }
        })
        .catch(error => {
            document.getElementById('loadingSection').style.display = 'none';
            displayError('Network error: ' + error.message);
        });
    });
});

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    
    // Determine if LLM was successfully used
    const llmSuccess = data.technique === 'llm' && data.technique_used === 'LLM-based';
    const llmIndicator = llmSuccess ? 
        '<span class="badge bg-success ms-2"><i class="fas fa-robot me-1"></i>LLM Success</span>' : 
        (data.technique === 'llm' ? '<span class="badge bg-warning ms-2"><i class="fas fa-exclamation-triangle me-1"></i>LLM Fallback to Template</span>' : '');
    
    resultsSection.innerHTML = `
        <div class="col-12">
            <div class="card border-success shadow-lg">
                <div class="card-header bg-success text-white">
                    <h3 class="card-title mb-0">
                        <i class="fas fa-check-circle me-2"></i>Policy Generation Results
                        ${llmIndicator}
                    </h3>
                </div>
                <div class="card-body">
                    <!-- Process Overview -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h5 class="card-title"><i class="fas fa-info-circle text-primary me-2"></i>Process Overview</h5>
                                    <ul class="list-unstyled mb-0">
                                        <li><strong>File:</strong> ${data.filename}</li>
                                        <li><strong>Technique:</strong> ${data.technique_used}</li>
                                        <li><strong>Fragmentation:</strong> ${data.fragmentation_strategy}</li>
                                        <li><strong>Process:</strong> ${data.bp_model.name}</li>
                                        <li><strong>Activities:</strong> ${data.bp_model.activities}</li>
                                        <li><strong>Fragments:</strong> ${data.fragments.length}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h5 class="card-title"><i class="fas fa-chart-pie text-info me-2"></i>Policy Metrics</h5>
                                    ${data.metrics ? `
                                        <div class="row text-center">
                                            <div class="col-4">
                                                <div class="metric-card bg-success text-white rounded p-2">
                                                    <div class="h4 mb-0">${data.metrics.total_permissions}</div>
                                                    <small>Permissions</small>
                                                </div>
                                            </div>
                                            <div class="col-4">
                                                <div class="metric-card bg-danger text-white rounded p-2">
                                                    <div class="h4 mb-0">${data.metrics.total_prohibitions}</div>
                                                    <small>Prohibitions</small>
                                                </div>
                                            </div>
                                            <div class="col-4">
                                                <div class="metric-card bg-warning text-white rounded p-2">
                                                    <div class="h4 mb-0">${data.metrics.total_obligations}</div>
                                                    <small>Obligations</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="mt-2 text-center">
                                            <small class="text-muted">Total Rules: ${data.metrics.total_rules}</small>
                                        </div>
                                    ` : '<p class="text-muted">Metrics not generated</p>'}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- BP Policy Information -->
                    ${data.bp_policy_info ? `
                        <div class="alert alert-info">
                            <h6><i class="fas fa-heart me-2"></i>BP-Level Policy Applied</h6>
                            <p class="mb-0">${data.bp_policy_info}</p>
                        </div>
                    ` : ''}

                    <!-- Fragments and Policies -->
                    <div class="accordion" id="fragmentsAccordion">
                        ${data.fragments.map((fragment, index) => `
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="heading${index}">
                                    <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" 
                                            data-bs-toggle="collapse" data-bs-target="#collapse${index}">
                                        <i class="fas fa-puzzle-piece me-2"></i>
                                        Fragment ${fragment.id} 
                                        <span class="badge bg-primary ms-2">${fragment.activities.length} activities</span>
                                        <span class="badge bg-secondary ms-1">${data.fragment_activity_policies[fragment.id] ? data.fragment_activity_policies[fragment.id].length : 0} policies</span>
                                    </button>
                                </h2>
                                <div id="collapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                                     data-bs-parent="#fragmentsAccordion">
                                    <div class="accordion-body">
                                        <!-- Activities -->
                                        <h6><i class="fas fa-tasks me-2"></i>Activities:</h6>
                                        <div class="row mb-3">
                                            ${fragment.activities.map(activity => `
                                                <div class="col-md-4 mb-2">
                                                    <span class="badge bg-light text-dark border">${activity.name || activity.id}</span>
                                                </div>
                                            `).join('')}
                                        </div>
                                        
                                        <!-- Policies -->
                                        <h6><i class="fas fa-shield-alt me-2"></i>Generated Policies:</h6>
                                        ${data.fragment_activity_policies[fragment.id] ? `
                                            <div class="table-responsive">
                                                <table class="table table-sm table-striped">
                                                    <thead class="table-dark">
                                                        <tr>
                                                            <th>Type</th>
                                                            <th>Action</th>
                                                            <th>Assignee</th>
                                                            <th>Activity</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        ${data.fragment_activity_policies[fragment.id].map(policy => `
                                                            <tr>
                                                                <td>
                                                                    <span class="badge ${policy.rule_type === 'permission' ? 'bg-success' : 
                                                                                       policy.rule_type === 'prohibition' ? 'bg-danger' : 'bg-warning'}">
                                                                        ${policy.rule_type}
                                                                    </span>
                                                                </td>
                                                                <td>${policy.action}</td>
                                                                <td>${policy.assignee}</td>
                                                                <td>${policy.target_activity_id}</td>
                                                            </tr>
                                                        `).join('')}
                                                    </tbody>
                                                </table>
                                            </div>
                                        ` : '<p class="text-muted">No policies generated for this fragment</p>'}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    <!-- Consistency Results -->
                    ${data.consistency_results ? `
                        <div class="mt-4">
                            <h5><i class="fas fa-check-double text-success me-2"></i>Policy Consistency Check</h5>
                            <div class="alert ${data.consistency_results.conflicts && data.consistency_results.conflicts.length > 0 ? 'alert-warning' : 'alert-success'}">
                                <strong>Conflicts Found:</strong> ${data.consistency_results.conflicts ? data.consistency_results.conflicts.length : 0}
                                ${data.consistency_results.conflicts && data.consistency_results.conflicts.length > 0 ? 
                                    '<ul class="mt-2">' + data.consistency_results.conflicts.map(conflict => `<li>${conflict}</li>`).join('') + '</ul>' : 
                                    '<p class="mb-0">All policies are consistent!</p>'}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Download Section -->
                    <div class="text-center mt-4">
                        <a href="/download/${data.results_dir}" class="btn btn-success btn-lg">
                            <i class="fas fa-download me-2"></i>Download Results (ZIP)
                        </a>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayError(errorMessage) {
    const errorSection = document.getElementById('errorSection');
    document.getElementById('errorMessage').textContent = errorMessage;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

