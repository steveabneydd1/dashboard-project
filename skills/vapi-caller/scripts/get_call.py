#!/usr/bin/env python3
"""
Get the status and details of a Vapi call.

Usage:
    python get_call.py --call-id "abc123"
    
Environment variables:
    VAPI_API_KEY - Your Vapi private API key (required)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def get_vapi_call(call_id: str, api_key: str = None) -> dict:
    """
    Get details of a Vapi call.
    
    Args:
        call_id: The Vapi call ID
        api_key: Vapi API key (uses env var if not provided)
    
    Returns:
        dict: Call details including status, transcript, recording URL, etc.
    """
    api_key = api_key or os.environ.get("VAPI_API_KEY")
    
    if not api_key:
        raise ValueError("VAPI_API_KEY environment variable is required")
    
    url = f"https://api.vapi.ai/call/{call_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    request = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {"success": True, "call": result}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        try:
            error_json = json.loads(error_body)
        except json.JSONDecodeError:
            error_json = {"message": error_body}
        return {"success": False, "error": error_json, "status_code": e.code}
    except urllib.error.URLError as e:
        return {"success": False, "error": {"message": str(e.reason)}}


def main():
    parser = argparse.ArgumentParser(description="Get Vapi call details")
    parser.add_argument("--call-id", required=True, help="The Vapi call ID")
    parser.add_argument("--api-key", help="Vapi API key (overrides env var)")
    
    args = parser.parse_args()
    
    result = get_vapi_call(call_id=args.call_id, api_key=args.api_key)
    
    print(json.dumps(result, indent=2))
    
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
