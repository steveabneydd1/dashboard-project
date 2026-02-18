#!/usr/bin/env python3
"""Send email via Microsoft Graph API."""
import os
import sys
import json
import argparse
import base64
import mimetypes
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

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

def send_email(access_token, user_email, to, subject, body, attachments=None, cc=None, bcc=None):
    """Send email via Graph API."""
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail"
    
    message = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'HTML',
                'content': body.replace('\n', '<br>')
            },
            'toRecipients': [{'emailAddress': {'address': addr.strip()}} for addr in to.split(',')],
        },
        'saveToSentItems': True
    }
    
    if cc:
        message['message']['ccRecipients'] = [{'emailAddress': {'address': addr.strip()}} for addr in cc.split(',')]
    
    if bcc:
        message['message']['bccRecipients'] = [{'emailAddress': {'address': addr.strip()}} for addr in bcc.split(',')]
    
    if attachments:
        message['message']['attachments'] = []
        for filepath in attachments:
            if os.path.exists(filepath):
                filename = os.path.basename(filepath)
                mime_type, _ = mimetypes.guess_type(filepath)
                mime_type = mime_type or 'application/octet-stream'
                
                with open(filepath, 'rb') as f:
                    content = base64.b64encode(f.read()).decode()
                
                message['message']['attachments'].append({
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': filename,
                    'contentType': mime_type,
                    'contentBytes': content
                })
            else:
                print(f"Warning: Attachment not found: {filepath}", file=sys.stderr)
    
    req = Request(url, data=json.dumps(message).encode(), method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urlopen(req) as resp:
            return {'success': True, 'status': resp.status}
    except HTTPError as e:
        error_body = e.read().decode()
        return {'success': False, 'status': e.code, 'error': error_body}

def main():
    parser = argparse.ArgumentParser(description='Send email via Microsoft Graph')
    parser.add_argument('--to', required=True, help='Recipient email(s), comma-separated')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--body', required=True, help='Email body (plain text, newlines converted to <br>)')
    parser.add_argument('--attachment', action='append', dest='attachments', help='File path to attach (can repeat)')
    parser.add_argument('--cc', help='CC recipient(s), comma-separated')
    parser.add_argument('--bcc', help='BCC recipient(s), comma-separated')
    args = parser.parse_args()
    
    # Get credentials from environment
    tenant_id = os.environ.get('MS_TENANT_ID')
    client_id = os.environ.get('MS_CLIENT_ID')
    client_secret = os.environ.get('MS_CLIENT_SECRET')
    user_email = os.environ.get('MS_USER_EMAIL')
    
    if not all([tenant_id, client_id, client_secret, user_email]):
        print(json.dumps({'success': False, 'error': 'Missing environment variables'}))
        sys.exit(1)
    
    try:
        token = get_access_token(tenant_id, client_id, client_secret)
        result = send_email(
            token, user_email, 
            args.to, args.subject, args.body,
            attachments=args.attachments,
            cc=args.cc, bcc=args.bcc
        )
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
