# TikTok DM Streak Automation 🔥

Auto kirim video dari FYP personal ke temen via DM buat maintain streak.

## Fitur

- 🎯 Ambil video dari FYP personal (berdasarkan algoritma akun lo)
- 📩 Kirim video ke temen via DM
- ⏰ Atur jam kirim yang diinginkan
- 🎲 Random offset biar nggak predicted
- 📋 Log otomatis

## Persiapan

### 1. Export Cookies TikTok

- Login TikTok di Chrome/Firefox
- Install extension **[Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)**
- Klik icon Cookie-Editor → Export → JSON
- Simpan ke file `cookies.json`

### 2. Edit Config

Buka `config.json`:

```json
{
    "target_username": "username_temen_lo",
    "send_time": "09:00",
    "random_offset_minutes": 30
}
```

| Field | Keterangan |
|-------|-----------|
| `target_username` | Username TikTok temen target |
| `send_time` | Jam kirim (HH:MM) |
| `random_offset_minutes` | Variasi ±menit |

## Jalankan

```bash
pip install requests
python3 main.py
```

## Sumber Video

Video diambil dari FYP personal akun lo:

1. Recommend (FYP personalized)
2. Homefeed
3. Discover random
4. Trending (fallback)

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Cookies tidak ditemukan | Export ulang dari browser |
| User tidak ditemukan | Cek `target_username` |
| Send gagal | Cookies expired → export ulang |

## License

MIT
