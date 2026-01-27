#!/usr/bin/env python3
"""
Startup script for the web interface.
"""
import subprocess
import sys
import os
from pathlib import Path


def install_flask():
    """Install Flask if not available."""
    try:
        import flask
        print("✅ Flask is already installed")
    except ImportError:
        print("📦 Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        print("✅ Flask installed successfully")


def create_directories():
    """Create necessary directories."""
    directories = ["output", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def main():
    """Main startup function."""
    print("🌐 Starting Research System Web Interface")
    print("=" * 50)
    
    # Install Flask if needed
    install_flask()
    
    # Create directories
    create_directories()
    
    # Start the web server
    print("\n🚀 Starting web server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


if __name__ == "__main__":
    main()