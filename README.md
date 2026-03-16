# Customer Success FTE - Multi-Channel Support System

A comprehensive customer support platform that integrates multiple communication channels (WhatsApp, Email, Web Form) with AI-powered assistance and ticket tracking capabilities.

## Features

- **Multi-Channel Support**: Handle customer queries via WhatsApp, Email, and Web Form from a single dashboard
- **AI-Powered Customer Success Agent**: Intelligent responses using OpenAI API
- **Real-Time Interface**: Event-driven architecture with message streaming
- **QR Code Ticket Tracking**: Visual identification for support tickets
- **Channel-Specific Notifications**: Automatic confirmation messages sent back to users via their original channel (WhatsApp, Email)
- **AI Customer Success Agent**: Intelligent responses using OpenAI API that processes queries and sends responses back to users
- **Dark Theme UI**: Modern interface with navy blue theme and colored channel indicators
- **Professional Dashboard**: Analytics and activity tracking for support teams
- **Ticket Management System**: Track and manage customer support tickets with status updates

## Channels

1. **WhatsApp Support**: Instant messaging with customers through WhatsApp integration
2. **Email Support**: Handle customer emails with intelligent routing
3. **Web Form**: Website contact form integration for customer inquiries

## Technical Architecture

- **Backend**: Python Flask server with event-driven API endpoints
- **Frontend**: HTML/CSS/JavaScript with dark-themed UI components
- **Data Validation**: Pydantic models for structured data handling
- **Message Processing**: Channel-aware communication with different response styles
- **Deployment Ready**: Configured for Heroku/DigitalOcean deployment

## Requirements

- Python 3.11+
- OpenAI API key (for AI functionality)
- Node.js (for development)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (for development, the system uses mock API keys):
   - `OPENAI_API_KEY`: Your OpenAI API key (for AI functionality)
   - `TWILIO_ACCOUNT_SID`: Your Twilio account SID (for WhatsApp notifications)
   - `TWILIO_AUTH_TOKEN`: Your Twilio auth token
   - `TWILIO_WHATSAPP_NUMBER`: Your Twilio WhatsApp number (format: whatsapp:+14155238886)
   - `SMTP_USERNAME`: Your email service username (for email notifications)
   - `SMTP_PASSWORD`: Your email service password
   - `FROM_EMAIL`: Sender email address
4. Run the server:
   ```bash
   python fixed_server.py
   ```

## Usage

1. Access the dashboard at `http://localhost:8082/`
2. Select a channel (WhatsApp, Email, or Web Form) to handle customer queries
3. Use the respective interface to send/receive messages
4. Track tickets with QR codes and dashboard analytics

## API Endpoints

- `POST /api/whatsapp/send` - Send WhatsApp message, receive ticket confirmation and AI response
- `POST /api/email/send` - Send email message, receive ticket confirmation and AI response
- `POST /api/web-form/submit` - Submit web form, receive ticket confirmation and AI response
- `GET /api/ticket/{ticket_id}` - Retrieve ticket status and information
- `GET /api/agent/test` - Test the AI customer success agent

## Deployment

The application is ready for deployment on Heroku, DigitalOcean, or similar platforms with Procfile configuration included.

## Files Structure

- `fixed_server.py` - Main server application
- `src/api/ui/unified_support.html` - Main dashboard UI
- `src/agent/customer_success_agent.py` - AI agent implementation
- `src/notifications/notification_service.py` - Channel-specific notification system
- `src/tickets/ticket_storage.py` - Ticket management system
- `Procfile` - Deployment configuration
- `requirements.txt` - Python dependencies

## Security

- API keys are handled securely with fallbacks for development
- Sensitive files are excluded via `.gitignore`
- Input validation with Pydantic models

## License

This project is created for the CRM Digital FTE Factory Final Hackathon.