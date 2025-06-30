"""Start the AlviaOrange HTTP server with enhanced configuration."""

from __future__ import annotations

import os
import sys
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment variables with defaults."""
    # Load .env file first
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded environment variables from .env file")
    except ImportError:
        logger.warning("python-dotenv not found. Skipping .env file loading.")
        
    # API Configuration
    os.environ.setdefault("PORT", "8001")
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("RELOAD", "false")
    
    # API Keys - set defaults for demo/testing
    if not os.environ.get("VALID_API_KEYS"):
        os.environ["VALID_API_KEYS"] = "demo-key,test-key,development-key"
        logger.warning("Using default API keys for development. Set VALID_API_KEYS environment variable in production.")
    
    # External service configurations
    os.environ.setdefault("NASA_FIRMS_API_KEY", "demo_key")
    os.environ.setdefault("ENVIRONMENT_CANADA_TIMEOUT", "30")
    os.environ.setdefault("CWFIS_TIMEOUT", "30")
    
    # Rate limiting (can be overridden)
    os.environ.setdefault("RATE_LIMIT_REQUESTS", "1000")
    os.environ.setdefault("RATE_LIMIT_WINDOW", "3600")
    
    logger.info("Environment configuration complete")

def main():
    """Start the server with proper configuration."""
    setup_environment()
    
    # Add current directory to Python path to find alviaorange module
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Import app after environment setup
    try:
        from alviaorange.server import app
    except ImportError as e:
        logger.error(f"Failed to import AlviaOrange server: {e}")
        logger.error("Make sure you're running from the project root and all dependencies are installed")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Python path: {sys.path}")
        sys.exit(1)
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"Starting AlviaOrange API server on {host}:{port}")
    logger.info(f"API Documentation available at: http://{host}:{port}/api/orange/docs")
    logger.info(f"Health check endpoint: http://{host}:{port}/api/orange/health")
    
    if reload:
        logger.info("Auto-reload enabled for development")
    else:
        logger.info("Auto-reload disabled for stability")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover - manual entry
    main()
