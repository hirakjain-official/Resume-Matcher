#!/usr/bin/env python3
"""
Windows-compatible Flask server startup script
Handles Windows-specific socket and threading issues
"""

import os
import sys
import logging
import signal
import atexit
from pathlib import Path

# Add poppler to PATH if it exists
poppler_path = r"C:\poppler\poppler-24.02.0\Library\bin"
if os.path.exists(poppler_path) and poppler_path not in os.environ['PATH']:
    os.environ['PATH'] += f";{poppler_path}"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\nReceived shutdown signal. Cleaning up...")
    cleanup_resources()
    sys.exit(0)

def run_app():
    """Run the Flask application with Windows-specific configurations"""
    # Setup signal handlers
    if os.name != 'nt':  # Unix systems
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    # Register cleanup function
    atexit.register(cleanup_resources)
    
    try:
        from app import app
        
        # Windows-specific Flask configuration
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        
        print("Starting Resume Matcher Web Application...")
        print("Server will be available at: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server")
        print("\n" + "="*50)
        
        # Set environment variables to avoid threading issues
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['FLASK_ENV'] = 'production'
        
        # Check if running in production (Render) or local development
        port = int(os.environ.get('PORT', 5000))
        is_production = os.environ.get('PORT') is not None
        
        if is_production:
            # Production settings for Render
            app.run(
                debug=False,
                host='0.0.0.0',
                port=port,
                threaded=True
            )
        else:
            # Windows local development settings
            app.run(
                debug=False,  # Disable debug mode to avoid reloader issues
                host='127.0.0.1',
                port=port,
                threaded=True,
                use_reloader=False,  # Disable auto-reloader on Windows
                use_debugger=False   # Disable debugger to avoid threading issues
            )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        cleanup_resources()
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        print(f"Error starting server: {str(e)}")
        cleanup_resources()
        sys.exit(1)

def cleanup_resources():
    """Clean up resources and threads on shutdown"""
    try:
        import threading
        import concurrent.futures
        
        # Get all threads
        active_threads = threading.active_count()
        if active_threads > 1:
            print(f"\nCleaning up {active_threads - 1} background threads...")
        
        # Force cleanup of any remaining futures
        import gc
        gc.collect()
        
        print("Cleanup completed.")
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")

if __name__ == '__main__':
    run_app()