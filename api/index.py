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
                # Text එකෙන් URL එක විතරක් වෙනම වෙන් කරගැනීම (Regex)
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
                    api_url = f"https://api.bypass.vip/bypass?url={target_url}"
                    res = requests.get(api_url, timeout=10).json()

                    # API එකෙන් එන විවිධ Response Keys පරීක්ෂා කිරීම
                    dest = res.get("destination") or res.get("result") or res.get("url") or res.get("bypassed_url")

                    # None හෝ فاضි නොවී හරියටම Destination Link එක ආවොත් පමණක් යැවීම
                    if (res.get("status") == "success" or res.get("success") is True) and dest and str(dest).lower() != "none":
                        reply_text = f"✅ **Original Link:**\n`{dest}`"
                        send_message(chat_id, reply_text)
                    else:
                        error_msg = "❌ Failed to bypass this link."
                        if detected_lang == 'si':
                            error_msg = "❌ මේ Link එක Bypass කරන්න බැරි වුණා (Link එකේ අවුලක් හෝ Supported නැත)."
                        send_message(chat_id, error_msg)
                except Exception as e:
                    send_message(chat_id, "❌ Error occurred! Try again later.")
            else:
                send_message(chat_id, "⚠️ Please send a valid URL / කරුණාකර නිවැරදි Link එකක් එවන්න.")

        return "ok", 200
    return "Bot is running live on Vercel!"

if __name__ == "__main__":
    app.run()
