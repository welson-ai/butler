"""
What this file does: Main entry point for the Crypto Butler backend server
What it receives as input: Command line arguments and environment variables
What it returns as output: Running Flask server with WebSocket support
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

from api.routes import api
from utils.logger import ButlerLogger

def create_app():
    """
    Create and configure Flask application
    
    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5173', '*'])
    
    # Register blueprint
    app.register_blueprint(api, url_prefix='/')
    
    return app

def main():
    """
    Main entry point for the backend server
    """
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = create_app()
    
    # Print startup message
    print("Butler API running on port 5001")
    
    # Run on port 5001
    app.run(host='0.0.0.0', port=5001, debug=True)

if __name__ == '__main__':
    main()
