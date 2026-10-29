import os
import sys
import shutil
import time
import socket
import webbrowser
import threading

# Setup base directory for PyInstaller frozen app vs dev mode
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    exe_dir = os.path.dirname(sys.executable)
    
    # 1. Seed database copy into exe folder if it doesn't already exist
    seed_db = os.path.join(BASE_DIR, "skillpath_ai.db")
    user_db = os.path.join(exe_dir, "skillpath_ai.db")
    if os.path.exists(seed_db) and not os.path.exists(user_db):
        try:
            shutil.copy2(seed_db, user_db)
        except Exception:
            pass
            
    # 2. Critical: Set working directory to BASE_DIR so all templates & static paths resolve
    os.chdir(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)

# Ensure BASE_DIR is in sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from main import app

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_available_port(start_port: int = 8000) -> int:
    port = start_port
    while is_port_in_use(port) and port < start_port + 50:
        port += 1
    return port

def open_browser_delayed(url: str):
    time.sleep(1.8)
    print(f"\n[SkillPath AI] Launching browser at: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[SkillPath AI] Could not launch browser automatically: {e}")

def main():
    port = find_available_port(8000)
    url = f"http://127.0.0.1:{port}"
    
    print("=" * 68)
    print("  🚀 SkillPath AI — Adaptive Learning & Career Platform")
    print(f"  🌐 Application URL: {url}")
    print("  🔑 Instant 1-Click Portals Available (or use demo accounts):")
    print("     • Student:     student@skillpath.ai   / Student@123")
    print("     • Teacher:     teacher@skillpath.ai   / Teacher@123")
    print("     • Super Admin: superadmin@skillpath.ai / Admin@123")
    print("     • College:     collegeadmin@skillpath.ai / Admin@123")
    print("  📌 Keep this console window open while using the application.")
    print("  ⭐ Press CTRL+C or close this window to exit.")
    print("=" * 68)
    
    # Launch browser in background thread
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()
    
    # Run uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()

