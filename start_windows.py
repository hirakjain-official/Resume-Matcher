#!/usr/bin/env python3
"""
Windows-Safe Flask Application Launcher
Specifically designed to avoid Windows socket and threading issues
"""

import os
import sys
import logging
from pathlib import Path

# Add poppler to PATH if it exists
poppler_path = r"C:\poppler\poppler-24.02.0\Library\bin"
if os.path.exists(poppler_path) and poppler_path not in os.environ['PATH']:
    os.environ['PATH'] += f";{poppler_path}"

# Set Windows-specific environment variables
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['FLASK_ENV'] = 'development'

# Configure logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Main entry point for Windows Flask server"""
    try:
        # Import Flask app
        from app import app
        
        print("=" * 60)
        print("🚀 Resume Matcher - Windows Safe Mode")
        print("=" * 60)
        print("Starting Flask server...")
        print("Server will be available at: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Windows-optimized configuration
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
        
        # Start the server with Windows-safe settings
        app.run(
            debug=False,           # Disable debug mode
            host='127.0.0.1',      # Localhost only
            port=5000,             # Fixed port
            threaded=True,         # Enable threading
            use_reloader=False,    # Disable auto-reloader
            use_debugger=False     # Disable debugger
        )
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Server stopped by user")
        print("=" * 60)
        
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
        print(f"❌ Error starting server: {str(e)}")
        
    finally:
        print("🧹 Cleaning up...")
        # Force cleanup
        try:
            import threading
            import gc
            
            active_threads = threading.active_count()
            if active_threads > 1:
                print(f"📊 Waiting for {active_threads - 1} background threads...")
            
            gc.collect()
            print("✅ Cleanup completed")
            
        except Exception as cleanup_error:
            logging.error(f"Cleanup error: {str(cleanup_error)}")

if __name__ == '__main__':
    main()