"""
WhatsApp Integration Handler for Customer Success FTE
Handles Twilio webhook processing and message sending
"""

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from fastapi import Request, HTTPException
import os
from datetime import datetime
from typing import Dict, List
import json
from database.queries import db_manager, Channel


class WhatsAppHandler:
    def __init__(self):
        """
        Initialize WhatsApp handler with Twilio credentials.
        In production, these would be loaded from environment variables.
        """
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')  # e.g., 'whatsapp:+14155238886'

        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            # For prototype, use mock values
            self.account_sid = 'mock_account_sid'
            self.auth_token = 'mock_auth_token'
            self.whatsapp_number = 'whatsapp:+1234567890'
            self.client = None  # Will be None in prototype mode
        else:
            self.client = Client(self.account_sid, self.auth_token)

        self.validator = RequestValidator(self.auth_token) if self.auth_token != 'mock_auth_token' else None

    async def validate_webhook(self, request: Request) -> bool:
        """
        Validate incoming Twilio webhook signature.
        In production, this would be called to ensure requests are from Twilio.
        """
        if not self.validator:
            # In prototype mode, always return True
            return True

        signature = request.headers.get('X-Twilio-Signature', '')
        url = str(request.url)
        form_data = await request.form()
        params = dict(form_data)

        return self.validator.validate(url, params, signature)

    async def process_webhook(self, form_data: Dict) -> Dict:
        """
        Process incoming WhatsApp message from Twilio webhook.
        """
        return {
            'channel': 'whatsapp',
            'channel_message_id': form_data.get('MessageSid'),
            'customer_phone': form_data.get('From', '').replace('whatsapp:', ''),
            'content': form_data.get('Body', ''),
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'num_media': form_data.get('NumMedia', '0'),
                'profile_name': form_data.get('ProfileName'),
                'wa_id': form_data.get('WaId'),
                'status': form_data.get('SmsStatus')
            }
        }

    async def send_message(self, to_phone: str, body: str) -> Dict:
        """
        Send WhatsApp message via Twilio.
        """
        if not to_phone.startswith('whatsapp:'):
            to_phone = f'whatsapp:{to_phone}'

        if self.client:
            # Real implementation
            message = self.client.messages.create(
                body=body,
                from_=self.whatsapp_number,
                to=to_phone
            )

            return {
                'channel_message_id': message.sid,
                'delivery_status': message.status  # 'queued', 'sent', 'delivered', 'failed'
            }
        else:
            # Prototype implementation
            return {
                'channel_message_id': f'mock_{hash(body)}',
                'delivery_status': 'sent'  # Always 'sent' in mock mode
            }

    def format_response(self, response: str, max_length: int = 1600) -> List[str]:
        """
        Format and split response for WhatsApp (max 1600 chars per message).
        """
        if len(response) <= max_length:
            return [response]

        # Split into multiple messages
        messages = []
        while response:
            if len(response) <= max_length:
                messages.append(response)
                break

            # Find a good break point
            break_point = response.rfind('. ', 0, max_length)
            if break_point == -1:
                break_point = response.rfind(' ', 0, max_length)
            if break_point == -1:
                break_point = max_length

            messages.append(response[:break_point + 1].strip())
            response = response[break_point + 1:].strip()

        return messages

    async def send_formatted_message(self, to_phone: str, body: str) -> List[Dict]:
        """
        Send a message that may need to be split into multiple parts for WhatsApp.
        """
        formatted_messages = self.format_response(body)
        results = []

        for msg in formatted_messages:
            result = await self.send_message(to_phone, msg)
            results.append(result)

        return results

    async def process_status_callback(self, form_data: Dict) -> Dict:
        """
        Process WhatsApp message status updates (delivered, read, etc.).
        """
        return {
            'channel_message_id': form_data.get('MessageSid'),
            'status': form_data.get('MessageStatus'),
            'timestamp': datetime.utcnow().isoformat()
        }