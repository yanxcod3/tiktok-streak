# TikTok DM Streak Automation 🔥

Auto kirim video FYP ke temen via DM buat maintain streak.

## Fitur

- 🎯 Ambil video dari **FYP personal** (berdasarkan algoritma akun lo)
- 📩 Kirim video ke temen via DM
- ⏰ Auto tunggu jam kirim yang diatur
- 🎲 Random offset ±30 menit biar nggak predicted
- 📋 Log otomatis ke `send_log.json`
- 🔒 Pakai cookies browser (tidak perlu login ulang)

## Persiapan

### 1. Export Cookies TikTok

- Login TikTok di Chrome/Firefox
- Install extension **[Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)** di Chrome Web Store
- Buka TikTok → klik icon Cookie-Editor
- Klik **Export** → pilih **JSON**
- Simpan hasilnya ke file `cookies.json` di folder ini

### 2. Edit Config

Buka file `config.json` dan isi:

```json
{
    "target_username": "username_temen_lo",
    "send_time": "09:00",
    "random_offset_minutes": 30
}
```

| Field | Keterangan | Default |
|-------|-----------|---------|
| `target_username` | Username TikTok temen target | wajib diisi |
| `send_time` | Jam kirim (format HH:MM) | `09:00` |
| `random_offset_minutes` | Variasi ±menit biar nggak predicted | `30` |

## Cara Jalankan

```bash
# Install dependency
pip install requests

# Jalankan
python3 main.py
```

Script akan:
1. Load cookies dari browser
2. Tunggu sampai jam `send_time` (dengan random offset)
3. Ambil video dari FYP personal akun lo
4. Kirim video ke temen via DM
5. Log hasil ke `send_log.json`

## Sumber Video

Script mengambil video dari FYP personal akun lo (bukan trending global):

1. **Recommend** — FYP personalized berdasarkan history
2. **Homefeed** — Feed utama akun lo
3. **Discover** — Discover random
4. **Trending** — Fallback kalau FYP kosong

## Struktur Folder

```
tiktok-streak/
├── main.py           # Script utama
├── config.json       # Konfigurasi target & jam kirim
├── cookies.json      # Cookies TikTok (export dari browser)
├── send_log.json     # Log pengiriman (auto-generated)
└── README.md
```

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `File cookies tidak ditemukan` | Export ulang cookies dari browser |
| `User tidak ditemukan` | Cek username di `config.json` |
| `Send gagal` | Cookies expired → export ulang |
| `Tidak ada video FYP` | Fallback ke trending otomatis |

## Notes

- Cookies TikTok expire dalam 1-4 minggu
- Kalau logout dari browser, cookies hangus
- Export ulang cookies kalau script error
- Script ini untuk personal use

## License

MIT
