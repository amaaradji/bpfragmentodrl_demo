"""
Flask web application for BPFragmentODRL demo tool.

This application provides a web interface for users to:
- Upload BPMN models
- Upload or generate BP-level policies
- Select policy generation approach (template or LLM)
- View generated fragments and policies
- See policy metrics and analytics
- Download results
"""

import os
import sys
import json
import logging
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS

# Add parent directory to path to import BPFragmentODRL modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.bp_fragment_odrl import BPFragmentODRL
from src.bp_policy_generator import BPPolicyGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'bpfragmentodrl_demo_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Enable CORS for all routes
CORS(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'bpmn', 'xml', 'json', 'odrl'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page of the demo tool."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle BPMN file upload and processing."""
    try:
        # Check if BPMN file was uploaded
        if 'bpmn_file' not in request.files:
            return jsonify({'error': 'No BPMN file uploaded'}), 400
        
        bpmn_file = request.files['bpmn_file']
        if bpmn_file.filename == '':
            return jsonify({'error': 'No BPMN file selected'}), 400
        
        if not allowed_file(bpmn_file.filename):
            return jsonify({'error': 'Invalid BPMN file type. Please upload a BPMN (.bpmn) or XML (.xml) file'}), 400
        
        # Get form parameters
        technique = request.form.get('approach', 'template')  # Keep 'approach' for form compatibility
        fragmentation_strategy = request.form.get('fragmentation_strategy', 'activity')
        bp_policy_source = request.form.get('bp_policy_source', 'none')
        bp_policy_template = request.form.get('bp_policy_template', 'standard')
        
        # Advanced options
        enable_consistency_check = request.form.get('enable_consistency_check') == 'on'
        generate_metrics = request.form.get('generate_metrics') == 'on'
        export_odrl = request.form.get('export_odrl') == 'on'
        
        # Save uploaded BPMN file
        filename = secure_filename(bpmn_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        bpmn_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        bpmn_file.save(bpmn_file_path)
        
        # Handle BP-level policy
        bp_policy = None
        bp_policy_info = {'source': bp_policy_source}
        
        if bp_policy_source == 'upload':
            # Handle BP policy file upload
            if 'bp_policy_file' in request.files:
                bp_policy_file = request.files['bp_policy_file']
                if bp_policy_file.filename != '' and allowed_file(bp_policy_file.filename):
                    bp_policy_filename = secure_filename(bp_policy_file.filename)
                    bp_policy_filename = f"{timestamp}_bp_policy_{bp_policy_filename}"
                    bp_policy_file_path = os.path.join(app.config['UPLOAD_FOLDER'], bp_policy_filename)
                    bp_policy_file.save(bp_policy_file_path)
                    
                    # Load BP policy from file
                    try:
                        with open(bp_policy_file_path, 'r') as f:
                            bp_policy = json.load(f)
                        bp_policy_info['file'] = bp_policy_filename
                        bp_policy_info['loaded'] = True
                    except Exception as e:
                        logger.warning(f"Failed to load BP policy file: {str(e)}")
                        bp_policy_info['error'] = f"Failed to load BP policy: {str(e)}"
        
        elif bp_policy_source == 'generate':
            # Generate BP-level policy
            try:
                bp_policy_generator = BPPolicyGenerator()
                bp_policy = bp_policy_generator.generate_bp_policy(template=bp_policy_template)
                bp_policy_info['template'] = bp_policy_template
                bp_policy_info['generated'] = True
            except Exception as e:
                logger.warning(f"Failed to generate BP policy: {str(e)}")
                bp_policy_info['error'] = f"Failed to generate BP policy: {str(e)}"
        
        # Process the BPMN file
        tool = BPFragmentODRL()
        
        # Load BPMN file
        if not tool.load_bpmn_file(bpmn_file_path):
            return jsonify({'error': 'Failed to load BPMN file. Please check if it is a valid BPMN file.'}), 400
        
        # Fragment process
        if not tool.fragment_process(fragmentation_strategy):
            return jsonify({'error': 'Failed to fragment the process.'}), 500
        
        # Generate policies with BP-level policy
        if not tool.generate_policies(technique, bp_policy):
            return jsonify({'error': 'Failed to generate policies.'}), 500
        
        # Check policy consistency (if enabled)
        consistency_results = None
        if enable_consistency_check:
            consistency_results = tool.check_policy_consistency()
        
        # Get metrics (if enabled)
        metrics = None
        if generate_metrics:
            metrics = tool.get_policy_metrics()
        
        # Prepare response data
        response_data = {
            'success': True,
            'filename': bpmn_file.filename,
            'technique': technique,
            'technique_used': 'LLM-based' if technique == 'llm' else 'Template-based',
            'fragmentation_strategy': fragmentation_strategy,
            'bp_policy_info': bp_policy_info,
            'bp_policy': bp_policy,
            'bp_model': {
                'id': tool.bp_model.get('id', 'Unknown'),
                'name': tool.bp_model.get('name', 'Unnamed Process'),
                'activities': len(tool.bp_model.get('activities', [])),
                'gateways': len(tool.bp_model.get('gateways', [])),
                'events': len(tool.bp_model.get('events', []))
            },
            'fragments': tool.fragments,
            'fragment_activity_policies': tool.fragment_activity_policies,
            'fragment_dependency_policies': tool.fragment_dependency_policies,
            'consistency_results': consistency_results,
            'metrics': metrics,
            'processing_timestamp': timestamp,
            'options': {
                'consistency_check': enable_consistency_check,
                'generate_metrics': generate_metrics,
                'export_odrl': export_odrl
            }
        }
        
        # Save results for download
        results_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'results_{timestamp}')
        tool.save_results(results_dir)
        response_data['results_dir'] = f'results_{timestamp}'
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': f'An error occurred while processing the file: {str(e)}'}), 500

@app.route('/download/<results_dir>')
def download_results(results_dir):
    """Download results as a ZIP file."""
    try:
        results_path = os.path.join(app.config['UPLOAD_FOLDER'], results_dir)
        
        if not os.path.exists(results_path):
            return jsonify({'error': 'Results not found'}), 404
        
        # Create a ZIP file of the results
        import zipfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(results_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, results_path)
                        zip_file.write(file_path, arc_name)
            
            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name=f'{results_dir}.zip',
                mimetype='application/zip'
            )
            
    except Exception as e:
        logger.error(f"Error creating download: {str(e)}")
        return jsonify({'error': f'An error occurred while creating the download: {str(e)}'}), 500

@app.route('/api/approaches')
def get_approaches():
    """Get available policy generation approaches and fragmentation strategies."""
    return jsonify({
        'approaches': ['template', 'llm'],
        'fragmentation_strategies': ['activity', 'gateway', 'hybrid'],
        'bp_policy_templates': [
            'standard',
            'financial', 
            'healthcare',
            'manufacturing',
            'custom'
        ]
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

