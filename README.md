# ♻️ Bank Sampah Digital + AI Detection

Sistem **Bank Sampah Digital berbasis Web** menggunakan **Flask + MySQL** dengan fitur **deteksi jenis sampah berbasis AI (Roboflow Inference API)** untuk membantu proses klasifikasi sampah secara otomatis.

Repository:
🔗 [https://github.com/KAA070209/bank-sampah](https://github.com/KAA070209/bank-sampah)

---

## 🚀 Teknologi yang Digunakan

* 🐍 Python 3
* 🌐 Flask 3.0.2
* 🗄 MySQL
* 🔐 Werkzeug Security 3.0.1 (Password Hashing)
* 🤖 Roboflow Inference API
  * `inference-sdk` 0.9.17
  * `roboflow` 1.1.48
* 📊 Chart.js
* ⚙️ python-dotenv 1.0.1 (Environment Variable Management)
* 🎨 HTML, CSS, Bootstrap

---

# ✨ Fitur Utama

---

## 🌐 0. Landing Page

* Halaman utama yang dapat diakses tanpa login
* Menampilkan daftar harga kategori sampah:
  * Organik
  * Anorganik Low Value
  * Anorganik High Value
  * B3
* Redirect ke login/register sesuai kebutuhan

---

## 👤 1. Sistem Autentikasi

### 🔐 Register Nasabah

* Registrasi akun dengan data lengkap:
  * Nama lengkap
  * Username
  * Email
  * Password
  * Alamat
  * No. HP
* Password di-hash menggunakan `generate_password_hash` (Werkzeug)
* Status akun: `pending` (harus disetujui admin sebelum login)

### 🔑 Login

* Validasi password dengan `check_password_hash`
* Redirect otomatis sesuai role:
  * `admin` → Admin Dashboard
  * `nasabah` → Dashboard Nasabah
* Validasi status akun (harus `approved`)

### 🚪 Logout

* Session dihapus seluruhnya
* Cache dinonaktifkan untuk keamanan

---

# 👑 2. Fitur Admin

## 📊 Admin Dashboard

Menampilkan statistik dan grafik:

* **Total Nasabah** - Jumlah seluruh nasabah terdaftar
* **Total Saldo Keseluruhan** - Total saldo semua nasabah
* **Jumlah Akun Pending** - Nasabah yang belum disetujui
* **Grafik Setor Sampah Bulanan** - Total berat setor per bulan
* **Grafik Saldo Masuk & Keluar** - Perbandingan saldo masuk (setor) vs keluar (penarikan) per bulan
* **Grafik Komposisi Jenis Sampah** - Berat berdasarkan kelompok:
  * Organik
  * Anorganik Low Value
  * Anorganik High Value
  * B3
* **List Pending Users** - Nasabah yang menunggu persetujuan
* **List Penarikan Pending** - Penarikan yang menunggu approval

---

## 👥 Manajemen Nasabah

* **Approve akun nasabah** - Setuju/menerima nasabah baru
* **Tambah nasabah langsung oleh admin** - Input data lengkap (nama, username, email, password, alamat, no hp)
* **Lihat daftar nasabah** - Data lengkap semua nasabah

---

## ♻️ Manajemen Kategori Sampah

* Tambah kategori baru dengan validasi:
  * **Nama kategori** tidak boleh kosong
  * **Harga per kg** harus angka dan > 0
  * **Kelompok** harus sesuai enum:
    * `organik`
    * `anorganik_low`
    * `anorganik_high`
    * `b3`
* Cegah duplikasi nama kategori

---

## 💰 Manajemen Penarikan

* **Approve penarikan** - Setuju penarikan saldo nasabah
* **Validasi saldo cukup** - Pastikan saldo mencukupi
* **Update saldo otomatis** - Kurangi saldo setelah approve
* **Simpan log saldo** - Catat saldo sebelum dan sesudah
* **Kirim notifikasi ke nasabah** - Beritahu nasabah penarikan disetujui

---

## 📦 Manajemen Transaksi

* Lihat semua transaksi setor
* Detail kategori & subtotal per transaksi

---

## 🔔 Sistem Notifikasi

* Notifikasi saat penarikan disetujui
* Hitung jumlah notifikasi unread
* Status read/unread per notifikasi

---

# 👨‍💼 3. Fitur Nasabah

## 📊 Dashboard Nasabah

Menampilkan:

* **Total Setoran** - Total nilai sampah yang disetorkan
* **Total Penarikan** - Total nilai penarikan yang disetujui
* **Saldo Saat Ini** - Saldo tersedia
* **Grafik Setor Bulanan** - Berat setor per bulan
* **Riwayat Setor** - Detail transaksi setor (tanggal, kode, berat, kategori, subtotal)
* **Riwayat Penarikan** - Semua pengajuan penarikan
* **Notifikasi terbaru** - Daftar notifikasi terbaru

---

## ♻️ Setor Sampah

Fitur utama:

* Upload foto sampah (wajib)
* Pilih kategori (manual atau dari AI)
* Input berat (dalam kg)
* Harga otomatis dari database
* Saldo otomatis bertambah setelah setor
* Simpan detail transaksi:
  * Foto
  * Confidence AI
  * Detail kategori & subtotal

Validasi:

* Foto wajib diupload
* Format hanya JPG / PNG
* Berat dikalkulasi menggunakan `Decimal` (presisi tinggi untuk uang)

---

## 🤖 Deteksi Sampah Otomatis (AI)

Menggunakan:

* `InferenceHTTPClient` dari Roboflow
* Model: `sampah-ufpof-cgmp3/4`

Endpoint:

```
POST /detect_ajax
```

Proses:

1. Upload gambar
2. AI mendeteksi kelas sampah
3. Filter confidence > 0.30
4. Ambil kategori dari database (tanpa hardcode harga)
5. Kirim response JSON:
   * `nama_kategori`
   * `harga_per_kg`
   * `kelompok`
   * `confidence`
   * `detected_class`

### Kelas AI yang Didukung

| AI Class | Mapping       |
| -------- | ------------- |
| BOTOL    | Botol Plastik |
| PLASTIK  | Plastik       |
| KERTAS   | Kertas        |
| KARDUS   | Kardus        |
| DAUN     | Organik       |
| KALENG   | Kaleng        |
| BATERAI  | B3            |

---

## 💸 Penarikan Saldo

* **Minimal penarikan**: Rp 50.000
* **Validasi saldo cukup** - Tidak boleh melebihi saldo
* **Validasi tidak ada penarikan pending** - Satu penarikan per waktu
* **Status awal**: `pending` (menunggu persetujuan admin)
* **Disetujui oleh admin** - Baru mengurangi saldo

---

## 👤 Profil Nasabah

* Edit nama lengkap
* Edit email
* Password tidak dapat diubah dari profil

---

# 🗄 Struktur Database (Tabel Utama)

* **users** - Data pengguna (admin & nasabah)
* **nasabah** - Data detail nasabah (kode, alamat, no hp, saldo)
* **kategori_sampah** - Kategori sampah dengan harga per kg & nama AI
* **transaksi_setor** - Header transaksi setor (tanggal, total berat, total harga, foto)
* **detail_setor** - Detail per kategori dalam satu transaksi (berat, harga, subtotal)
* **penarikan** - Riwayat penarikan saldo (jumlah, metode, status)
* **log_saldo** - Log perubahan saldo (sebelum/sesudah, tipe transaksi)
* **notifikasi** - Notifikasi untuk пользователей

---

# 🔒 Sistem Keamanan

* **Password hashing** - Menggunakan Werkzeug `generate_password_hash`
* **Session-based authentication** - Session Flask dengan secret key
* **Role-based access control** - Decorator `@role_required` untuk权限 kontrol
* **No-cache headers** - Mencegah caching halaman sensitif
* **Validasi input server-side** - Semua input divalidasi sebelum database
* **Decimal untuk transaksi uang** - Presisi tinggi untuk perhitungan uang
* **Session security config** - HttpOnly, SameSite Lax cookies

---

# ⚙️ Instalasi

## 1️⃣ Clone Repository

```
bash
git clone https://github.com/KAA070209/bank-sampah.git
cd bank-sampah
```

## 2️⃣ Install Dependency

```
bash
pip install Flask==3.0.2 mysql-connector-python==8.3.0 Werkzeug==3.0.1 python-dotenv==1.0.1 inference-sdk==0.9.17 roboflow==1.1.48
```

## 3️⃣ Setup Environment Variable

Buat file `.env` di root project:

```
SECRET_KEY=your_secret_key_ Disini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=db_bank_sampah
```

## 4️⃣ Setup Database

Import file SQL ke MySQL:

```
bash
mysql -u root -p db_bank_sampah < db/db_bank_sampah.sql
```

## 5️⃣ Jalankan Aplikasi

```
bash
python app.py
```

Akses:

```
http://127.0.0.1:5000
```

---

# 📌 Role Sistem

| Role    | Hak Akses                   |
| ------- | --------------------------- |
| admin   | Full akses sistem          |
| nasabah | Setor, penarikan, profil   |

---

# 🎯 Keunggulan Sistem

✅ AI Detection Otomatis (Roboflow)
✅ Harga Dinamis dari Database
✅ Dashboard Statistik Lengkap dengan 6 Grafik
✅ Sistem Approval Berlapis (pending → approved)
✅ Notifikasi Real-Time
✅ Keamanan Password Hashing
✅ Presisi Decimal untuk Transaksi Uang
✅ Clean Architecture Flask
✅ Landing Page dengan Daftar Harga
✅ Log Perubahan Saldo

---

# 📷 Preview Fitur

* Landing Page dengan daftar harga kategori
* Dashboard Admin dengan 6 grafik statistik
* Dashboard Nasabah dengan riwayat lengkap
* Form Setor dengan AI Detection
* Sistem Notifikasi Real-Time
* Manajemen Kategori Sampah
* Approval Penarikan oleh Admin

---

# 📄 Lisensi

Project ini dibuat untuk keperluan pembelajaran dan pengembangan sistem Bank Sampah Digital.

---
# 👨‍💻 Developer

Developed by: **KAA070209**

---

# 🙏 Credits

* Model AI: [sampah-ufpof-cgmp3/4](https://universe.roboflow.com/azkas-workspace-iffj2/sampah-ufpof-cgmp3) by Azkas Workspace
* Roboflow for AI Inference API
