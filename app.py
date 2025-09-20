#!/usr/bin/env python3
"""
Resume Matcher Web Application

A modern web interface for AI-powered resume matching system.
"""

import os
import json
import zipfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import logging

from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import PyPDF2
import docx2txt
from threading import Thread
import threading
import uuid

# Import our existing resume matcher
from resume_matcher import process_resumes, extract_job_requirements, choose_api

app = Flask(__name__)
app.secret_key = 'resume-matcher-secure-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('temp', exist_ok=True)
os.makedirs('results', exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    """Extract text from various file formats"""
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.pdf':
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                return text
        
        elif file_ext == '.docx':
            return docx2txt.process(file_path)
        
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
    
    except Exception as e:
        logging.error(f"Error extracting text from {file_path}: {str(e)}")
        return ""
    
    return ""

def extract_job_details(job_text):
    """Extract job title and description from job posting text"""
    try:
        # Simple extraction - you can enhance this with NLP
        lines = job_text.strip().split('\n')
        
        # Try to find job title (usually in first few lines)
        job_title = "Software Engineer"  # Default
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                if any(keyword in line.lower() for keyword in ['engineer', 'developer', 'analyst', 'manager', 'specialist']):
                    job_title = line
                    break
        
        return {
            'title': job_title,
            'description': job_text,
            'requirements': job_text  # For now, use full text as requirements
        }
    
    except Exception as e:
        logging.error(f"Error extracting job details: {str(e)}")
        return {
            'title': 'Job Position',
            'description': job_text,
            'requirements': job_text
        }

class ProcessingStatus:
    """Class to track processing status"""
    def __init__(self):
        self.sessions = {}
    
    def start_processing(self, session_id):
        self.sessions[session_id] = {
            'status': 'processing',
            'progress': 0,
            'stage': 'Initializing...',
            'results': None,
            'error': None
        }
    
    def update_progress(self, session_id, progress, stage):
        if session_id in self.sessions:
            self.sessions[session_id]['progress'] = progress
            self.sessions[session_id]['stage'] = stage
    
    def complete_processing(self, session_id, results):
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = 'completed'
            self.sessions[session_id]['progress'] = 100
            self.sessions[session_id]['stage'] = 'Completed'
            self.sessions[session_id]['results'] = results
    
    def set_error(self, session_id, error):
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = 'error'
            self.sessions[session_id]['error'] = str(error)
    
    def get_status(self, session_id):
        return self.sessions.get(session_id, {'status': 'not_found'})

# Global processing status tracker
processing_status = ProcessingStatus()

def process_resumes_async(session_id, job_description, resume_files):
    """Process resumes asynchronously"""
    try:
        # Initialize API
        processing_status.update_progress(session_id, 10, 'Initializing AI API...')
        choose_api()
        
        processing_status.update_progress(session_id, 20, 'Processing resumes...')
        
        # Process resumes using existing backend with timeout protection
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Processing timeout exceeded")
        
        # Set a timeout for the entire processing (30 minutes)
        if os.name != 'nt':  # Unix systems
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1800)  # 30 minutes
        
        try:
            results = process_resumes(job_description, resume_files)
        finally:
            if os.name != 'nt':  # Unix systems
                signal.alarm(0)  # Cancel the alarm
        
        # Sort results by score
        sorted_results = sorted(results, key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
        
        processing_status.update_progress(session_id, 90, 'Generating final report...')
        
        # Format results for web display
        formatted_results = []
        for result in sorted_results:
            if len(result) >= 8:
                filename, score, emoji, color, label, match_reasons, website, red_flags = result
                formatted_results.append({
                    'filename': filename,
                    'score': score,
                    'emoji': emoji,
                    'color': color,
                    'label': label,
                    'match_reasons': match_reasons,
                    'website': website,
                    'red_flags': red_flags
                })
        
        # Calculate statistics
        scores = [r['score'] for r in formatted_results if isinstance(r['score'], (int, float))]
        stats = {
            'total_candidates': len(formatted_results),
            'top_score': max(scores) if scores else 0,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'qualified_candidates': len([s for s in scores if s >= 80])
        }
        
        final_results = {
            'candidates': formatted_results,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }
        
        processing_status.complete_processing(session_id, final_results)
        
    except TimeoutError as e:
        logging.error(f"Processing timeout for session {session_id}: {str(e)}")
        processing_status.set_error(session_id, "Processing timeout - please try with fewer resumes")
    except Exception as e:
        logging.error(f"Error in async processing: {str(e)}")
        processing_status.set_error(session_id, str(e))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Check if files are present
        if 'job_file' not in request.files or 'resume_files' not in request.files:
            return jsonify({'error': 'Missing required files'}), 400
        
        job_file = request.files['job_file']
        resume_file = request.files['resume_files']
        
        if job_file.filename == '' or resume_file.filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate file types
        if not (allowed_file(job_file.filename) and allowed_file(resume_file.filename)):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Create session ID
        session_id = str(uuid.uuid4())
        
        # Create temporary directories
        temp_dir = Path('temp') / session_id
        temp_dir.mkdir(exist_ok=True)
        
        # Save job file
        job_filename = secure_filename(job_file.filename)
        job_path = temp_dir / job_filename
        job_file.save(str(job_path))
        
        # Extract job description
        job_text = extract_text_from_file(job_path)
        if not job_text.strip():
            return jsonify({'error': 'Could not extract text from job file'}), 400
        
        job_details = extract_job_details(job_text)
        
        # Handle resume file (ZIP or single PDF)
        resume_files = []
        if resume_file.filename.endswith('.zip'):
            # Extract ZIP file
            zip_path = temp_dir / secure_filename(resume_file.filename)
            resume_file.save(str(zip_path))
            
            resume_dir = temp_dir / 'resumes'
            resume_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(resume_dir)
            
            # Find all PDF files in extracted directory
            for pdf_file in resume_dir.rglob('*.pdf'):
                resume_files.append(str(pdf_file))
        
        else:
            # Single resume file
            resume_filename = secure_filename(resume_file.filename)
            resume_path = temp_dir / resume_filename
            resume_file.save(str(resume_path))
            resume_files.append(str(resume_path))
        
        if not resume_files:
            return jsonify({'error': 'No valid resume files found'}), 400
        
        # Store session info
        session['session_id'] = session_id
        session['job_details'] = job_details
        session['resume_count'] = len(resume_files)
        
        # Start async processing
        processing_status.start_processing(session_id)
        thread = Thread(
            target=process_resumes_async, 
            args=(session_id, job_details['description'], resume_files),
            name=f'ResumeProcessor-{session_id[:8]}'
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'job_title': job_details['title'],
            'resume_count': len(resume_files)
        })
    
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/status/<session_id>')
def get_status(session_id):
    status = processing_status.get_status(session_id)
    return jsonify(status)

@app.route('/results/<session_id>')
def show_results(session_id):
    status = processing_status.get_status(session_id)
    
    if status['status'] != 'completed':
        return redirect(url_for('processing', session_id=session_id))
    
    return render_template('results.html', 
                         results=status['results'],
                         job_details=session.get('job_details', {}),
                         session_id=session_id)

@app.route('/processing/<session_id>')
def processing(session_id):
    return render_template('processing.html', session_id=session_id)

@app.route('/contact', methods=['POST'])
def send_contact_email():
    try:
        data = request.get_json()
        candidate_name = data.get('candidate_name')
        candidate_email = data.get('candidate_email')
        message = data.get('message')
        
        # Here you would integrate with your email service
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'message': f'Email prepared for {candidate_name}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Use 0.0.0.0 for production hosting, 127.0.0.1 for local development
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    # Windows-specific configuration to avoid socket errors
    if os.name == 'nt' and not os.environ.get('PORT'):  # Windows local development
        app.run(debug=False, host='127.0.0.1', port=port, threaded=True, use_reloader=False)
    else:  # Production or non-Windows
        app.run(debug=debug, host=host, port=port, threaded=True)
