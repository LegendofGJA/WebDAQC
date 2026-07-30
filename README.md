# Internal Audit / Visit Store — Streamlit App

Web app hasil konversi dari `Template_0726.xlsx` (sheet **DETAIL AUDIT**).
Sheet **ATTACHMENT** tidak ditampilkan di web, tapi tetap ikut dibawa
utuh (tidak diubah) saat file di-download.

## Cara kerja singkat

- Semua 124 poin penilaian (item 1–124, sesuai kolom A di Excel) ditampilkan
  per kategori/subkategori dalam tabel yang bisa diisi kolom **Remarks**-nya.
- Begitu kolom Remarks suatu poin diisi teks apapun → **Actual Score poin itu
  otomatis jadi 0** (logika ini yang berjalan menggantikan input skor manual).
  Kalau kosong, Actual Score = Basic Score.
- Semua rumus rekap (total per kategori, Total Score, Final Score, Grading)
  direplikasi persis dari rumus Excel aslinya, termasuk bobot ×3 khusus
  kategori **OTHER** (`=D174/C174*100*3`) yang memang ada di template asli.
- Item **125 (ETC)** hanya catatan teks, tidak ada skor — ditampilkan apa
  adanya, sama seperti di Excel.

## Setup

1. **Buat project Supabase** (gratis) di https://supabase.com
2. Buka **SQL Editor**, jalankan isi file `supabase_schema.sql` di repo ini.
3. Di **Project Settings → API**, salin `Project URL` dan `anon public key`.
4. Salin `.streamlit/secrets.toml.example` menjadi `.streamlit/secrets.toml`,
   isi dengan URL & key tadi.
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Jalankan:
   ```bash
   streamlit run app.py
   ```

## Deploy (Streamlit Community Cloud)

1. Push folder ini ke GitHub repo.
2. Buka https://share.streamlit.io → New app → pilih repo, file `app.py` ; https://ateazzi.streamlit.app/
3. Di menu **Secrets** aplikasi, tempel isi `secrets.toml` (SUPABASE_URL,
   SUPABASE_KEY).
4. Deploy.

## Fitur "Save for Later" & lanjutkan nanti

- Tombol **💾 Save for Later** menyimpan seluruh isi (header + remarks) ke
  Supabase, dikunci berdasarkan **STORE NAME + DATE** (kombinasi ini harus
  unik — kalau toko yang sama diaudit tanggal berbeda, akan tersimpan
  sebagai draft terpisah).
- Setelah berhasil save, URL browser otomatis berisi `?store=...&date=...`.
  Jadi kalau browser di-refresh, data **tidak hilang** — otomatis dimuat
  ulang dari Supabase.
- Untuk melanjutkan audit toko lain di sesi baru / device lain, buka panel
  **📂 Buka data toko yang tersimpan**, pilih dari daftar, klik **Muat Draft**.

## Catatan penting

- Karena tanpa login, siapa saja yang punya akses ke aplikasi bisa
  membaca/menulis semua draft (RLS Supabase dibuka publik). Cocok untuk
  tim internal, tapi jangan expose URL app ke publik luas kalau datanya
  sensitif.
- Kalau ingin Actual Score bisa diisi manual (bukan cuma otomatis dari
  Remarks), beri tahu saya — bisa ditambahkan sebagai kolom yang bisa
  di-override.
- File `template.xlsx` adalah salinan template asli — jangan dihapus,
  dipakai sebagai basis setiap kali tombol Download ditekan (formula &
  formatting Excel tetap terjaga, hanya sel Store/Date/Auditor/PIC dan
  Actual Score + Remarks per item yang diisi ulang).
