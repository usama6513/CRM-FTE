"""
Notification Service for Customer Success FTE
Handles sending ticket confirmations back to users via their respective channels
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from twilio.rest import Client
from typing import Dict, Any
from datetime import datetime
import json


class NotificationService:
    def __init__(self):
        # Initialize with environment variables
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@crm-fte.com')

    def send_confirmation_whatsapp(self, phone_number: str, ticket_id: str, query: str, user_name: str = None) -> Dict[str, Any]:
        """
        Send ticket confirmation via WhatsApp
        """
        if not phone_number.startswith('whatsapp:'):
            phone_number = f'whatsapp:{phone_number}'

        # Format the confirmation message
        message_body = f"Hello{' ' + user_name if user_name else ''}! ✅\n\n"
        message_body += f"Your support request has been received.\n\n"
        message_body += f"Ticket ID: {ticket_id}\n"
        message_body += f"Query: {query[:50]}{'...' if len(query) > 50 else ''}\n\n"
        message_body += f"Status: Open\n"
        message_body += f"Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        message_body += f"Thank you for contacting our support team! We will respond to your ticket shortly."

        if self.twilio_account_sid and self.twilio_auth_token:
            # Production mode - send actual WhatsApp message
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            message = client.messages.create(
                body=message_body,
                from_=self.twilio_whatsapp_number,
                to=phone_number
            )
            return {
                'status': 'sent',
                'channel_message_id': message.sid,
                'delivery_status': message.status,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        else:
            # Mock mode - for development
            return {
                'status': 'sent',
                'channel_message_id': f'mock_{hash(message_body)}',
                'delivery_status': 'sent',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'Mock WhatsApp message sent (development mode)'
            }

    def send_confirmation_email(self, email_address: str, ticket_id: str, query: str, subject: str = None, user_name: str = None) -> Dict[str, Any]:
        """
        Send ticket confirmation via email
        """
        # Format the email message
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = email_address
        msg['Subject'] = f"Support Ticket Confirmation - ID: {ticket_id}" if not subject else f"Re: {subject}"

        body = f"Hello{' ' + user_name if user_name else ''},\n\n"
        body += f"Your support request has been received.\n\n"
        body += f"Ticket ID: {ticket_id}\n"
        body += f"Subject: {subject or 'Support Request'}\n"
        body += f"Message: {query[:100]}{'...' if len(query) > 100 else ''}\n\n"
        body += f"Status: Open\n"
        body += f"Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        body += f"Thank you for contacting our support team! We will respond to your ticket shortly.\n\n"
        body += f"This is an automated message. Please do not reply to this email."

        msg.attach(MIMEText(body, 'plain'))

        if self.smtp_username and self.smtp_password:
            # Production mode - send actual email
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                text = msg.as_string()
                server.sendmail(self.from_email, email_address, text)
                server.quit()
                return {
                    'status': 'sent',
                    'delivery_status': 'delivered',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                return {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
        else:
            # Mock mode - for development
            return {
                'status': 'sent',
                'delivery_status': 'sent (mock)',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'Mock email sent (development mode)'
            }

    def send_confirmation_web_form(self, email_address: str, ticket_id: str, query: str, user_name: str = None, subject: str = None) -> Dict[str, Any]:
        """
        Send ticket confirmation for web form submission
        """
        return self.send_confirmation_email(email_address, ticket_id, query, subject, user_name)