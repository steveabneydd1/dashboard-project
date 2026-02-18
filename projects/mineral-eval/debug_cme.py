#!/usr/bin/env python3
"""
Debug CME WebSocket connection issues.
Tests endpoint, credentials, and network connectivity.
"""

import json
import time
from cme_config import load_cme_credentials

try:
    import websocket
    WEBSOCKET_OK = True
except ImportError:
    WEBSOCKET_OK = False

def test_credentials():
    """Load and validate credentials."""
    print("\n" + "="*60)
    print("STEP 1: Load Credentials from .env")
    print("="*60)
    
    try:
        creds = load_cme_credentials()
        print(f"✅ Credentials loaded:")
        print(f"   Username: {creds['username']}")
        print(f"   Password: {'*' * len(creds['password'])}")
        print(f"   Endpoint: {creds['endpoint']}")
        return creds
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None

def test_websocket_module():
    """Check if websocket-client is installed."""
    print("\n" + "="*60)
    print("STEP 2: Check websocket-client Module")
    print("="*60)
    
    if not WEBSOCKET_OK:
        print("❌ websocket-client not installed")
        print("   Run: python3 -m pip install websocket-client")
        return False
    
    print(f"✅ websocket-client installed: {websocket.__version__}")
    return True

def test_connection(creds):
    """Test actual WebSocket connection."""
    print("\n" + "="*60)
    print("STEP 3: Test WebSocket Connection")
    print("="*60)
    
    if not WEBSOCKET_OK:
        print("⏭️  Skipped (websocket-client not available)")
        return False
    
    endpoint = creds['endpoint']
    print(f"Connecting to: {endpoint}")
    
    connected = False
    authenticated = False
    error_msg = None
    
    def on_open(ws):
        nonlocal connected
        connected = True
        print("✅ WebSocket opened")
        
        # Send auth
        auth = {
            "user": creds['username'],
            "password": creds['password'],
        }
        print(f"Sending auth: {json.dumps(auth)}")
        ws.send(json.dumps(auth))
    
    def on_message(ws, message):
        nonlocal authenticated
        print(f"Message received: {message[:100]}...")
        try:
            data = json.loads(message)
            if "authenticated" in data:
                authenticated = data["authenticated"]
                if authenticated:
                    print("✅ Authentication successful!")
                else:
                    print("❌ Authentication failed")
        except:
            pass
    
    def on_error(ws, error):
        nonlocal error_msg
        error_msg = str(error)
        print(f"❌ WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print(f"WebSocket closed (code: {close_status_code})")
    
    try:
        ws = websocket.WebSocketApp(
            endpoint,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        
        # Run for up to 5 seconds
        ws.run_forever(timeout=5)
        
        if connected:
            print("✅ Connected to endpoint")
        else:
            print("❌ Failed to connect to endpoint")
        
        if authenticated:
            print("✅ Authenticated with CME")
            return True
        else:
            print("❌ Failed to authenticate (check username/password)")
            return False
    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print(f"\nPossible issues:")
        print(f"  1. Endpoint URL is incorrect")
        print(f"  2. Network/firewall blocking WebSocket")
        print(f"  3. CME cert environment not ready yet")
        return False

def test_endpoint_format(creds):
    """Validate endpoint URL format."""
    print("\n" + "="*60)
    print("STEP 4: Validate Endpoint Format")
    print("="*60)
    
    endpoint = creds['endpoint']
    print(f"Endpoint: {endpoint}")
    
    if not endpoint.startswith('wss://') and not endpoint.startswith('ws://'):
        print("❌ Endpoint should start with 'wss://' or 'ws://'")
        print("\nCommon CME WebSocket endpoints:")
        print("  wss://api.cmegroup.com/ws")
        print("  wss://datacert.cmegroup.com/ws (certification)")
        return False
    
    print("✅ Endpoint format looks valid")
    return True

def main():
    print("\n🔍 CME WebSocket Connection Debug Tool")
    print("=" * 60)
    
    # Step 1: Load credentials
    creds = test_credentials()
    if not creds:
        print("\n❌ Cannot proceed without credentials")
        return
    
    # Step 2: Check module
    ws_ok = test_websocket_module()
    
    # Step 3: Validate endpoint
    test_endpoint_format(creds)
    
    # Step 4: Test connection
    if ws_ok:
        result = test_connection(creds)
        if result:
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED - CME connection should work!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ CONNECTION FAILED - See above for details")
            print("="*60)
            print("\nNext steps:")
            print("1. Verify CME username/password are correct")
            print("2. Check if certification environment is fully activated")
            print("3. Run: python3 setup_cme.py to re-enter credentials")
            print("4. Contact CME support: cmedatasales@cmegroup.com")
    else:
        print("\n⏭️  Cannot test connection (websocket-client not installed)")

if __name__ == "__main__":
    main()
