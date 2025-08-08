#!/usr/bin/env python
"""
Railway startup script that ensures all dependencies are installed
"""

import subprocess
import sys
import os

print("🚀 Starting PrevostGO Backend on Railway...")

# Ensure we're in the right directory
if os.path.exists('backend'):
    os.chdir('backend')
    print("✅ Changed to backend directory")

# Install dependencies
print("📦 Installing dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Now import and run the main app
print("🌐 Starting FastAPI application...")
import main

# If main.py doesn't run the server automatically, do it here
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
