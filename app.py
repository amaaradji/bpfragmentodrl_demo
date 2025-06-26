"""
Flask web application for BPFragmentODRL demo tool.

This application provides a web interface for users to:
- Upload BPMN models
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
ALLOWED_EXTENSIONS = {'bpmn', 'xml'}

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
        # Check if file was uploaded
        if 'bpmn_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['bpmn_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a BPMN (.bpmn) or XML (.xml) file'}), 400
        
        # Get form parameters
        approach = request.form.get('approach', 'template')
        fragmentation_strategy = request.form.get('fragmentation_strategy', 'activity')
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the BPMN file
        tool = BPFragmentODRL()
        
        # Load BPMN file
        if not tool.load_bpmn_file(file_path):
            return jsonify({'error': 'Failed to load BPMN file. Please check if it is a valid BPMN file.'}), 400
        
        # Fragment process
        if not tool.fragment_process(fragmentation_strategy):
            return jsonify({'error': 'Failed to fragment the process.'}), 500
        
        # Generate policies
        if not tool.generate_policies(approach):
            return jsonify({'error': 'Failed to generate policies.'}), 500
        
        # Check policy consistency
        tool.check_policy_consistency()
        
        # Get metrics
        metrics = tool.get_policy_metrics()
        
        # Prepare response data
        response_data = {
            'success': True,
            'filename': file.filename,
            'approach': approach,
            'fragmentation_strategy': fragmentation_strategy,
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
            'consistency_results': tool.consistency_results,
            'metrics': metrics,
            'processing_timestamp': timestamp
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
                download_name=f'bpfragmentodrl_results_{results_dir}.zip',
                mimetype='application/zip'
            )
    
    except Exception as e:
        logger.error(f"Error creating download: {str(e)}")
        return jsonify({'error': 'Failed to create download'}), 500

@app.route('/api/approaches')
def get_approaches():
    """Get available policy generation approaches."""
    return jsonify({
        'approaches': [
            {'value': 'template', 'label': 'Template-based', 'description': 'Rule-based policy generation using predefined templates'},
            {'value': 'llm', 'label': 'LLM-based', 'description': 'AI-powered policy generation using Large Language Models'}
        ],
        'fragmentation_strategies': [
            {'value': 'activity', 'label': 'Activity-based', 'description': 'Fragment based on individual activities'},
            {'value': 'gateway', 'label': 'Gateway-based', 'description': 'Fragment based on gateway structures'},
            {'value': 'hybrid', 'label': 'Hybrid', 'description': 'Combination of activity and gateway-based fragmentation'}
        ]
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

