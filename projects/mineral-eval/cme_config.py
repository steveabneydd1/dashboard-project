"""
Load CME credentials from .env file.
Used by dashboard and other modules that need to authenticate with CME.
"""

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
ENV_FILE = PROJECT_DIR / ".env"

def load_cme_credentials():
    """
    Load CME credentials from .env file.
    Returns: dict with 'username', 'password', 'endpoint'
    Raises: FileNotFoundError if .env doesn't exist
    """
    if not ENV_FILE.exists():
        raise FileNotFoundError(
            f".env file not found at {ENV_FILE}\n"
            "Run: python3 setup_cme.py"
        )
    
    creds = {}
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                creds[key.strip()] = value.strip()
    
    required = ["CME_USERNAME", "CME_PASSWORD", "CME_ENDPOINT"]
    missing = [k for k in required if k not in creds]
    if missing:
        raise ValueError(f"Missing credentials in .env: {missing}")
    
    return {
        "username": creds["CME_USERNAME"],
        "password": creds["CME_PASSWORD"],
        "endpoint": creds["CME_ENDPOINT"],
    }

if __name__ == "__main__":
    # Test: load and print (without exposing password)
    try:
        creds = load_cme_credentials()
        print("✅ Credentials loaded successfully")
        print(f"   Username: {creds['username']}")
        print(f"   Endpoint: {creds['endpoint']}")
    except Exception as e:
        print(f"❌ Error: {e}")
