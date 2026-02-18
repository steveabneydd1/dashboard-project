#!/usr/bin/env python3
"""Create calendar event via Microsoft Graph API."""
import os
import sys
import json
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
from datetime import datetime, timedelta

def get_access_token(tenant_id, client_id, client_secret):
    """Get OAuth2 access token using client credentials flow."""
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }).encode()
    
    req = Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        return result['access_token']

def create_event(access_token, user_email, subject, start_time, end_time, attendees, body=None, location=None, timezone="America/Chicago"):
    """Create calendar event via Graph API."""
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/calendar/events"
    
    event = {
        'subject': subject,
        'start': {
            'dateTime': start_time,
            'timeZone': timezone
        },
        'end': {
            'dateTime': end_time,
            'timeZone': timezone
        },
        'attendees': [
            {
                'emailAddress': {'address': addr.strip()},
                'type': 'required'
            } for addr in attendees.split(',')
        ]
    }
    
    if body:
        event['body'] = {
            'contentType': 'HTML',
            'content': body.replace('\n', '<br>')
        }
    
    if location:
        event['location'] = {'displayName': location}
    
    req = Request(url, data=json.dumps(event).encode(), method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            return {'success': True, 'event_id': result.get('id'), 'web_link': result.get('webLink')}
    except HTTPError as e:
        error_body = e.read().decode()
        return {'success': False, 'status': e.code, 'error': error_body}

def main():
    parser = argparse.ArgumentParser(description='Create calendar event via Microsoft Graph')
    parser.add_argument('--subject', required=True, help='Event subject/title')
    parser.add_argument('--start', required=True, help='Start time (YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--end', help='End time (YYYY-MM-DDTHH:MM:SS). Defaults to 1 hour after start.')
    parser.add_argument('--attendees', required=True, help='Attendee email(s), comma-separated')
    parser.add_argument('--body', help='Event description')
    parser.add_argument('--location', help='Event location')
    parser.add_argument('--timezone', default='America/Chicago', help='Timezone (default: America/Chicago)')
    args = parser.parse_args()
    
    # Get credentials from environment
    tenant_id = os.environ.get('MS_TENANT_ID')
    client_id = os.environ.get('MS_CLIENT_ID')
    client_secret = os.environ.get('MS_CLIENT_SECRET')
    user_email = os.environ.get('MS_USER_EMAIL')
    
    if not all([tenant_id, client_id, client_secret, user_email]):
        print(json.dumps({'success': False, 'error': 'Missing environment variables'}))
        sys.exit(1)
    
    # Default end time to 1 hour after start
    end_time = args.end
    if not end_time:
        start_dt = datetime.fromisoformat(args.start)
        end_dt = start_dt + timedelta(hours=1)
        end_time = end_dt.isoformat()
    
    try:
        token = get_access_token(tenant_id, client_id, client_secret)
        result = create_event(
            token, user_email,
            args.subject, args.start, end_time,
            args.attendees,
            body=args.body,
            location=args.location,
            timezone=args.timezone
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
