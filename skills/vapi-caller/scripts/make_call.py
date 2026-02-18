#!/usr/bin/env python3
"""
Make an outbound phone call using the Vapi API.

Usage:
    python make_call.py --phone "+15551234567" --task "Schedule appointment for tomorrow"
    
Environment variables:
    VAPI_API_KEY - Your Vapi private API key (required)
    VAPI_ASSISTANT_ID - Your Vapi assistant ID (required)
    VAPI_PHONE_NUMBER_ID - Your Vapi phone number ID for caller ID (optional)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def make_vapi_call(phone_number: str, task: str, assistant_id: str = None, 
                   phone_number_id: str = None, api_key: str = None) -> dict:
    """
    Initiate an outbound phone call via Vapi API.
    
    Args:
        phone_number: E.164 formatted phone number (e.g., +15551234567)
        task: Description of what the assistant should accomplish on the call
        assistant_id: Vapi assistant ID (uses env var if not provided)
        phone_number_id: Vapi phone number ID for outbound caller ID (optional)
        api_key: Vapi API key (uses env var if not provided)
    
    Returns:
        dict: API response with call details
    """
    api_key = api_key or os.environ.get("VAPI_API_KEY")
    assistant_id = assistant_id or os.environ.get("VAPI_ASSISTANT_ID")
    phone_number_id = phone_number_id or os.environ.get("VAPI_PHONE_NUMBER_ID")
    
    if not api_key:
        raise ValueError("VAPI_API_KEY environment variable is required")
    if not assistant_id:
        raise ValueError("VAPI_ASSISTANT_ID environment variable is required")
    
    # Build the request payload
    payload = {
        "assistantId": assistant_id,
        "customer": {
            "number": phone_number
        },
        "assistantOverrides": {
            "variableValues": {
                "task": task
            }
        }
    }
    
    # Add phone number ID (required for outbound calls)
    if phone_number_id:
        payload["phoneNumberId"] = phone_number_id
    else:
        raise ValueError("VAPI_PHONE_NUMBER_ID environment variable is required for outbound calls")
    
    # Make the API request
    url = "https://api.vapi.ai/call"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
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
    parser = argparse.ArgumentParser(description="Make an outbound call via Vapi API")
    parser.add_argument("--phone", required=True, help="Phone number in E.164 format (e.g., +15551234567)")
    parser.add_argument("--task", required=True, help="Task description for the assistant")
    parser.add_argument("--assistant-id", help="Vapi assistant ID (overrides env var)")
    parser.add_argument("--phone-number-id", help="Vapi phone number ID for caller ID")
    parser.add_argument("--api-key", help="Vapi API key (overrides env var)")
    
    args = parser.parse_args()
    
    result = make_vapi_call(
        phone_number=args.phone,
        task=args.task,
        assistant_id=args.assistant_id,
        phone_number_id=args.phone_number_id,
        api_key=args.api_key
    )
    
    print(json.dumps(result, indent=2))
    
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
