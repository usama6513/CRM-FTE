# Running the Customer Success FTE System

## Overview
The Customer Success FTE (Full-Time Equivalent) system is a complete AI-powered customer support solution that handles multi-channel communication (Email, WhatsApp, Web Form) with 24/7 availability.

## System Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MULTI-CHANNEL INTAKE ARCHITECTURE                        │
│                                                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│   │    Gmail     │    │   WhatsApp   │    │   Web Form   │                 │
│   │   (Email)    │    │  (Messaging) │    │  (Website)   │                 │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                 │
│          │                   │                   │                          │
│          ▼                   ▼                   ▼                          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│   │ Gmail API /  │    │   Twilio     │    │   FastAPI    │                 │
│   │   Webhook    │    │   Webhook    │    │   Endpoint   │                 │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                 │
│          │                   │                   │                          │
│          └───────────────────┼───────────────────┘                          │
│                              ▼                                               │
│                    ┌─────────────────┐                                      │
│                    │  Unified Ticket │                                      │
│                    │    Ingestion    │                                      │
│                    │     (Kafka)     │                                      │
│                    └────────┬────────┘                                      │
│                             │                                                │
│                             ▼                                                │
│                    ┌─────────────────┐                                      │
│                    │   Customer      │                                      │
│                    │   Success FTE   │                                      │
│                    │    (Agent)      │                                      │
│                    └────────┬────────┘                                      │
│                             │                                                │
│              ┌──────────────┼──────────────┐                                │
│              ▼              ▼              ▼                                 │
│         Reply via      Reply via     Reply via                              │
│          Email         WhatsApp       Web/API                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## How to Run the Complete System

### Method 1: Using the Complete System Script (Recommended)
```bash
cd D:\hackatho-5
python start_full_system.py
```

This script will:
- Start the Multi-Channel UI Server on port 8082
- Start the AI Message Processor
- Open the browser to the main dashboard
- Monitor both services and restart them if they crash

### Method 2: Manual Startup
```bash
# Terminal 1: Start the UI server
python run_project_full.py

# Terminal 2: Start the message processor
python -m src.workers.message_processor
```

## System Access Points

Once the system is running, access these URLs:

- **Main Dashboard**: [http://localhost:8082/](http://localhost:8082/)
- **WhatsApp Interface**: [http://localhost:8082/whatsapp.html](http://localhost:8082/whatsapp.html)
- **WhatsApp-Style Interface**: [http://localhost:8082/whatsapp-style.html](http://localhost:8082/whatsapp-style.html)
- **Email Interface**: [http://localhost:8082/email.html](http://localhost:8082/email.html)
- **Web Form**: [http://localhost:8082/web_form.html](http://localhost:8082/web_form.html)
- **API Health Check**: [http://localhost:8082/health](http://localhost:8082/health)

## Channel-Specific Endpoints

The system provides the following API endpoints:

- **POST /api/whatsapp/send** - Process WhatsApp messages
- **POST /api/email/send** - Process email messages
- **POST /api/web-form/submit** - Process web form submissions
- **POST /api/support/submit** - Legacy web form endpoint
- **GET /conversations/{conversation_id}** - Get conversation history
- **GET /customers/lookup?email={email}** - Look up customer

## Features

✅ **Multi-Channel Support**: Seamless experience across Email, WhatsApp, and Web Form
✅ **AI-Powered Agent**: 24/7 customer success agent with OpenAI integration
✅ **Channel Awareness**: Adapts communication style based on channel
✅ **Real-time Interface**: Interactive dashboards for each channel
✅ **Sentiment Analysis**: Detects negative sentiment and escalates appropriately
✅ **Knowledge Base Integration**: Semantic search of product documentation
✅ **Customer Context**: Unified profiles and conversation history across channels
✅ **Escalation Logic**: Automatic escalation for complex issues
✅ **Enterprise Security**: Proper authentication, validation, and access controls
✅ **Monitoring**: Channel-specific metrics and performance tracking

## System Verification

To verify the system is working properly, run:
```bash
python system_verification.py
```

This will test all channels and endpoints to ensure complete functionality.

## Stopping the System

Press **Ctrl+C** in the terminal where `start_full_system.py` is running to gracefully shut down all services.

## Production Considerations

For production deployment:
- Set up proper environment variables (OPENAI_API_KEY, database credentials, etc.)
- Configure Kafka cluster for message streaming
- Set up PostgreSQL with pgvector extension
- Configure SSL/TLS for secure communication
- Set up monitoring and logging infrastructure
- Configure auto-scaling policies

## Troubleshooting

If services fail to start:
1. Check that no other processes are using ports 8082
2. Verify that all dependencies are installed (`pip install -r requirements.txt`)
3. Ensure environment variables are properly set
4. Check the console output for specific error messages