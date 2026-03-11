# Escalation Rules

## When to Escalate to Human Agent

### Automatic Escalations (Always Escalate)
1. **Pricing Inquiries**
   - Any mention of "price", "pricing", "cost", "discount", "deal", "negotiation"
   - Requests for custom pricing or enterprise quotes

2. **Billing Issues**
   - Refund requests
   - Billing errors or discrepancies
   - Payment processing problems
   - Subscription changes or cancellations

3. **Legal/Compliance Concerns**
   - Any mention of "lawyer", "legal", "compliance", "audit", "subpoena", "court", "sue", "lawsuit"
   - Regulatory compliance questions beyond standard security certifications

4. **Technical Escalations**
   - API keys or authentication issues persisting beyond 2 attempts
   - Data loss reports
   - Security concerns or breach suspicions
   - System outages affecting multiple customers

5. **Customer Sentiment**
   - Negative sentiment score below 0.3
   - Use of profanity or aggressive language
   - Explicit requests for human support
   - Expressions of frustration or anger

### Conditional Escalations (Based on Context)
1. **Complex Integrations**
   - Custom development requests beyond standard API usage
   - Complex data migration needs
   - Third-party integration failures

2. **High-Value Accounts**
   - Enterprise customers (annual contract >$10,000)
   - Strategic partnership accounts
   - Long-standing customers with >2 years tenure

3. **Escalation History**
   - Customer whose issue was escalated previously
   - Accounts with multiple unresolved tickets in 30 days

## Escalation Process

1. **Immediate Actions**
   - Log escalation in system with reason
   - Notify customer that their issue is being escalated
   - Provide estimated response time from human agent

2. **Information Handoff**
   - Complete conversation history
   - Customer details and account status
   - Previous resolution attempts
   - Urgency level

3. **Follow-up**
   - Monitor for resolution within 4 hours
   - Send follow-up to customer if not resolved
   - Escalate further if needed

## Communication During Escalation

### Email Channel
"Thank you for contacting TechCorp Support. Your issue requires specialized attention from our human support team. A support specialist will contact you within 2-4 hours. Your ticket ID is [TICKET_ID] and reference number is [REF_NUM]."

### WhatsApp Channel
"Thanks for reaching out! Your issue needs expert attention. A human agent will contact you via your email within 2-4 hours. Ref: [TICKET_ID]"

### Web Form Channel
"Your request has been escalated to our human support team. You'll receive an email response within 2-4 hours. Reference: [TICKET_ID]. You can also check status using your ticket ID at [support portal link]."

## Escalation Categories and Priorities

### Urgent (Within 1 hour)
- Data loss reports
- Security concerns
- System outages affecting business operations
- Legal issues

### High (Within 4 hours)
- Billing disputes
- Pricing inquiries
- Refund requests
- Customer with negative sentiment

### Standard (Within 24 hours)
- Complex technical issues
- Integration problems
- Feature requests
- Account access issues