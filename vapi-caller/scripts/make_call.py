#!/usr/bin/env python3
"""
Make phone calls using Vapi API
"""
import os
import sys
import argparse
import requests
import json

def make_call(phone_number, task, assistant_id, api_key):
    """Make a phone call via Vapi"""
    
    url = "https://api.vapi.ai/call/phone"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "phoneNumberId": "e056348c-e1ad-485c-9394-11fd2e5c506c",
        "customer": {
            "number": phone_number
        },
        "assistantId": assistant_id,
        "assistantOverrides": {
            "variableValues": {
                "task": task
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"✓ Call initiated successfully!")
        print(f"Call ID: {result.get('id', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error making call: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Make a phone call via Vapi')
    parser.add_argument('--phone', required=True, help='Phone number to call (E.164 format, e.g., +1234567890)')
    parser.add_argument('--task', required=True, help='Task description for the call')
    
    args = parser.parse_args()
    
    # Get credentials from environment
    api_key = os.environ.get('VAPI_API_KEY')
    assistant_id = os.environ.get('VAPI_ASSISTANT_ID')
    
    if not api_key:
        print("Error: VAPI_API_KEY environment variable not set")
        sys.exit(1)
    
    if not assistant_id:
        print("Error: VAPI_ASSISTANT_ID environment variable not set")
        sys.exit(1)
    
    make_call(args.phone, args.task, assistant_id, api_key)

if __name__ == "__main__":
    main()
