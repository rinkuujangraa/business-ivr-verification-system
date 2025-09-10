# Professional Business IVR System for Twilio

An enterprise-grade Interactive Voice Response (IVR) system for customer identity verification and business communication services, designed for Twilio account access and compliance.

## Features

- **Voice Verification**: Interactive voice prompts for customer identity verification
- **SMS Integration**: Automated verification code delivery via SMS
- **Call Routing**: Professional call management and routing capabilities
- **Customer Support**: Integration points for customer service representatives
- **Compliance Ready**: Built with Twilio's terms of service in mind

## Use Case

This IVR service is designed for businesses that need:
- Automated customer identity verification
- Professional phone system integration
- Secure verification code delivery
- Streamlined customer support processes

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the `twilioshowcase` directory with your Twilio credentials:

```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number
BUSINESS_NAME=Your Business Name Here
PORT=5000
```

### 2. Install Dependencies

```bash
cd twilioshowcase
pip install -r requirements.txt
```

### 3. Run the Bot

```bash
python simple.py
```

The bot will start on `http://localhost:5000`

### 4. Configure Twilio Webhooks

In your Twilio Console, configure the following webhooks for your phone number:

- **Voice URL**: `https://your-domain.com/incoming-call`
- **SMS URL**: `https://your-domain.com/incoming-sms`

## API Endpoints

- `POST /incoming-call` - Handle incoming voice calls
- `POST /handle_verification_choice` - Process user verification choice
- `POST /verify_code` - Verify entered verification code
- `POST /incoming-sms` - Handle incoming SMS messages
- `GET /health` - Health check endpoint

## How It Works

1. **Incoming Call**: Customer calls your Twilio number
2. **Voice Prompts**: Bot provides options for verification
3. **SMS Verification**: Customer can request verification code via SMS
4. **Code Verification**: Customer enters code to complete verification
5. **Support Option**: Alternative path to customer service

## Compliance Features

- **Transactional SMS Only**: No marketing messages sent
- **User-Initiated**: All communications are user-initiated
- **Secure Verification**: Temporary code storage with cleanup
- **Professional Voice**: Clear, professional voice prompts

## Development Notes

- Built with Flask for easy deployment
- Uses Twilio's TwiML for voice responses
- Includes comprehensive logging
- Health check endpoint for monitoring
- Error handling for failed SMS delivery

## Deployment

This bot is ready for deployment on various platforms:
- Heroku
- AWS
- Google Cloud
- DigitalOcean
- Any platform supporting Python/Flask

## Support

For questions about this implementation, refer to:
- Twilio Documentation
- Flask Documentation
- Your Twilio account dashboard
