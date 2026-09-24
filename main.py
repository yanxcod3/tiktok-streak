#!/usr/bin/env python3
"""
TikTok DM Streak Automation — Playwright Edition
Auto kirim video FYP ke temen via DM buat maintain streak 🔥
"""

import json
import time
import random
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

# ============================================================
# CONFIG
# ============================================================

CONFIG_FILE = "config.json"
USER_DATA_DIR = Path(__file__).parent / "browser_data"
LOG_FILE = "send_log.json"

# ============================================================
# CONFIG LOADER
# ============================================================

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Config tidak ditemukan: {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)

# ============================================================
# BROWSER SESSION
# ============================================================

def get_browser(playwright):
    """Buka Chrome dengan user data (session tersimpan)."""
    USER_DATA_DIR.mkdir(exist_ok=True)
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=str(USER_DATA_DIR),
        headless=False,  # Tampil biar bisa login manual pertama kali
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ],
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800},
    )
    return browser

def ensure_logged_in(page):
    """Cek apakah sudah login, kalau belum minta login manual."""
    page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    
    # Cek login status — kalau ada tombol login, berarti belum login
    login_btn = page.query_selector('button[data-e2e="login-button"]')
    if login_btn:
        print("\n" + "=" * 50)
        print("  ⚠️  BELUM LOGIN TIKTOK")
        print("  Silakan login manual di browser yang terbuka.")
        print("  Setelah login, tekan ENTER di terminal ini.")
        print("=" * 50)
        input("\nTekan ENTER setelah login selesai...")
        page.reload(wait_until="domcontentloaded")
        time.sleep(2)
    
    # Verifikasi login
    avatar = page.query_selector('[data-e2e="nav-login-avatar"]') or page.query_selector('img[alt*="avatar"]')
    if avatar:
        print("✅ Login berhasil!")
        return True
    else:
        print("⚠️  Login mungkin belum berhasil, coba lagi.")
        return False

# ============================================================
# GET FYP VIDEO
# ============================================================

def get_fyp_video(page) -> str | None:
    """Ambil random video dari FYP."""
    page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    
    # Scroll sekali biar load beberapa video
    for _ in range(random.randint(2, 5)):
        page.mouse.wheel(0, random.randint(300, 800))
        time.sleep(random.uniform(0.5, 1.5))
    
    # Ambil semua video link
    video_links = page.query_selector_all('a[href*="/video/"]')
    
    if not video_links:
        print("[WARN] Tidak ada video di FYP")
        return None
    
    # Pilih random
    chosen = random.choice(video_links)
    href = chosen.get_attribute("href")
    
    if href:
        if href.startswith("/"):
            return f"https://www.tiktok.com{href}"
        return href
    return None

# ============================================================
# SEND DM VIA SHARE
# ============================================================

def share_video_to_dm(page, video_url: str, target_username: str) -> bool:
    """Share video ke temen via DM TikTok."""
    try:
        # Buka video
        page.goto(video_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        
        # Klik tombol Share
        share_btn = page.query_selector('[data-e2e="share-button"]') or page.query_selector('button[aria-label*="Share"]')
        if not share_btn:
            # Coba cari share icon
            share_btn = page.query_selector('[data-e2e="share-btn"]')
        
        if not share_btn:
            print("[WARN] Tombol share tidak ditemukan")
            return False
        
        share_btn.click()
        time.sleep(2)
        
        # Klik "Send to friends" atau "Message"
        send_to_friend = page.query_selector('div[data-e2e="share-to-friends"]')
        if not send_to_friend:
            send_to_friend = page.query_selector('text="Send to friends"')
        if not send_to_friend:
            send_to_friend = page.query_selector('text="Message"')
        
        if send_to_friend:
            send_to_friend.click()
            time.sleep(2)
        
        # Cari target di search
        search_input = page.query_selector('input[placeholder*="Search"]') or page.query_selector('input[data-e2e="search-user-input"]')
        if search_input:
            search_input.fill(target_username)
            time.sleep(2)
            
            # Klik hasil pencarian pertama
            first_result = page.query_selector(f'div[data-e2e="search-user-item"]') or page.query_selector(f'span:has-text("{target_username}")')
            if first_result:
                first_result.click()
                time.sleep(1)
                
                # Klik tombol Send
                send_btn = page.query_selector('button[data-e2e="send-btn"]') or page.query_selector('button:has-text("Send")')
                if send_btn:
                    send_btn.click()
                    time.sleep(2)
                    print(f"    ✅ Video dikirim ke @{target_username}!")
                    return True
        
        print("[WARN] Gagal kirim DM via share")
        # Tutup share modal
        page.keyboard.press("Escape")
        return False
        
    except Exception as e:
        print(f"[ERROR] Share gagal: {e}")
        try:
            page.keyboard.press("Escape")
        except:
            pass
        return False

# ============================================================
# LOG
# ============================================================

def log_send(target: str, video_url: str, success: bool):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "video_url": video_url,
        "success": success,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ============================================================
# WAIT UNTIL TIME
# ============================================================

def wait_until(target_time: str, offset_minutes: int = 0):
    now = datetime.now()
    hour, minute = map(int, target_time.split(":"))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if offset_minutes > 0:
        offset = random.randint(-offset_minutes, offset_minutes)
        target += timedelta(minutes=offset)
    
    if target <= now:
        target += timedelta(days=1)
    
    wait_seconds = (target - now).total_seconds()
    print(f"    Menunggu sampai {target.strftime('%H:%M')} ({int(wait_seconds // 3600)}j {int((wait_seconds % 3600) // 60)}m)...")
    time.sleep(wait_seconds)

# ============================================================
# MAIN
# ============================================================

def main():
    config = load_config()
    target = config["target_username"]
    send_time = config.get("send_time", "09:00")
    offset = config.get("random_offset_minutes", 30)
    
    print("=" * 50)
    print("  TikTok DM Streak Automation 🔥")
    print("=" * 50)
    print(f"  Target: @{target}")
    print(f"  Jam kirim: {send_time} (±{offset} menit)")
    print()
    
    # Tunggu jam target
    print(f"[1] Menunggu jam kirim...")
    wait_until(send_time, offset)
    
    print(f"\n[2] Buka browser...")
    with sync_playwright() as p:
        browser = get_browser(p)
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Login check
        print(f"[3] Cek login...")
        if not ensure_logged_in(page):
            print("[ERROR] Login gagal")
            browser.close()
            return
        
        # Ambil video FYP
        print(f"\n[4] Cari video FYP...")
        video_url = get_fyp_video(page)
        if not video_url:
            print("[ERROR] Tidak dapat video FYP")
            browser.close()
            return
        print(f"    Video: {video_url}")
        
        # Share ke DM
        print(f"\n[5] Share ke @{target}...")
        success = share_video_to_dm(page, video_url, target)
        
        # Log
        log_send(target, video_url, success)
        
        if success:
            print(f"\n[6] ✅ Selesai! Streak terjaga 🔥")
        else:
            print(f"\n[6] ⚠️  Gagal kirim, coba manual.")
        
        print("=" * 50)
        
        # Tutup browser
        browser.close()

if __name__ == "__main__":
    main()
