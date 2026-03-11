"""
Gmail Integration Handler for Customer Success FTE
Handles Gmail webhook processing and email sending
"""

import uuid
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.cloud import pubsub_v1
import base64
import email
from email.mime.text import MIMEText
from datetime import datetime
from typing import Dict, Optional, List, Any
import json
import asyncio
from database.queries import db_manager, Channel


class GmailHandler:
    def __init__(self, credentials_path: str = None):
        """
        Initialize Gmail handler.
        In production, you would use proper credentials loaded from environment.
        """
        self.credentials_path = credentials_path
        self.service = None
        if credentials_path:
            self.credentials = Credentials.from_authorized_user_file(credentials_path)
            self.service = build('gmail', 'v1', credentials=self.credentials)

    async def setup_push_notifications(self, topic_name: str) -> Dict:
        """
        Set up Gmail push notifications via Pub/Sub.
        This is typically called once during initialization.
        """
        if not self.service:
            raise Exception("Gmail service not initialized")

        request = {
            'labelIds': ['INBOX'],
            'topicName': topic_name,
            'labelFilterAction': 'include'
        }
        return self.service.users().watch(userId='me', body=request).execute()

    async def process_notification(self, pubsub_message: Dict) -> List[Dict]:
        """
        Process incoming Pub/Sub notification from Gmail.
        In a real implementation, this would retrieve new messages from Gmail API.
        """
        history_id = pubsub_message.get('historyId')
        messages = []

        # In a real implementation, you would fetch the actual messages from Gmail
        # For this prototype, we'll simulate extracting message information
        # The actual Gmail API calls would be synchronous, so we'd need to handle appropriately
        for _ in range(1):  # Simulate processing one message for now
            message_data = {
                'channel': 'email',
                'channel_message_id': pubsub_message.get('messageId', 'simulated_id'),
                'customer_email': 'sender@example.com',  # Would extract from header in real impl
                'subject': 'Support Request',  # Would extract from message in real impl
                'content': 'This is a simulated email content',  # Would extract body in real impl
                'received_at': datetime.utcnow().isoformat(),
                'thread_id': pubsub_message.get('threadId', 'simulated_thread'),
                'metadata': {
                    'headers': {},
                    'labels': []
                }
            }
            messages.append(message_data)

        return messages

    async def get_message(self, message_id: str) -> Dict:
        """
        Fetch and parse a Gmail message using the Gmail API.
        """
        if not self.service:
            raise Exception("Gmail service not initialized")

        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}

        # Extract body
        body = self._extract_body(msg['payload'])

        return {
            'channel': 'email',
            'channel_message_id': message_id,
            'customer_email': self._extract_email(headers.get('From', '')),
            'subject': headers.get('Subject', ''),
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': msg.get('threadId'),
            'metadata': {
                'headers': headers,
                'labels': msg.get('labelIds', [])
            }
        }

    def _extract_body(self, payload: Dict) -> str:
        """Extract text body from email payload."""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

        return ''

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        import re
        match = re.search(r'<(.+?)>', from_header)
        return match.group(1) if match else from_header

    async def send_reply(self, to_email: str, subject: str, body: str, thread_id: str = None) -> Dict:
        """
        Send email reply via Gmail API.
        """
        if not self.service:
            raise Exception("Gmail service not initialized")

        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        send_request = {'raw': raw}
        if thread_id:
            send_request['threadId'] = thread_id

        result = self.service.users().messages().send(
            userId='me',
            body=send_request
        ).execute()

        return {
            'channel_message_id': result['id'],
            'delivery_status': 'sent',
            'thread_id': result.get('threadId')
        }

    # Simulated async methods for prototype
    async def process_webhook_payload(self, webhook_payload: Dict) -> Dict:
        """
        Process a webhook payload directly (for when using webhook mode instead of push).
        """
        # Extract headers
        headers = webhook_payload.get('headers', {})
        from_email = headers.get('From', 'unknown@example.com')
        subject = headers.get('Subject', 'No Subject')

        # Extract body
        body = webhook_payload.get('body', 'No content')

        return {
            'channel': 'email',
            'channel_message_id': webhook_payload.get('id', str(uuid.uuid4())),
            'customer_email': from_email,
            'subject': subject,
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': webhook_payload.get('threadId'),
            'metadata': {
                'headers': headers,
                'labels': webhook_payload.get('labels', [])
            }
        }