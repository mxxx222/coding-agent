#!/usr/bin/env python3
"""Simple script to run the Coding Agent API server."""

if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Add the server directory to the Python path
    sys.path.insert(0, os.path.dirname(__file__))
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

