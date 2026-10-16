import os
import re
import time
import threading
import requests
from flask import Flask, request
from bs4 import BeautifulSoup

BOT_TOKEN = "8621084667:AAGrNfeOwpl1H-6PYho3o6r2vICv2Mg4dLM"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

LOGO_URL = "https://i.ibb.co/60cF3xk3/logo.png"

app = Flask(__name__)

SUPPORTED_SITES_TEXT = """🌐 **ꜱᴜᴩᴩᴏʀᴛᴇᴅ ꜱɪᴛᴇꜱ**

• 10drives
• 4br
• adlink
• adlinksumo
• adrinolinks
• adsfly
• aii
• alpharede
• arahlink
• arlinks
• arolink
• babylinks
• besargaji
• bicolink
• bindaaslinks
• bit.ly
• boky
• boostylink
• caslinks
• clksz
• cloudfam
• cpmshort
• cutt.ly
• cuttty
• cuty
• devuploads
• dl.surf
• droplink
• dupload
• earn2click
• earn4link
• earnads
• earnbylink
• earnlink
• easysky
• egolinks
• encurtarapido
• exe
• exeygo
• ez4short
• ezy
• fast-acort
• fastuplod
• ffgaminglink
• ffgamingshort
• filelimited
• finityrede
• fly2url
• followyou
• get2short
• goo.su
• gplinks
• gujjumods
• iflylink
• inddrive
• indiaearnx
• indianshortner
• inshorturl
• instantlinks
• just2earn
• link2unlock
• link4sub
• linkify
• linkjust
• linkpays
• links.asprin
• linksfire
• linksflys
• linksgo
• linkshort
• linkshortx
• linkvertise
• linkx
• liteshort
• liteurl
• lksfy
• lnbz
• luckyurl
• makelinks
• mediafire
• mineverse360
• minifyurls
• modishort
• moneyblink
• monteolympus
• move2link
• nanolinks
• nhapma
• nitro-link
• nowshort
• oii.la
• open2get
• ouo
• papajiurl
• prospexurl
• raysvidya
• rbxurl
• redirly
• rempo
• remso
• safefileku
• sannerurl
• seulink
• sfile
• sfl
• short.gy
• short4cash
• shortwala
• shortxlinks
• shortz.linkpc
• shrinkme
• shrtslug
• skiplinko
• softurl
• srnky
• sub2boost
• sub2go
• sub2unlock
• sub4unlock
• subforunlock
• submais
• subs4unlock
• surajitlinks
• task-locker
• teknoasian
• tfushorty
• tinysl
• tinyurl
• tipsguru
• tpi.li
• tr.ee
• tutwuri
• unityrede
• unlocktoearn
• upfiles
• uploadrar
• urlking
• urllinkshort
• urlspay
• v2links
• vipshort
• vplink
• vplinks
• yeumoney
• yorurl
• yourfamily
• zdrive
• Safelink"""

def delete_message_later(chat_id, message_id, delay=1800):
    def delayed_delete():
        time.sleep(delay)
        try:
            requests.post(f"{TELEGRAM_API}/deleteMessage", json={"chat_id": chat_id, "message_id": message_id})
        except Exception:
            pass
    thread = threading.Thread(target=delayed_delete)
    thread.daemon = True
    thread.start()

def set_reaction(chat_id, message_id, emoji="🔥"):
    url = f"{TELEGRAM_API}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}]
    }
    try:
        requests.post(url, json=payload)
    except Exception:
        pass

def send_message(chat_id, text, reply_markup=None, auto_delete=True):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    res = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload).json()
    msg_id = res.get("result", {}).get("message_id")
    if msg_id:
        if auto_delete:
            delete_message_later(chat_id, msg_id, 1800)
        set_reaction(chat_id, msg_id, "🔥")
    return res

def send_photo(chat_id, photo_url, caption, reply_markup=None, auto_delete=True):
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    res = requests.post(f"{TELEGRAM_API}/sendPhoto", json=payload).json()
    msg_id = res.get("result", {}).get("message_id")
    if msg_id:
        if auto_delete:
            delete_message_later(chat_id, msg_id, 1800)
        set_reaction(chat_id, msg_id, "🔥")
    return res

def edit_message(chat_id, message_id, text):
    requests.post(f"{TELEGRAM_API}/editMessageText", json={"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"})

def resolve_url(url):
    """බයිපාස් API කිහිපයක් හරහා vplinks වැනි සයිට් වල නියම අಂತಿම ලින්ක් එක ලබාගැනීම"""
    
    # 1. Primary Bypass API
    try:
        api_res = requests.get(f"https://api.bypass.vip/bypass?url={url}", timeout=8).json()
        if api_res.get("status") == "success" and api_res.get("destination"):
            dest = api_res.get("destination")
            if dest and dest.startswith("http"):
                return dest
    except Exception:
        pass

    # 2. Secondary Bypass API (Alternative Worker)
    try:
        api_res = requests.get(f"https://bypass.lasernull.workers.dev/?url={url}", timeout=8).json()
        if api_res.get("destination"):
            dest = api_res.get("destination")
            if dest and dest.startswith("http"):
                return dest
    except Exception:
        pass

    # 3. Third Bypass API (Universal Bypasser)
    try:
        api_res = requests.get(f"https://eu.org/api/bypass?url={url}", timeout=8).json()
        if api_res.get("result"):
            dest = api_res.get("result")
            if dest and dest.startswith("http"):
                return dest
    except Exception:
        pass

    # 4. Direct Scraping Fallback
    try:
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'}
        res = session.get(url, headers=headers, allow_redirects=True, timeout=8)
        if res.url and res.url != url and "vplinks" not in res.url:
            return res.url
            
        soup = BeautifulSoup(res.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and 'vplinks' not in href and 'google' not in href and 'telegram' not in href:
                return href
    except Exception:
        pass

    return None

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        data = request.get_json(force=True)

        if "callback_query" in data:
            query = data["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            if query["data"] == "show_supported_sites":
                send_message(chat_id, SUPPORTED_SITES_TEXT)
            return "ok", 200

        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_first_name = data["message"]["from"].get("first_name", "User")
            text = data["message"]["text"].strip()
            user_msg_id = data["message"]["message_id"]

            set_reaction(chat_id, user_msg_id, "🔥")
            delete_message_later(chat_id, user_msg_id, 1800)

            if text == "/start":
                welcome_text = (
                    "👋 **Hello! I am BYPASS BOT - SIBOK** </>\n\n"
                    "Send me any short link from supported sites, and I will extract the original link for you!\n\n"
                    "👋 **ආයුබෝවන්! මම Link Bypasser Bot කෙනෙක්.**\n"
                    "ඔයාගේ Short Link එක මට එවන්න!\n\n"
                    "⏱️ _Note: All messages will auto-delete in 30 minutes._"
                )
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🌐 Supported Sites [147 Total]", "callback_data": "show_supported_sites"}]
                    ]
                }
                
                res = send_photo(chat_id, LOGO_URL, welcome_text, reply_markup=keyboard)
                if not res.get("ok"):
                    send_message(chat_id, welcome_text, reply_markup=keyboard)
                return "ok", 200

            url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
            url_match = re.search(url_pattern, text)

            if url_match:
                target_url = url_match.group(0)

                sent_msg = send_message(chat_id, "🌀 **BYPASSING LINK...**\n\n`[ █▒▒▒▒▒▒▒▒▒ ] 10%`\n_⚡ Connecting..._")
                msg_id = sent_msg.get("result", {}).get("message_id")

                if msg_id:
                    time.sleep(0.5)
                    edit_message(chat_id, msg_id, "🌀 **BYPASSING LINK...**\n\n`[ █████▒▒▒▒▒ ] 50%`\n_⚡ Extracting destination..._")

                final_url = resolve_url(target_url)

                if msg_id:
                    edit_message(chat_id, msg_id, "🌀 **BYPASSING LINK...**\n\n`[ ██████████ ] 100%`\n_⚡ Done!_")
                    time.sleep(0.3)

                if final_url:
                    reply_text = (
                        "━━━━━━━━━━━━━━━━━━━\n"
                        "⚡ **ʙʏᴩᴀꜱꜱ ʙᴏᴛ - ꜱɪʙᴏᴋ** 🌟\n"
                        "━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🔗 **ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :-**\n`{target_url}`\n\n"
                        f"✅ **ʙʏᴩᴀꜱꜱᴇᴅ ʟɪɴᴋ :-**\n`{final_url}`\n\n"
                        "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
                        "⚡ **ꜱᴏᴜʀᴄᴇ :-** `Live API Bypass`\n"
                        f"🥳 **ʀᴇqᴜᴇꜱᴛᴇᴅ ʙʏ :-** `{user_first_name}`\n"
                        "━━━━━━━━━━━━━━━━━━━\n"
                        "🥫 **ᴅᴇᴠ :** `@SibokBypasser_bot` 🌟\n\n"
                        "⏱️ _This message will auto-delete in 30 minutes._"
                    )
                    if msg_id:
                        edit_message(chat_id, msg_id, reply_text)
                    else:
                        send_message(chat_id, reply_text)
                else:
                    error_msg = (
                        "❌ **BYPASS FAILED!**\n\n"
                        "⚠️ Could not extract the final destination link.\n\n"
                        "⏱️ _Auto-deletes in 30 minutes._"
                    )
                    if msg_id:
                        edit_message(chat_id, msg_id, error_msg)
                    else:
                        send_message(chat_id, error_msg)

            else:
                send_message(chat_id, "⚠️ **Please send a valid URL!** / කරුණාකර නිවැරදි Link එකක් විතරක් එවන්න.")

        return "ok", 200
    return "Bot is running live on Vercel!"

if __name__ == "__main__":
    app.run()
