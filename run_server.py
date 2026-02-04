#!/usr/bin/env python
"""
Startup script for Fridge Vision API.
Run: python run_server.py
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import get_config, print_config, API_CONFIG, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start the Fridge Vision API server."""
    try:
        # Print configuration
        print_config()
        
        # Import FastAPI app
        from api.main import app
        import uvicorn
        
        logger.info("Starting Fridge Vision API server...")
        logger.info(f"Host: {API_CONFIG['host']}")
        logger.info(f"Port: {API_CONFIG['port']}")
        logger.info(f"Debug: {API_CONFIG['debug']}")
        logger.info(f"Reload: {API_CONFIG['reload']}")
        
        # Run server
        uvicorn.run(
            app,
            host=API_CONFIG['host'],
            port=API_CONFIG['port'],
            debug=API_CONFIG['debug'],
            reload=API_CONFIG['reload'],
            workers=API_CONFIG['workers'],
            log_level=LOG_LEVEL.lower()
        )
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
