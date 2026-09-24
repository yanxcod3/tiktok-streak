# TikTok DM Streak Automation 🔥

Auto kirim video dari FYP personal ke temen via DM buat maintain streak.

## Fitur

- 🎯 Ambil video dari FYP personal (berdasarkan algoritma akun lo)
- 📩 Kirim video ke temen via DM TikTok
- ⏰ Atur jam kirim yang diinginkan
- 🎲 Random offset biar nggak predicted
- 🔒 Pakai Playwright (browser automation, lebih aman)
- 📋 Log otomatis

## Persiapan

### 1. Install Dependencies

```bash
pip install playwright
python3 -m playwright install chromium
```

### 2. Edit Config

Buka `config.json`:

```json
{
    "target_username": "kemaldinnn",
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
python3 main.py
```

### Pertama Kali

Script akan buka browser TikTok. **Login manual** di browser tersebut, lalu tekan ENTER di terminal. Session akan tersimpan otomatis.

### Setelah Itu

Script buka browser yang sama → session otomatis → cari video FYP → kirim DM → tutup.

## Flow

```
1. Tunggu sampai jam kirim
2. Buka browser (session tersimpan)
3. Cek login status
4. Ambil video random dari FYP
5. Share video ke temen via DM
6. Log hasil
7. Tutup browser
```

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Browser minta login | Login manual, tekan ENTER |
| Share gagal | Cek koneksi, coba lagi |
| Video nggak ketemu | FYP kosong, script retry otomatis |

## Notes

- Pertama kali jalankan, login manual dulu di browser
- Session tersimpan di folder `browser_data/`
- Browser tampil (bukan headless) biar bisa login
- Script ini untuk personal use

## License

MIT
