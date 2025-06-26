# BPFragmentODRL Demo Tool - Production Deployment

A web-based tool for fragment-level policy generation in business processes using both template-based and LLM approaches.

## 🚀 Quick Deploy

### Railway.app (Recommended)
1. Fork this repository to your GitHub
2. Go to [Railway.app](https://railway.app)
3. Click "Deploy from GitHub repo"
4. Select your forked repository
5. Railway will automatically detect and deploy your Flask app
6. Your app will be live in 2-3 minutes!

### Render.com
1. Fork this repository to your GitHub
2. Go to [Render.com](https://render.com)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Render will use the `render.yaml` configuration
6. Deploy automatically!

### Heroku
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Fork this repository
3. Clone your fork locally
4. Run these commands:
```bash
heroku create your-app-name
git push heroku main
heroku open
```

### PythonAnywhere
1. Upload files to your PythonAnywhere account
2. Create a new web app (Flask)
3. Point to your `app.py` file
4. Install requirements: `pip3.11 install --user -r requirements.txt`
5. Reload your web app

## 📋 Features

- **Fragment-level Policy Generation**: Generate policies for business process fragments
- **Multiple Approaches**: Template-based and LLM-based policy generation
- **Fragmentation Strategies**: Activity-based, Gateway-based, and Hybrid
- **BPMN Support**: Upload and process BPMN models
- **Policy Consistency**: Automatic consistency checking
- **Metrics Analysis**: Comprehensive policy analytics
- **ODRL Compliance**: Generate ODRL-compliant policies
- **Download Results**: Export generated policies and analysis

## 🛠 Technical Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Processing**: BPMN parsing, policy generation, consistency checking
- **Output**: JSON, ODRL, ZIP downloads

## 📁 Project Structure

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

## 🔧 Configuration Files

- **Procfile**: Heroku deployment configuration
- **railway.toml**: Railway.app deployment settings
- **render.yaml**: Render.com service configuration
- **runtime.txt**: Python version specification
- **requirements.txt**: Python package dependencies

## 🌐 Environment Variables

The application automatically detects the hosting environment and configures itself accordingly:

- **PORT**: Automatically set by hosting platforms
- **DEBUG**: Set to False in production
- **HOST**: Binds to 0.0.0.0 for external access

## 📊 Usage

1. **Upload BPMN Model**: Drag and drop or select a BPMN (.bpmn) or XML (.xml) file
2. **Select Approach**: Choose between Template-based or LLM-based policy generation
3. **Choose Strategy**: Select fragmentation strategy (Activity-based, Gateway-based, or Hybrid)
4. **Process**: Click "Process BPMN Model" to generate policies
5. **View Results**: Examine generated fragments, policies, and metrics
6. **Download**: Export results as a ZIP file

## 🔍 API Endpoints

- `GET /`: Main application interface
- `POST /upload`: Process BPMN file and generate policies
- `GET /download/<results_dir>`: Download results as ZIP
- `GET /api/approaches`: Get available approaches and strategies
- `GET /health`: Health check endpoint

## 🚨 Important Notes

- **File Size Limit**: 16MB maximum upload size
- **Supported Formats**: BPMN (.bpmn) and XML (.xml) files
- **Processing Time**: Typically 1-5 seconds for standard models
- **Storage**: Temporary files are automatically cleaned up

## 🔒 Security Features

- File type validation
- Secure filename handling
- CORS protection
- Input sanitization
- Error handling and logging

## 📈 Performance

- **Response Time**: < 5 seconds for typical BPMN models
- **Memory Usage**: Optimized for cloud deployment
- **Scalability**: Supports multiple concurrent users
- **Reliability**: Comprehensive error handling

## 🆘 Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are in requirements.txt
2. **Port Issues**: The app automatically uses the PORT environment variable
3. **File Upload Issues**: Check file format and size limits
4. **Memory Issues**: Large BPMN files may require more memory

### Logs:
- Check platform-specific logs for debugging
- Health check endpoint: `/health`

## 📞 Support

For issues or questions:
1. Check the logs on your hosting platform
2. Verify all files are uploaded correctly
3. Ensure requirements.txt includes all dependencies
4. Test locally before deploying

## 📄 License

This project is available for research and educational purposes.

---

**Ready to deploy?** Choose your preferred platform above and follow the quick deploy instructions!

