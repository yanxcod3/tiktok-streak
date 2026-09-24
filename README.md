# TikTok DM Streak Automation 🔥

Auto kirim trending video TikTok ke temen via DM buat maintain streak.

## Fitur

- 🔍 Auto cari trending video TikTok (FYP)
- 📩 Kirim video ke temen via DM
- ⏰ Auto loop setiap 24 jam
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
    "interval_hours": 24,
    "message_template": ""
}
```

| Field | Keterangan |
|-------|-----------|
| `target_username` | Username TikTok temen yang mau dikirim |
| `interval_hours` | Interval pengiriman (default: 24 jam) |
| `message_template` | Pesanopsional sebelum link video |

## Cara Jalankan

```bash
# Install dependencies
pip install requests

# Jalankan sekali
python3 main.py

# Jalankan auto loop (setiap 24 jam)
python3 main.py --loop
```

## Flow

```
1. Load cookies dari browser
2. Cari trending video TikTok (FYP random)
3. Kirim link video ke temen via DM
4. Log hasil ke send_log.json
5. Ulangi setiap 24 jam
```

## Struktur Folder

```
tiktok-streak/
├── main.py           # Script utama
├── config.json       # Konfigurasi target & interval
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
| `Tidak ada trending video` | Coba lagi nanti / cek koneksi |

## Notes

- Cookies TikTok expire dalam 1-4 minggu
- Kalau logout dari browser, cookies hangus
- Export ulang cookies kalau script error
- Script ini untuk personal use, jangan spam

## License

MIT
