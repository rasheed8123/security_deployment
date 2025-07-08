#!/usr/bin/env python3
"""
Quick Commerce Medicine Delivery - Frontend Application
Run this script to start the Streamlit frontend application.
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    print("🏥 Starting Quick Commerce Medicine Delivery Frontend...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("🔄 Make sure the backend server is running on port 8000")
    print("-" * 50)
    
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    os.chdir(frontend_dir)
    
    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ]) 