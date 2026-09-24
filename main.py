#!/usr/bin/env python3
"""
TikTok DM Streak Automation
Kirim trending video ke temen via DM setiap hari buat maintain streak 🔥
"""

import json
import time
import random
import hashlib
import os
import sys
from datetime import datetime

import requests

# ============================================================
# CONFIG
# ============================================================

COOKIES_FILE = "cookies.json"        # Export dari Cookie-Editor
TARGET_USERNAME = ""                  # Username temen target
INTERVAL_HOURS = 24                  # Kirim sekali sehari
MESSAGE_TEMPLATE = ""                 # Pesanopsional (kosong = cuma link)

# ============================================================
# TIKTOK API ENDPOINTS (internal)
# ============================================================

TIKTOK_BASE = "https://www.tiktok.com"

# Headers umum
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}


# ============================================================
# COOKIE LOADER
# ============================================================

def load_cookies(path: str) -> dict:
    """Load cookies dari file JSON (Cookie-Editor format)."""
    if not os.path.exists(path):
        print(f"[ERROR] File cookies tidak ditemukan: {path}")
        print("Export cookies dari browser pakai Cookie-Editor → JSON format")
        sys.exit(1)
    
    with open(path) as f:
        raw = json.load(f)
    
    # Cookie-Editor exports as list of {name, value, domain, ...}
    if isinstance(raw, list):
        cookies = {}
        for c in raw:
            name = c.get("name", "")
            value = c.get("value", "")
            if name and value:
                cookies[name] = value
        return cookies
    
    # Jika sudah format dict
    if isinstance(raw, dict):
        return raw
    
    print("[ERROR] Format cookies tidak dikenali")
    sys.exit(1)


def get_session(cookies: dict) -> requests.Session:
    """Buat session requests dengan cookies TikTok."""
    s = requests.Session()
    s.headers.update(BASE_HEADERS)
    for name, value in cookies.items():
        s.cookies.set(name, value, domain=".tiktok.com")
    return s


# ============================================================
# GET CSRF TOKEN
# ============================================================

def get_csrf_token(s: requests.Session) -> str:
    """Ambil CSRF token dari cookies atau halaman TikTok."""
    # Coba dari cookies langsung
    csrf = s.cookies.get("tt_csrf_token") or s.cookies.get("csrf_token") or s.cookies.get("msToken")
    if csrf:
        return csrf
    
    # Coba dari halaman
    try:
        res = s.get(f"{TIKTOK_BASE}/", timeout=15)
        # Cari di response
        for line in res.text.split("\n"):
            if "csrfToken" in line or "csrf_token" in line:
                # Extract value
                import re
                match = re.search(r'"csrfToken":\s*"([^"]+)"', line)
                if match:
                    return match.group(1)
                match = re.search(r'"csrf_token":\s*"([^"]+)"', line)
                if match:
                    return match.group(1)
    except Exception:
        pass
    
    return ""


# ============================================================
# GET USER INFO (resolve username → user_id)
# ============================================================

def get_user_info(s: requests.Session, username: str) -> dict | None:
    """Ambil info user dari username."""
    try:
        res = s.get(
            f"{TIKTOK_BASE}/api/user/detail/",
            params={"uniqueId": username},
            timeout=15,
        )
        data = res.json()
        if data.get("statusCode") == 0:
            user = data.get("userInfo", {})
            return {
                "user_id": user.get("user", {}).get("id", ""),
                "sec_uid": user.get("user", {}).get("secUid", ""),
                "unique_id": user.get("user", {}).get("uniqueId", ""),
                "nickname": user.get("user", {}).get("nickname", ""),
            }
    except Exception as e:
        print(f"[ERROR] Gagal ambil info user: {e}")
    return None


# ============================================================
# GET CONVERSATION ID (buat DM)
# ============================================================

def get_conversation_id(s: requests.Session, user_id: str) -> str | None:
    """Ambil conversation_id untuk DM ke user tertentu."""
    try:
        # Coba list conversations dulu
        res = s.get(
            f"{TIKTOK_BASE}/api/dm/conversation/list/",
            params={"count": 50},
            timeout=15,
        )
        data = res.json()
        if data.get("statusCode") == 0:
            for conv in data.get("conversations", []):
                participants = conv.get("participants", [])
                for p in participants:
                    if str(p.get("user_id", "")) == str(user_id):
                        return conv.get("conversation_id", "")
        
        # Jika nggak ketemu, initiate chat baru
        res = s.post(
            f"{TIKTOK_BASE}/api/dm/conversation/create/",
            json={"user_id": user_id},
            timeout=15,
        )
        data = res.json()
        if data.get("statusCode") == 0:
            return data.get("conversation_id", "")
            
    except Exception as e:
        print(f"[ERROR] Gagal ambil conversation_id: {e}")
    return None


# ============================================================
# GET TRENDING/FYP VIDEOS
# ============================================================

def get_trending_videos(s: requests.Session, count: int = 10) -> list[dict]:
    """Ambil video trending dari TikTok FYP."""
    videos = []
    
    try:
        # Method 1: Challenge/trending endpoint
        res = s.get(
            f"{TIKTOK_BASE}/api/challenge/item_list/",
            params={
                "challengeID": "1",  # trending
                "count": count,
                "cursor": 0,
            },
            timeout=15,
        )
        data = res.json()
        if data.get("statusCode") == 0:
            for item in data.get("itemList", []):
                videos.append({
                    "id": item.get("id", ""),
                    "desc": item.get("desc", ""),
                    "author": item.get("author", {}).get("uniqueId", ""),
                    "url": f"https://www.tiktok.com/@{item.get('author', {}).get('uniqueId', '')}/video/{item.get('id', '')}",
                })
    except Exception:
        pass
    
    # Method 2: Generic trending
    if not videos:
        try:
            res = s.get(
                f"{TIKTOK_BASE}/api/trending/item_list/",
                params={"count": count, "cursor": 0},
                timeout=15,
            )
            data = res.json()
            if data.get("statusCode") == 0:
                for item in data.get("itemList", []):
                    videos.append({
                        "id": item.get("id", ""),
                        "desc": item.get("desc", ""),
                        "author": item.get("author", {}).get("uniqueId", ""),
                        "url": f"https://www.tiktok.com/@{item.get('author', {}).get('uniqueId', '')}/video/{item.get('id', '')}",
                    })
        except Exception:
            pass
    
    # Method 3: Discover page
    if not videos:
        try:
            res = s.get(
                f"{TIKTOK_BASE}/api/discover/item/",
                params={"count": count},
                timeout=15,
            )
            data = res.json()
            if data.get("statusCode") == 0:
                for item in data.get("data", []):
                    vid = item.get("aweme", item)
                    videos.append({
                        "id": vid.get("id", ""),
                        "desc": vid.get("desc", ""),
                        "author": vid.get("author", {}).get("unique_id", ""),
                        "url": f"https://www.tiktok.com/@{vid.get('author', {}).get('unique_id', '')}/video/{vid.get('id', '')}",
                    })
        except Exception:
            pass
    
    return videos


# ============================================================
# SEND DM
# ============================================================

def send_dm(s: requests.Session, conversation_id: str, text: str) -> bool:
    """Kirim pesan DM via TikTok."""
    try:
        csrf = get_csrf_token(s)
        headers = {
            "X-CSRFToken": csrf,
            "Content-Type": "application/json",
        }
        
        payload = {
            "conversation_id": conversation_id,
            "content": text,
            "item_type": 0,  # 0 = text, 3 = share video
        }
        
        res = s.post(
            f"{TIKTOK_BASE}/api/dm/send/",
            json=payload,
            headers=headers,
            timeout=15,
        )
        data = res.json()
        
        if data.get("statusCode") == 0:
            return True
        else:
            print(f"[WARN] Send gagal: {data.get('status_msg', 'unknown error')}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Send DM gagal: {e}")
        return False


def send_video_share(s: requests.Session, conversation_id: str, video_url: str) -> bool:
    """Share video ke DM."""
    try:
        csrf = get_csrf_token(s)
        headers = {
            "X-CSRFToken": csrf,
            "Content-Type": "application/json",
        }
        
        payload = {
            "conversation_id": conversation_id,
            "content": video_url,
            "item_type": 3,  # 3 = share video/link
        }
        
        res = s.post(
            f"{TIKTOK_BASE}/api/dm/send/",
            json=payload,
            headers=headers,
            timeout=15,
        )
        data = res.json()
        
        if data.get("statusCode") == 0:
            return True
        else:
            # Fallback: kirim sebagai text
            return send_dm(s, conversation_id, f"Check this out! {video_url}")
            
    except Exception as e:
        # Fallback
        return send_dm(s, conversation_id, f"Check this out! {video_url}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 50)
    print("  TikTok DM Streak Automation 🔥")
    print("=" * 50)
    print()
    
    # Load cookies
    print("[1] Loading cookies...")
    cookies = load_cookies(COOKIES_FILE)
    print(f"    Loaded {len(cookies)} cookies")
    
    # Buat session
    s = get_session(cookies)
    
    # Get user info
    print(f"\n[2] Mencari user: {TARGET_USERNAME}...")
    user = get_user_info(s, TARGET_USERNAME)
    if not user:
        print(f"[ERROR] User '{TARGET_USERNAME}' tidak ditemukan")
        sys.exit(1)
    print(f"    User ID: {user['user_id']}")
    print(f"    Nickname: {user['nickname']}")
    
    # Get conversation_id
    print(f"\n[3] Mencari conversation...")
    conv_id = get_conversation_id(s, user["user_id"])
    if not conv_id:
        print("[ERROR] Tidak bisa membuat/get conversation")
        sys.exit(1)
    print(f"    Conversation ID: {conv_id}")
    
    # Get trending videos
    print(f"\n[4] Mencari trending video...")
    videos = get_trending_videos(s, count=20)
    if not videos:
        print("[WARN] Tidak dapat trending video, coba ambil random")
        # Fallback: kirim link random
        video_url = "https://www.tiktok.com/trending"
    else:
        video = random.choice(videos)
        video_url = video["url"]
        print(f"    Video dipilih: {video['desc'][:50]}...")
        print(f"    URL: {video_url}")
    
    # Kirim DM
    print(f"\n[5] Mengirim DM...")
    if MESSAGE_TEMPLATE:
        success = send_dm(s, conv_id, f"{MESSAGE_TEMPLATE}\n\n{video_url}")
    else:
        success = send_video_share(s, conv_id, video_url)
    
    if success:
        print("    ✅ Berhasil dikirim!")
    else:
        print("    ❌ Gagal mengirim")
    
    # Log
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "target": TARGET_USERNAME,
        "video_url": video_url,
        "success": success,
    }
    
    with open("send_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"\n[6] Log tersimpan ke send_log.json")
    print("=" * 50)


if __name__ == "__main__":
    main()
