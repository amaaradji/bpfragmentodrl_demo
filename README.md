# BPFragmentODRL Demo Tool

## Features

- **Fragment-level Policy Generation**: Generate policies for business process fragments
- **Multiple Approaches**: Template-based and LLM-based policy generation
- **Fragmentation Strategies**: Activity-based, Gateway-based, and Hybrid
- **BPMN Support**: Upload and process BPMN models
- **Policy Consistency**: Automatic consistency checking
- **Metrics Analysis**: Comprehensive policy analytics
- **ODRL Compliance**: Generate ODRL-compliant policies
- **Download Results**: Export generated policies and analysis

## Technical Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Processing**: BPMN parsing, policy generation, consistency checking
- **Output**: JSON, ODRL, ZIP downloads

## Project Structure

```
bpfragmentodrl_deployment/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku configuration
├── railway.toml          # Railway configuration
├── render.yaml           # Render configuration
├── runtime.txt           # Python version specification
├── templates/            # HTML templates
│   └── index.html
├── static/               # CSS, JS, images
│   ├── css/
│   └── js/
├── src/                  # BPFragmentODRL core modules
│   ├── bp_fragment_odrl.py
│   ├── bpmn_parser.py
│   ├── enhanced_fragmenter.py
│   ├── enhanced_policy_generator.py
│   └── ...
└── uploads/              # Temporary file storage
```

## Environment Variables

The application automatically detects the hosting environment and configures itself accordingly:

- **PORT**: Automatically set by hosting platforms
- **DEBUG**: Set to False in production
- **HOST**: Binds to 0.0.0.0 for external access

## Usage

1. **Upload BPMN Model**: Drag and drop or select a BPMN (.bpmn) or XML (.xml) file
2. **Select Approach**: Choose between Template-based or LLM-based policy generation
3. **Choose Strategy**: Select fragmentation strategy (Activity-based, Gateway-based, or Hybrid)
4. **Process**: Click "Process BPMN Model" to generate policies
5. **View Results**: Examine generated fragments, policies, and metrics
6. **Download**: Export results as a ZIP file

## API Endpoints

- `GET /`: Main application interface
- `POST /upload`: Process BPMN file and generate policies
- `GET /download/<results_dir>`: Download results as ZIP
- `GET /api/approaches`: Get available approaches and strategies
- `GET /health`: Health check endpoint

## Important Notes

- **File Size Limit**: 16MB maximum upload size
- **Supported Formats**: BPMN (.bpmn) and XML (.xml) files
- **Processing Time**: Typically 1-5 seconds for standard models
- **Storage**: Temporary files are automatically cleaned up

## Security Features

- File type validation
- Secure filename handling
- CORS protection
- Input sanitization
- Error handling and logging

## Performance

- **Response Time**: < 5 seconds for typical BPMN models
- **Memory Usage**: Optimized for cloud deployment
- **Scalability**: Supports multiple concurrent users
- **Reliability**: Comprehensive error handling

## Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are in requirements.txt
2. **Port Issues**: The app automatically uses the PORT environment variable
3. **File Upload Issues**: Check file format and size limits
4. **Memory Issues**: Large BPMN files may require more memory

### Logs:
- Check platform-specific logs for debugging
- Health check endpoint: `/health`

## License

This project is available for research and educational purposes.
