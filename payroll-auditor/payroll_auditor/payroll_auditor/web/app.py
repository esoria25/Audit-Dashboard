"""
Web interface for the Payroll Auditor Tool using Flask
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

try:
    from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'payroll-auditor-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration
UPLOAD_FOLDER = Path('uploads')
RESULTS_FOLDER = Path('results')
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf', 'csv', 'json'}

# Create directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with file upload form"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payroll Auditor Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .hero-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 0; }
        .card { border: none; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .upload-area { border: 2px dashed #dee2e6; border-radius: 10px; padding: 40px; text-align: center; transition: all 0.3s; }
        .upload-area:hover { border-color: #007bff; background-color: #f8f9ff; }
        .feature-icon { font-size: 3rem; color: #007bff; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-calculator me-2"></i>
                Payroll Auditor
            </a>
        </div>
    </nav>

    <!-- Hero Section -->
    <div class="hero-section">
        <div class="container text-center">
            <h1 class="display-4 mb-4">
                <i class="fas fa-search me-3"></i>
                Payroll Auditor Tool
            </h1>
            <p class="lead mb-4">Compare and audit payroll data across different file formats with intelligent analysis</p>
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="d-flex justify-content-center flex-wrap gap-3">
                        <span class="badge bg-light text-dark fs-6 px-3 py-2">Excel Support</span>
                        <span class="badge bg-light text-dark fs-6 px-3 py-2">PDF Processing</span>
                        <span class="badge bg-light text-dark fs-6 px-3 py-2">Smart Matching</span>
                        <span class="badge bg-light text-dark fs-6 px-3 py-2">Risk Assessment</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container mt-5">
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <div class="card">
                    <div class="card-header bg-white">
                        <h4 class="mb-0">
                            <i class="fas fa-file-alt me-2 text-primary"></i>
                            Upload Payroll Files for Comparison
                        </h4>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="/upload" enctype="multipart/form-data" id="uploadForm">
                            <div class="row mb-4">
                                <div class="col-md-6">
                                    <div class="upload-area">
                                        <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                                        <h5>First Payroll File</h5>
                                        <input type="file" class="form-control mt-3" name="file1" 
                                               accept=".xlsx,.xls,.pdf,.csv,.json" required>
                                        <small class="text-muted">Source 1: Previous or reference data</small>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="upload-area">
                                        <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
                                        <h5>Second Payroll File</h5>
                                        <input type="file" class="form-control mt-3" name="file2" 
                                               accept=".xlsx,.xls,.pdf,.csv,.json" required>
                                        <small class="text-muted">Source 2: Current or comparison data</small>
                                    </div>
                                </div>
                            </div>

                            <!-- Settings -->
                            <div class="card mb-4">
                                <div class="card-header">
                                    <h6 class="mb-0">
                                        <i class="fas fa-cog me-1"></i>
                                        Comparison Settings
                                    </h6>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-4">
                                            <label class="form-label">Earnings Tolerance ($)</label>
                                            <input type="number" class="form-control" name="earnings_tolerance" 
                                                   value="0.01" step="0.01" min="0">
                                            <small class="text-muted">Allow small rounding differences</small>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">Name Match Threshold</label>
                                            <input type="number" class="form-control" name="name_threshold" 
                                                   value="0.8" step="0.1" min="0" max="1">
                                            <small class="text-muted">0.8 = 80% similarity required</small>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="form-check mt-4">
                                                <input class="form-check-input" type="checkbox" name="fuzzy_matching" checked>
                                                <label class="form-check-label">Enable Fuzzy Matching</label>
                                                <small class="d-block text-muted">Match similar names</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fas fa-search me-2"></i>
                                    Start Comparison Analysis
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Features Section -->
        <div class="row mt-5 mb-5">
            <div class="col-md-4">
                <div class="card h-100 text-center">
                    <div class="card-body">
                        <i class="fas fa-file-excel feature-icon"></i>
                        <h5>Multi-Format Support</h5>
                        <p class="text-muted">Compare Excel, PDF, CSV, and JSON files seamlessly with intelligent parsing</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 text-center">
                    <div class="card-body">
                        <i class="fas fa-brain feature-icon"></i>
                        <h5>Smart Matching</h5>
                        <p class="text-muted">AI-powered employee matching with fuzzy name recognition and similarity scoring</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card h-100 text-center">
                    <div class="card-body">
                        <i class="fas fa-chart-line feature-icon"></i>
                        <h5>Detailed Analysis</h5>
                        <p class="text-muted">Comprehensive reports with risk assessment and actionable recommendations</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4 mt-5">
        <div class="container text-center">
            <p class="mb-0">
                <i class="fas fa-code me-1"></i>
                Payroll Auditor Tool - Built for payroll professionals
            </p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('uploadForm').addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            submitBtn.disabled = true;
        });
    </script>
</body>
</html>
    '''

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file upload and start comparison"""
    
    if 'file1' not in request.files or 'file2' not in request.files:
        return '''
        <div style="padding: 40px; text-align: center; font-family: Arial;">
            <h2>❌ Upload Error</h2>
            <p>Please select both files for comparison.</p>
            <a href="/" style="color: #007bff;">← Go Back</a>
        </div>
        '''
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if file1.filename == '' or file2.filename == '':
        return '''
        <div style="padding: 40px; text-align: center; font-family: Arial;">
            <h2>❌ Upload Error</h2>
            <p>Please select both files for comparison.</p>
            <a href="/" style="color: #007bff;">← Go Back</a>
        </div>
        '''
    
    if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
        return '''
        <div style="padding: 40px; text-align: center; font-family: Arial;">
            <h2>❌ File Format Error</h2>
            <p>Unsupported file format. Please use Excel (.xlsx), PDF, CSV, or JSON files.</p>
            <a href="/" style="color: #007bff;">← Go Back</a>
        </div>
        '''
    
    # For now, return a success message
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comparison Results</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h4 class="mb-0">
                                <i class="fas fa-check-circle me-2"></i>
                                Files Uploaded Successfully!
                            </h4>
                        </div>
                        <div class="card-body">
                            <div class="alert alert-info">
                                <h5><i class="fas fa-info-circle me-2"></i>Processing Status</h5>
                                <p><strong>File 1:</strong> {file1.filename}</p>
                                <p><strong>File 2:</strong> {file2.filename}</p>
                                <p><strong>Status:</strong> Ready for analysis</p>
                            </div>
                            
                            <div class="alert alert-warning">
                                <h5><i class="fas fa-tools me-2"></i>Development Note</h5>
                                <p>This is the web interface framework. The full comparison engine is being integrated.</p>
                                <p><strong>Next steps:</strong></p>
                                <ul>
                                    <li>File parsing and data extraction</li>
                                    <li>Employee matching algorithms</li>
                                    <li>Discrepancy analysis</li>
                                    <li>Report generation</li>
                                </ul>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <a href="/" class="btn btn-primary">
                                    <i class="fas fa-arrow-left me-2"></i>
                                    Upload More Files
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/status')
def api_status():
    """API endpoint to check system status"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'features': {
            'file_upload': True,
            'comparison_engine': 'in_development',
            'supported_formats': ['xlsx', 'pdf', 'csv', 'json']
        }
    })

if __name__ == '__main__':
    if not FLASK_AVAILABLE:
        print("❌ Flask not installed. Please install dependencies:")
        print("pip install flask")
        print("Or install all dependencies: pip install -r requirements.txt")
    else:
        print("🚀 Starting Payroll Auditor Web Interface...")
        print("📱 Open your browser to: http://localhost:5000")
        print("📋 Supported formats: Excel, PDF, CSV, JSON")
        print("⚡ Press Ctrl+C to stop the server")
        app.run(debug=True, host='0.0.0.0', port=5000)
