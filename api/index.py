import os
import re
import requests
from flask import Flask, request
from deep_translator import GoogleTranslator

BOT_TOKEN = "8621084667:AAGrNfeOwpl1H-6PYho3o6r2vICv2Mg4dLM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"].strip()

            if text == "/start":
                welcome_text = (
                    "👋 Hello! I am your Multi-Language Link Bypasser Bot.\n"
                    "Send me any short link, and I will get the original link for you!\n\n"
                    "👋 ආයුබෝවන්! මම ඕනෑම භාෂාවකින් වැඩ කරන Link Bypasser Bot කෙනෙක්.\n"
                    "ඔයාගේ Short Link එක මට එවන්න!"
                )
                send_message(chat_id, welcome_text)

            elif "http" in text:
                url_match = re.search(r'https?://[^\s]+', text)
                if not url_match:
                    send_message(chat_id, "⚠️ Please send a valid URL / කරුණාකර නිවැරදි Link එකක් එවන්න.")
                    return "ok", 200

                target_url = url_match.group(0)

                try:
                    detected_lang = GoogleTranslator(source='auto', target='en').detect(text)
                except:
                    detected_lang = 'en'

                send_message(chat_id, "⏳ Bypassing link... Please wait / පොඩ්ඩක් ඉන්න...")

                try:
                    # Redirects අනුගමනය කරමින් අවසාන Link එක ලබාගැනීම
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    response = requests.get(target_url, headers=headers, allow_redirects=True, timeout=15)
                    
                    final_url = response.url

                    if final_url and final_url != target_url:
                        reply_text = f"✅ **Original Link:**\n`{final_url}`"
                        send_message(chat_id, reply_text)
                    else:
                        error_msg = "❌ Could not bypass this link directly. It may require a captcha or token."
                        if detected_lang == 'si':
                            error_msg = "❌ මේ Link එක කෙලින්ම Bypass කරන්න බැහැ (Captcha එකක් හෝ Token එකක් අවශ්‍ය විය හැක)."
                        send_message(chat_id, error_msg)
                except Exception as e:
                    send_message(chat_id, "❌ Error occurred! Try again later.")
            else:
                send_message(chat_id, "⚠️ Please send a valid URL / කරුණාකර නිවැරදි Link එකක් එවන්න.")

        return "ok", 200
    return "Bot is running live on Vercel!"

if __name__ == "__main__":
    app.run()
