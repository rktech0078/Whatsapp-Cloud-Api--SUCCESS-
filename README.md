# WhatsApp Cloud API AI Assistant 🤖

This project is an AI-powered WhatsApp assistant for **AL-GHAZALI HIGH SCHOOL**. It uses Google Gemini (via the Generative AI API) to answer parents' school-related queries in English, Urdu script, or Roman Urdu, and is deployed as a Flask web server with WhatsApp Cloud API integration.

---

## 🚀 Features
- **AI Assistant**: Answers school-related questions (admissions, timings, fees, holidays, etc.)
- **Multilingual**: Detects and responds in English, Urdu script, or Roman Urdu
- **WhatsApp Integration**: Sends and receives messages via WhatsApp Cloud API
- **Self-pinging**: Keeps the server alive on free hosting platforms
- **Customizable**: Easily update school info and instructions

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/rktech0078/Whatsapp-Cloud-Api--SUCCESS-
cd Whatsapp-Cloud-Api--SUCCESS-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root with the following variables:

```env
WHATSAPP_TOKEN=your_whatsapp_cloud_api_token
PHONE_NUMBER_ID=your_whatsapp_phone_number_id
VERIFY_TOKEN=your_webhook_verify_token
GOOGLE_API_KEY=your_google_gemini_api_key
SELF_URL=https://your-deployed-app-url (optional, for keep-alive)
PORT=5000 (optional)
```

### 4. Run the Server
```bash
python main.py
```

The server will start on `http://0.0.0.0:5000` by default.

---

## 📲 WhatsApp Webhook Setup
1. Deploy your server (e.g., on [Render](https://render.com/), [Railway](https://railway.app/), [Heroku](https://heroku.com/), or your own VPS).
2. Set your webhook URL in the [Meta for Developers Console](https://developers.facebook.com/).
3. Use the `/webhook` endpoint for verification and message delivery.

---

## 🧪 API Endpoints

- `GET /webhook` – Webhook verification (Meta)
- `POST /webhook` – Receives WhatsApp messages
- `GET /health` – Health check (used for keep-alive)

---

## 📝 Example Interactions

| Parent Message                | AI Response (Language)         |
|------------------------------|--------------------------------|
| What are the school timings?  | 8:00 AM to 2:10 PM... (English)|
| اسکول کی فیس کیا ہے؟         | ... (Urdu script)              |
| admission ka process kya hai? | ... (Roman Urdu)               |

---

## 🏫 School Info (Default)
- **Name:** AL-GHAZALI HIGH SCHOOL
- **Address:** 41/25-28, Area 36-B, Landhi Karachi 75160 Pakistan
- **Contact:** +92-313-2317606
- **Email:** rk8466995@gmail.com
- **Website:** https://mahadusman.com
- **Timings:** 8:00 AM to 2:10 PM (Sat–Thu)
- **Principal:** Dr. Zakariya

---

## ⚙️ Customization
- Update school info and instructions in the `SCHOOL_INFO` variable in `main.py`.
- Adjust language detection or AI prompt logic in the `WhatsAppAIAgent` class.

---

## 🛡️ Security & Notes
- **Never share your API keys or tokens publicly.**
- For production, set `debug=False` in `main.py`.
- Use HTTPS for webhook endpoints in production.

---

## 🙋 FAQ
- **Q:** Can I use this for another school?  
  **A:** Yes! Just update the `SCHOOL_INFO` and environment variables.
- **Q:** Does it support group chats?  
  **A:** This is designed for 1:1 parent-school communication.
- **Q:** How do I change the AI model?  
  **A:** Update the `model = genai.GenerativeModel(...)` line in `main.py`.

---

## 📧 Contact
For help or questions, contact the school at [rk8466995@gmail.com](mailto:rk8466995@gmail.com) or open an issue in this repository.

---

## ⭐ Star this project if you found it useful! 