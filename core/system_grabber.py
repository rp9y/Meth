import os
import getpass
from pathlib import Path
from config.paths import SYSTEM, OTHER

LOG_DIR = Path("METH_LOGS")
LOG_DIR.mkdir(exist_ok=True)

def extract_system_content():
    username = getpass.getuser()

    for name, raw_path in {**SYSTEM, **OTHER}.items():
        path = os.path.expandvars(raw_path.replace("<username>", username))
        if not os.path.exists(path):
            continue

        category_file = LOG_DIR / f"system_{name.lower().replace(' ', '_')}.txt"
        with open(category_file, "w", encoding="utf-8", errors="ignore") as log:
            log.write(f"=== {name} ===\n")
            log.write(f"Path: {path}\n\n")

            try:
                if os.path.isfile(path):
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read(4000)
                            log.write("Content:\n")
                            log.write(content + "\n")
                    except:
                        with open(path, "rb") as f:
                            data = f.read(512)
                            log.write("Binary preview (hex):\n")
                            log.write(data.hex() + "\n")
                elif os.path.isdir(path):
                    log.write("Directory listing (first 20 items):\n")
                    count = 0
                    for root, dirs, files in os.walk(path):
                        for d in dirs + files:
                            if count >= 20:
                                break
                            log.write(f"  {os.path.join(root, d)}\n")
                            count += 1
                        if count >= 20:
                            break
            except Exception as e:
                log.write(f"Error: {e}\n")
            log.write("\n")

def main():
    extract_system_content()

if __name__ == "__main__":
    main()