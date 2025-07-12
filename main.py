import os
import json
import logging
import threading
import time
from flask import Flask, request, jsonify
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

# Environment variables
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SELF_URL = os.getenv('SELF_URL')

# Google Gemini setup
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# School information and AI Assistant instructions
SCHOOL_INFO = """
You are the official AI Assistant of AL-GHAZALI HIGH SCHOOL. Your role is to assist parents by answering their school-related queries in a helpful, polite, and informative manner. You must always provide accurate, up-to-date, and school-appropriate information. Never provide personal opinions or unrelated information.

📍 School Details:
- School Name: AL-GHAZALI HIGH SCHOOL
- Address: 41/25-28, Area 36-B, Landhi Karachi 75160 Pakistan 
- Contact Number: +92-313-2317606
- Email: rk8466995@gmail.com
- Website: https://mahadusman.com
- Timings: 8:00 AM to 2:10 PM (Saturday to Thursday)
- Principal: Dr. Zakariya

💳 Fee Structure:
- Monthly Tuition Fee: Varies by class. Check with the school directly & visit our website and the fees is follow.
    - Level-1: 1000
    - Level-2: 2000
    - Level-3: 3000
    - Level-4: 4000
    - Level-5: 5000
    - Level-6: 6000
    - SSC-1: 7000
    - SSC-2: 8000
- Admission Fee: Rs. 4000 (new) / Rs. 2500 (old)

🧠 Language Instruction:
- If the parent writes in **English**, respond only in **English**.
- If the parent writes in **Urdu script**, respond only in **Urdu script**.
- If the parent writes in **Roman Urdu**, respond only in **Roman Urdu**.
- Never mix languages in a single message.

📌 Important Guidelines:
- Handle only **school-related** questions (e.g. admissions, timings, fees, holidays).
- Always maintain a **polite, professional, and friendly** tone.
- If unsure, respond:
  - Urdu: "معذرت، براہ کرم اسکول آفس سے رابطہ کریں۔"
  - English: "Sorry, please contact the school office for more information."
"""

class WhatsAppAIAgent:
    def __init__(self):
        self.conversation_history = {}

    def get_gemini_response(self, user_message, phone_number):
        try:
            if phone_number not in self.conversation_history:
                self.conversation_history[phone_number] = []

            detected_lang = self.detect_language(user_message)
            if detected_lang == 'english':
                lang_instruction = "Reply ONLY in English."
            elif detected_lang == 'urdu_script':
                lang_instruction = "Reply ONLY in Urdu script."
            else:
                lang_instruction = "Reply ONLY in Roman Urdu."

            prompt = f"""
            {SCHOOL_INFO}

            Previous conversation:
            {self.get_conversation_context(phone_number)}

            Parent's Question: {user_message}

            {lang_instruction}
            """

            response = model.generate_content(prompt)
            ai_response = response.text

            self.conversation_history[phone_number].append({
                'user': user_message,
                'ai': ai_response
            })

            if len(self.conversation_history[phone_number]) > 5:
                self.conversation_history[phone_number] = self.conversation_history[phone_number][-5:]

            return ai_response

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return "Technical issue. Please try again later."

    def get_conversation_context(self, phone_number):
        if phone_number not in self.conversation_history:
            return "This is the first message."
        context = ""
        for conv in self.conversation_history[phone_number][-3:]:
            context += f"Parent: {conv['user']}\nAI: {conv['ai']}\n\n"
        return context or "This is the first message."

    def detect_language(self, text):
        for char in text:
            if '\u0600' <= char <= '\u06FF':
                return 'urdu_script'
        english_words = set(['the', 'is', 'are', 'to', 'for', 'with', 'and'])
        words = text.lower().split()
        english_count = sum(1 for w in words if w in english_words)
        if len(words) > 0 and english_count / len(words) > 0.5:
            return 'english'
        return 'roman_urdu'

ai_agent = WhatsAppAIAgent()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully.")
            return challenge, 200
        else:
            logger.warning("Webhook verification failed.")
            return 'Verification token mismatch', 403

    elif request.method == 'POST':
        try:
            data = request.json
            entry = data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            messages = value.get('messages')

            if messages:
                msg = messages[0]
                text = msg['text']['body']
                from_number = msg['from']

                logger.info(f"Received from {from_number}: {text}")
                reply = ai_agent.get_gemini_response(text, from_number)

                url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
                headers = {
                    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "messaging_product": "whatsapp",
                    "to": from_number,
                    "type": "text",
                    "text": {"body": reply}
                }
                res = requests.post(url, headers=headers, json=payload)
                logger.info(f"Message sent to {from_number}, status: {res.status_code}")

            return jsonify(status="success"), 200

        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return jsonify(error=str(e)), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify(status="healthy")

# Self-ping thread to prevent sleep
def keep_alive():
    if not SELF_URL:
        logger.warning("SELF_URL not set. Skipping keep-alive pinger.")
        return
    while True:
        try:
            logger.info("Sending keep-alive ping to /health")
            res = requests.get(f"{SELF_URL}/health")
            logger.info(f"Keep-alive response: {res.status_code}")
        except Exception as e:
            logger.error(f"Keep-alive ping failed: {e}")
        time.sleep(300)

if __name__ == '__main__':
    port_env = os.getenv('PORT')
    port = int(port_env) if port_env and port_env.isdigit() else 5000

    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=port, debug=True)
