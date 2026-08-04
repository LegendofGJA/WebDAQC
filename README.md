# Audit & QC Toolkit — Streamlit App

Aplikasi multipage: isi penilaian audit toko, simpan sebagai draft, lalu
tempel foto QC ke Excel yang sama tanpa upload ulang.

## Struktur

```
WebDAQC/
├── app.py                      # landing page (2 kartu tool)
├── audit_core.py                # koneksi Supabase + generator workbook (dipakai bersama)
├── scoring.py                   # replikasi rumus skor dari Excel
├── style.py                     # tema CSS bersama
├── structure.json               # hasil parse struktur item Excel
├── template.xlsx                # template Excel master (jangan dihapus)
├── requirements.txt
├── supabase_schema.sql
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
├── presets/
│   └── .gitkeep                 # taruh .xlsx preset lain di sini kalau perlu
└── pages/
    ├── 1_DETAIL_AUDIT.py        # isi & simpan penilaian audit
    ├── 2_QC_Image_Inserter.py   # ambil draft, tempel foto, download
    └── 3_Admin_Hapus_Data.py    # hapus draft (password protected)
```

## Alur pemakaian

1. Buka halaman **DETAIL AUDIT** → isi Store Name, Date, Auditor, PIC, dan
   Remarks tiap poin (Remarks terisi → Actual Score poin itu otomatis 0).
2. Klik **Save** → data tersimpan ke Supabase, dikunci per Store Name + Date.
3. Buka halaman **QC Image Inserter** → pada "Sumber template" pilih
   **"Dari Draft DETAIL AUDIT"** → pilih toko & tanggal yang tadi disimpan →
   header dan skor otomatis terisi, tidak perlu upload apapun.
4. Upload tanda tangan Auditor/PIC (opsional) dan foto-foto QC.
5. Klik **MULAI EXPORT DAN PROSES DATA** → **Download**. Halaman ini
   sengaja **tidak punya opsi save** — foto tidak pernah dikirim ke
   Supabase, supaya storage tidak jebol.
6. (Opsional, admin) Halaman **Admin — Hapus Data** untuk menghapus draft
   yang sudah tidak diperlukan. Perlu password (`ADMIN_PASSWORD` di secrets).

## Setup

1. **Supabase**: buat project → jalankan `supabase_schema.sql` di SQL
   Editor → catat Project URL dan **Publishable key** (Project Settings →
   API Keys → bukan Secret key).
2. Salin `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`,
   isi `SUPABASE_URL`, `SUPABASE_KEY`, dan `ADMIN_PASSWORD` (untuk halaman
   admin).
3. Install & jalankan lokal (opsional, untuk tes sebelum deploy):
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Deploy ke Streamlit Community Cloud

1. Push repo ini ke GitHub.
2. [share.streamlit.io](https://share.streamlit.io) → **Create app** →
   pilih repo, branch `main`, main file `app.py`.
3. **Advanced settings → Secrets**, isi:
   ```toml
   SUPABASE_URL = "https://xxxxx.supabase.co"
   SUPABASE_KEY = "sb_publishable_xxxxxxxxxxxxxxxxx"
   ADMIN_PASSWORD = "password-kamu"
   ```
4. Deploy.

## Catatan keamanan

- Tanpa login untuk pengguna biasa — siapapun yang punya link app bisa
  isi/lihat/lanjutkan draft (RLS Supabase dibuka publik). Cocok untuk tim
  internal, jangan sebar link ke publik luas kalau datanya sensitif.
- Halaman Admin dikunci password sederhana (`ADMIN_PASSWORD`). Ini bukan
  sistem login penuh — cukup untuk mencegah orang iseng menghapus data,
  bukan untuk data yang butuh keamanan tingkat tinggi.
- **Jangan pernah commit `secrets.toml` (tanpa `.example`) ke GitHub.**
  `.gitignore` sudah memblokir ini — pastikan foldernya benar bernama
  `.streamlit` (dengan titik di depan) dan file `.gitignore` (dengan titik
  di depan) supaya proteksi ini benar-benar aktif.
