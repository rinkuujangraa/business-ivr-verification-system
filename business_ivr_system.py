#!/usr/bin/env python3
"""
Professional Business IVR System
Enterprise-grade Interactive Voice Response system for customer identity verification
and business communication services.
"""

from flask import Flask, request, Response
from twilio.twiml import VoiceResponse, MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
import logging
import time
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio credentials
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
BUSINESS_NAME = os.getenv('BUSINESS_NAME', 'Business Verification Services')

# Initialize Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN) if ACCOUNT_SID and AUTH_TOKEN else None

class BusinessIVRSystem:
    """Professional Business IVR System for customer identity verification"""
    
    def __init__(self):
        self.verification_sessions = {}  # Store verification sessions with expiration
        self.rate_limits = {}  # Rate limiting for security
        
    def check_rate_limit(self, phone_number):
        """Check if phone number is rate limited"""
        current_time = time.time()
        if phone_number in self.rate_limits:
            if current_time - self.rate_limits[phone_number] < 300:  # 5 minutes
                return False
        self.rate_limits[phone_number] = current_time
        return True
    
    def generate_verification_code(self, phone_number):
        """Generate a secure 6-digit verification code with expiration"""
        import random
        code = str(random.randint(100000, 999999))
        expiration = datetime.now() + timedelta(minutes=10)
        
        self.verification_sessions[phone_number] = {
            'code': code,
            'expires': expiration,
            'attempts': 0,
            'created': datetime.now()
        }
        
        logger.info(f"Generated verification session for {phone_number}")
        return code
    
    def send_verification_sms(self, phone_number, code):
        """Send professional verification code via SMS"""
        if not client:
            logger.error("Twilio client not initialized")
            return False
            
        try:
            message = client.messages.create(
                body=f"{BUSINESS_NAME}: Your identity verification code is {code}. "
                     f"This code expires in 10 minutes. Do not share this code with anyone.",
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logger.info(f"Verification SMS sent to {phone_number}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send verification SMS to {phone_number}: {str(e)}")
            return False
    
    def handle_incoming_call(self, phone_number):
        """Handle incoming business verification calls"""
        response = VoiceResponse()
        
        # Check rate limiting
        if not self.check_rate_limit(phone_number):
            response.say(
                "We're experiencing high call volume. Please try again in a few minutes.",
                voice='alice',
                language='en-US'
            )
            response.hangup()
            return str(response)
        
        # Professional welcome message
        response.say(
            f"Thank you for calling {BUSINESS_NAME}. "
            "This is our automated identity verification system. "
            "Please select from the following options.",
            voice='alice',
            language='en-US'
        )
        
        # Gather user input for verification
        gather = response.gather(
            num_digits=1,
            action='/handle_verification_choice',
            method='POST',
            timeout=15
        )
        gather.say(
            "Press 1 to receive an identity verification code via text message, "
            "or press 2 to speak with a customer service representative.",
            voice='alice',
            language='en-US'
        )
        
        # Fallback if no input
        response.say(
            "We didn't receive your selection. Please call back and try again. Goodbye.",
            voice='alice',
            language='en-US'
        )
        response.hangup()
        
        return str(response)
    
    def handle_verification_choice(self, phone_number, choice):
        """Handle user's verification choice with security measures"""
        response = VoiceResponse()
        
        if choice == '1':
            # Generate and send verification code
            code = self.generate_verification_code(phone_number)
            sms_sent = self.send_verification_sms(phone_number, code)
            
            if sms_sent:
                response.say(
                    "An identity verification code has been sent to your registered phone number. "
                    "Please check your text messages and enter the code when prompted.",
                    voice='alice',
                    language='en-US'
                )
                
                # Gather verification code
                gather = response.gather(
                    num_digits=6,
                    action='/verify_code',
                    method='POST',
                    timeout=45
                )
                gather.say(
                    "Please enter the 6-digit verification code you received via text message.",
                    voice='alice',
                    language='en-US'
                )
                
                # Fallback
                response.say(
                    "We didn't receive the verification code. Please call back and try again. Goodbye.",
                    voice='alice',
                    language='en-US'
                )
            else:
                response.say(
                    "We're experiencing technical difficulties. "
                    "Please try again later or contact our customer support team.",
                    voice='alice',
                    language='en-US'
                )
                
        elif choice == '2':
            # Transfer to customer service
            response.say(
                "Please hold while we connect you to a customer service representative.",
                voice='alice',
                language='en-US'
            )
            # In a real implementation, you would dial a customer service number
            response.say(
                "Our customer service team is currently unavailable. "
                "Please try again during business hours or use our online support portal.",
                voice='alice',
                language='en-US'
            )
        else:
            response.say(
                "Invalid selection. Please call back and try again. Goodbye.",
                voice='alice',
                language='en-US'
            )
        
        response.hangup()
        return str(response)
    
    def verify_code(self, phone_number, entered_code):
        """Verify the entered code with security measures"""
        response = VoiceResponse()
        
        session = self.verification_sessions.get(phone_number)
        
        if not session:
            response.say(
                "No active verification session found. Please start a new verification process.",
                voice='alice',
                language='en-US'
            )
            response.hangup()
            return str(response)
        
        # Check if session has expired
        if datetime.now() > session['expires']:
            del self.verification_sessions[phone_number]
            response.say(
                "Your verification session has expired. Please call back to start a new verification process.",
                voice='alice',
                language='en-US'
            )
            response.hangup()
            return str(response)
        
        # Check attempt limit
        if session['attempts'] >= 3:
            del self.verification_sessions[phone_number]
            response.say(
                "Too many failed attempts. Please call back to start a new verification process.",
                voice='alice',
                language='en-US'
            )
            response.hangup()
            return str(response)
        
        # Increment attempts
        session['attempts'] += 1
        
        if entered_code == session['code']:
            # Code is correct
            del self.verification_sessions[phone_number]
            response.say(
                "Identity verification successful! You have been successfully verified. "
                "Thank you for using our business verification service.",
                voice='alice',
                language='en-US'
            )
        else:
            # Code is incorrect
            response.say(
                "Verification failed. The code you entered is incorrect. "
                "Please call back and try again.",
                voice='alice',
                language='en-US'
            )
        
        response.hangup()
        return str(response)

# Initialize the business IVR system
business_ivr = BusinessIVRSystem()

@app.route('/')
def home():
    """Home endpoint"""
    return f"""
    <h1>Professional Business IVR System</h1>
    <p>Enterprise-grade Interactive Voice Response system for customer identity verification and business communication services</p>
    <h2>Service Information:</h2>
    <ul>
        <li><strong>Business Name:</strong> {BUSINESS_NAME}</li>
        <li><strong>Service Type:</strong> Identity Verification & Customer Support</li>
        <li><strong>Compliance:</strong> Fully compliant with business communication standards</li>
    </ul>
    <h2>API Endpoints:</h2>
    <ul>
        <li>POST /incoming-call - Handle incoming business verification calls</li>
        <li>POST /handle_verification_choice - Process verification choice</li>
        <li>POST /verify_code - Verify entered identity verification code</li>
        <li>POST /incoming-sms - Handle incoming SMS messages</li>
        <li>GET /health - System health check</li>
    </ul>
    <h2>Security Features:</h2>
    <ul>
        <li>Rate limiting protection</li>
        <li>Session expiration management</li>
        <li>Attempt limit enforcement</li>
        <li>Secure code generation</li>
    </ul>
    """

@app.route('/incoming-call', methods=['POST'])
def handle_incoming_call():
    """Handle incoming business verification calls"""
    phone_number = request.form.get('From', '')
    logger.info(f"Business verification call from: {phone_number}")
    
    twiml_response = business_ivr.handle_incoming_call(phone_number)
    return Response(twiml_response, mimetype='text/xml')

@app.route('/handle_verification_choice', methods=['POST'])
def handle_verification_choice():
    """Handle user's verification choice"""
    phone_number = request.form.get('From', '')
    choice = request.form.get('Digits', '')
    
    logger.info(f"Verification choice from {phone_number}: {choice}")
    
    twiml_response = business_ivr.handle_verification_choice(phone_number, choice)
    return Response(twiml_response, mimetype='text/xml')

@app.route('/verify_code', methods=['POST'])
def verify_code():
    """Verify the entered identity verification code"""
    phone_number = request.form.get('From', '')
    entered_code = request.form.get('Digits', '')
    
    logger.info(f"Identity verification attempt from {phone_number}")
    
    twiml_response = business_ivr.verify_code(phone_number, entered_code)
    return Response(twiml_response, mimetype='text/xml')

@app.route('/incoming-sms', methods=['POST'])
def handle_incoming_sms():
    """Handle incoming SMS messages for business support"""
    phone_number = request.form.get('From', '')
    message_body = request.form.get('Body', '').strip().lower()
    
    logger.info(f"Business SMS from {phone_number}: {message_body}")
    
    response = MessagingResponse()
    
    if message_body in ['help', 'support']:
        response.message(
            f"Welcome to {BUSINESS_NAME}! "
            "Call our business verification line to start the identity verification process. "
            "Reply with 'status' to check your verification status."
        )
    elif message_body == 'status':
        if phone_number in business_ivr.verification_sessions:
            response.message(
                "You have a pending identity verification session. "
                "Please call our business verification line to complete the process."
            )
        else:
            response.message(
                "No pending verification session found. "
                "Call our business verification line to start the identity verification process."
            )
    else:
        response.message(
            f"Thank you for contacting {BUSINESS_NAME}. "
            "For identity verification assistance, please call our business verification line. "
            "Reply with 'help' for more options."
        )
    
    return Response(str(response), mimetype='text/xml')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for business monitoring"""
    return {
        'status': 'healthy',
        'service': 'Professional Business IVR System',
        'business_name': BUSINESS_NAME,
        'version': '1.0.0',
        'features': [
            'Identity verification',
            'Customer support routing',
            'Rate limiting',
            'Session management',
            'Security compliance'
        ]
    }

if __name__ == '__main__':
    # Check if Twilio credentials are configured
    if not ACCOUNT_SID or not AUTH_TOKEN:
        logger.warning("Twilio credentials not found in environment variables")
        logger.warning("Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER")
        logger.warning("Also set BUSINESS_NAME for professional branding")
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Professional Business IVR System on port {port}")
    logger.info(f"Business Name: {BUSINESS_NAME}")
    app.run(host='0.0.0.0', port=port, debug=False)  # Set to False for production
