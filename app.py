from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from decimal import Decimal
import uuid
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "bank_sampah_secret_key")  # Ganti dengan key yang lebih aman di produksi

# ================= KONEKSI DATABASE =================
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
@app.context_processor
def inject_notif():
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) as total
            FROM notifikasi
            WHERE user_id=%s
        """, (session['user_id'],))

        total_notif = cursor.fetchone()['total']
        cursor.close()
        db.close()

        return dict(total_notif=total_notif)

    return dict(total_notif=0)
# =========================
# DECORATORS
# =========================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') != role:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return decorated
    return wrapper
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
# =========================
# HOME
# =========================
@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT nama_kategori, harga_per_kg, kelompok
        FROM kategori_sampah
        ORDER BY kelompok, harga_per_kg DESC
    """)
    kategori = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('landing.html', kategori=kategori)
# =========================
# REGISTER NASABAH
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    # Jika sudah login, tidak boleh akses register
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nama = request.form['nama']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        alamat = request.form['alamat']
        no_hp = request.form['no_hp']

        hashed_pw = generate_password_hash(password)

        db = get_db()
        cursor = db.cursor()

        try:
            # Insert user
            cursor.execute("""
                INSERT INTO users (nama, username,email, password, role, status)
                VALUES (%s,%s,%s,%s,'nasabah','pending')
            """, (nama, username, email, hashed_pw))

            user_id = cursor.lastrowid

            # Insert nasabah
            cursor.execute("""
                INSERT INTO nasabah (user_id, kode_nasabah, alamat, no_hp, saldo)
                VALUES (%s,%s,%s,%s,0)
            """, (user_id, f"NSB{user_id:04d}", alamat, no_hp))

            db.commit()
            flash("Registrasi berhasil! Tunggu konfirmasi admin.", "success")
            return redirect(url_for('login'))

        except mysql.connector.Error:
            db.rollback()
            flash("Username sudah digunakan!", "danger")

        finally:
            cursor.close()
            db.close()

    return render_template('register.html')

# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    # Jika sudah login, redirect sesuai role
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user['password'], password):

            if user['status'] != 'approved':
                flash("Akun belum disetujui admin!", "warning")
                return redirect(url_for('login'))

            session['user_id'] = user['id']
            session['role'] = user['role']
            session['nama'] = user['nama']

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))

        flash("Login gagal!", "danger")

    return render_template('login.html')

# =========================
# LOGOUT
# =========================
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Berhasil logout!", "success")
    return redirect(url_for('login'))

# =========================
# ADMIN DASHBOARD
# =========================
@app.route('/admin_dashboard')
@login_required
@role_required('admin')
def admin_dashboard():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Statistik
    cursor.execute("SELECT COUNT(*) as total FROM nasabah")
    total_nasabah = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM users 
        WHERE role='nasabah' AND status='pending'
    """)
    pending = cursor.fetchone()['total']

    cursor.execute("SELECT IFNULL(SUM(saldo),0) as total FROM nasabah")
    total_saldo = cursor.fetchone()['total']

    # Grafik bulanan
    cursor.execute("""
        SELECT MONTH(tanggal) as bulan, 
               IFNULL(SUM(total_berat),0) as total
        FROM transaksi_setor
        GROUP BY MONTH(tanggal)
        ORDER BY MONTH(tanggal)
    """)
    data = cursor.fetchall()

    bulan_labels = [f"Bulan {d['bulan']}" for d in data]
    bulan_data = [float(d['total']) for d in data]

    # Pending list
    cursor.execute("""
        SELECT id, nama, username 
        FROM users 
        WHERE role='nasabah' AND status='pending'
    """)
    pending_users = cursor.fetchall()
    # Penarikan pending
    cursor.execute("""
        SELECT p.id, p.jumlah, p.tanggal, n.kode_nasabah, u.nama
        FROM penarikan p
        JOIN nasabah n ON p.nasabah_id = n.id
        JOIN users u ON n.user_id = u.id
        WHERE p.status='pending'
        ORDER BY p.tanggal DESC
    """)
    penarikan_pending = cursor.fetchall()
    cursor.execute("""
        SELECT MONTH(tanggal) as bulan,
            IFNULL(SUM(total_harga),0) as total
        FROM transaksi_setor
        GROUP BY MONTH(tanggal)
        ORDER BY MONTH(tanggal)
    """)
    masuk = cursor.fetchall()

    saldo_masuk = [float(m['total']) for m in masuk]
    cursor.execute("""
        SELECT MONTH(tanggal) as bulan,
            IFNULL(SUM(jumlah),0) as total
        FROM penarikan
        WHERE status='approved'
        GROUP BY MONTH(tanggal)
        ORDER BY MONTH(tanggal)
    """)
    keluar = cursor.fetchall()

    saldo_keluar = [float(k['total']) for k in keluar]
    cursor.execute("""
        SELECT ks.kelompok,
            IFNULL(SUM(ds.berat),0) as total
        FROM detail_setor ds
        JOIN kategori_sampah ks ON ds.kategori_id = ks.id
        GROUP BY ks.kelompok
    """)
    jenis = cursor.fetchall()

    # Default 0
    organik = 0
    low = 0
    high = 0
    b3 = 0

    for j in jenis:
        if j['kelompok'] == 'organik':
            organik = float(j['total'])
        elif j['kelompok'] == 'anorganik_low':
            low = float(j['total'])
        elif j['kelompok'] == 'anorganik_high':
            high = float(j['total'])
        elif j['kelompok'] == 'b3':
            b3 = float(j['total'])

    jenis_data = [organik, low, high, b3]
    cursor.close()
    db.close()

    return render_template(
        "admin_dashboard.html",
        total_nasabah=total_nasabah,
        setor_hari_ini=0,
        total_saldo=total_saldo,
        pending=pending,
        bulan_labels=bulan_labels,
        penarikan_pending=penarikan_pending,
        bulan_data=bulan_data,
        pending_users=pending_users,
        saldo_masuk=saldo_masuk,
        saldo_keluar=saldo_keluar,
        jenis_data=jenis_data
    )
@app.route('/tambah_nasabah', methods=['POST'])
@login_required
@role_required('admin')
def tambah_nasabah():

    nama = request.form['nama']
    username = request.form['username']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])
    alamat = request.form['alamat']
    no_hp = request.form['no_hp']

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (nama, username, email, password, role, status)
            VALUES (%s,%s,%s,%s,'nasabah','approved')
        """, (nama, username, email, password))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO nasabah (user_id, kode_nasabah, alamat, no_hp, saldo)
            VALUES (%s,%s,%s,%s,0)
        """, (user_id, f"NSB{user_id:04d}", alamat, no_hp))

        db.commit()
        flash("Nasabah berhasil ditambahkan!", "success")

    except:
        db.rollback()
        flash("Gagal menambahkan nasabah!", "danger")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for('admin_dashboard'))
@app.route('/tambah_kategori', methods=['POST'])
@login_required
@role_required('admin')
def tambah_kategori():

    nama_kategori = request.form.get('nama_kategori', '').strip()
    harga = request.form.get('harga_per_kg', '').strip()
    kelompok = request.form.get('kelompok', '').strip()

    allowed_kelompok = ['organik', 'anorganik_low', 'anorganik_high', 'b3']

    # ======================
    # VALIDASI INPUT
    # ======================

    # 1️⃣ Nama tidak boleh kosong
    if not nama_kategori:
        flash("Nama kategori wajib diisi!", "danger")
        return redirect(url_for('admin_dashboard'))

    # 2️⃣ Harga harus angka dan > 0
    try:
        harga = Decimal(harga)
        if harga <= 0:
            flash("Harga harus lebih dari 0!", "danger")
            return redirect(url_for('admin_dashboard'))
    except:
        flash("Harga harus berupa angka yang valid!", "danger")
        return redirect(url_for('admin_dashboard'))

    # 3️⃣ Kelompok harus sesuai ENUM
    if kelompok not in allowed_kelompok:
        flash("Kelompok tidak valid!", "danger")
        return redirect(url_for('admin_dashboard'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        # 4️⃣ Cek duplikat nama kategori
        cursor.execute("""
            SELECT id FROM kategori_sampah
            WHERE nama_kategori = %s
        """, (nama_kategori,))
        existing = cursor.fetchone()

        if existing:
            flash("Kategori sudah ada!", "warning")
            return redirect(url_for('admin_dashboard'))

        # Insert ke database
        cursor.execute("""
            INSERT INTO kategori_sampah 
            (nama_kategori, harga_per_kg, kelompok)
            VALUES (%s,%s,%s)
        """, (nama_kategori, harga, kelompok))

        db.commit()
        flash("Kategori berhasil ditambahkan!", "success")

    except Exception as e:
        db.rollback()
        print("ERROR TAMBAH KATEGORI:", e)
        flash("Terjadi kesalahan sistem!", "danger")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for('admin_dashboard'))
# =========================
# ADMIN APPROVAL
# =========================
@app.route('/approve/<int:user_id>')
@login_required
@role_required('admin')
def approve(user_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE users SET status='approved' WHERE id=%s",
        (user_id,)
    )
    db.commit()

    cursor.close()
    db.close()

    flash("Nasabah berhasil disetujui!", "success")
    return redirect(url_for('admin_dashboard'))
@app.route('/approve_penarikan/<int:penarikan_id>')
@login_required
@role_required('admin')
def approve_penarikan(penarikan_id):

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM penarikan
            WHERE id=%s AND status='pending'
        """, (penarikan_id,))
        penarikan = cursor.fetchone()

        if not penarikan:
            flash("Data tidak ditemukan!", "danger")
            return redirect(url_for('admin_dashboard'))

        # Ambil saldo sekarang
        cursor.execute("SELECT saldo FROM nasabah WHERE id=%s",
                       (penarikan['nasabah_id'],))
        nasabah = cursor.fetchone()

        saldo_sebelum = nasabah['saldo']
        saldo_sesudah = saldo_sebelum - penarikan['jumlah']

        if saldo_sesudah < 0:
            flash("Saldo tidak cukup!", "danger")
            return redirect(url_for('admin_dashboard'))

        # Update saldo
        cursor.execute("""
            UPDATE nasabah
            SET saldo=%s
            WHERE id=%s
        """, (saldo_sesudah, penarikan['nasabah_id']))

        # Update penarikan
        cursor.execute("""
            UPDATE penarikan
            SET status='approved',
                approved_by=%s
            WHERE id=%s
        """, (session['user_id'], penarikan_id))

        # Log saldo
        cursor.execute("""
            INSERT INTO log_saldo
            (nasabah_id, tipe, referensi_id, jumlah,
             saldo_sebelum, saldo_sesudah)
            VALUES (%s,'penarikan',%s,%s,%s,%s)
        """, (
            penarikan['nasabah_id'],
            penarikan_id,
            penarikan['jumlah'],
            saldo_sebelum,
            saldo_sesudah
        ))

        # Kirim notifikasi ke nasabah
        cursor.execute("""
            SELECT user_id FROM nasabah WHERE id=%s
        """, (penarikan['nasabah_id'],))
        user = cursor.fetchone()

        cursor.execute("""
            INSERT INTO notifikasi (user_id, judul, pesan)
            VALUES (%s,%s,%s)
        """, (
            user['user_id'],
            "Penarikan Disetujui",
            f"Penarikan Rp {penarikan['jumlah']} telah disetujui admin"
        ))

        db.commit()
        flash("Penarikan berhasil disetujui!", "success")

    except Exception as e:
        db.rollback()
        print("ERROR:", e)
        flash("Terjadi kesalahan!", "danger")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for('admin_dashboard'))
# =========================
# HALAMAN KATEGORI
# =========================
@app.route('/admin_kategori')
@login_required
@role_required('admin')
def admin_kategori():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM kategori_sampah ORDER BY id DESC")
    kategori = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_kategori.html', kategori=kategori)
# =========================
# HALAMAN NASABAH
# =========================
@app.route('/admin_nasabah')
@login_required
@role_required('admin')
def admin_nasabah():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT n.*, u.nama, u.username
        FROM nasabah n
        JOIN users u ON n.user_id = u.id
        ORDER BY n.id DESC
    """)
    nasabah = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_nasabah.html', nasabah=nasabah)
# =========================
# HALAMAN PENARIKAN
# =========================
@app.route('/admin_penarikan')
@login_required
@role_required('admin')
def admin_penarikan():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, u.nama, n.kode_nasabah
        FROM penarikan p
        JOIN nasabah n ON p.nasabah_id = n.id
        JOIN users u ON n.user_id = u.id
        ORDER BY p.tanggal DESC
    """)
    penarikan = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_penarikan.html', penarikan=penarikan)
# =========================
# HALAMAN TRANSAKSI
# =========================
@app.route('/admin_transaksi')
@login_required
@role_required('admin')
def admin_transaksi():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT ts.*, u.nama
        FROM transaksi_setor ts
        JOIN nasabah n ON ts.nasabah_id = n.id
        JOIN users u ON n.user_id = u.id
        ORDER BY ts.tanggal DESC
    """)
    transaksi = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_transaksi.html', transaksi=transaksi)
# =========================
# HALAMAN NOTIFIKASI
# =========================
@app.route('/admin_notifikasi')
@login_required
@role_required('admin')
def admin_notifikasi():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM notifikasi
        ORDER BY created_at DESC
    """)
    notifikasi = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('admin_notifikasi.html', notifikasi=notifikasi)
# =========================
# DASHBOARD NASABAH
# =========================

@app.route('/dashboard')
@login_required
@role_required('nasabah')
def dashboard():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Ambil data nasabah
    cursor.execute("""
        SELECT n.*, u.nama, u.email
        FROM nasabah n
        JOIN users u ON n.user_id = u.id
        WHERE n.user_id=%s
    """, (session['user_id'],))

    nasabah = cursor.fetchone()
    cursor.execute("""
        SELECT * FROM notifikasi
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 20
    """, (session['user_id'],))
    notifications = cursor.fetchall()

    # Hitung notif belum dibaca
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM notifikasi
        WHERE user_id = %s AND is_read = 0
    """, (session['user_id'],))
    total_notif = cursor.fetchone()['total']

    # Total Setor
    cursor.execute("""
        SELECT IFNULL(SUM(total_harga),0) as total_setor 
        FROM transaksi_setor
        WHERE nasabah_id=%s
    """, (nasabah['id'],))
    total_setor = cursor.fetchone()['total_setor']

    # Total Penarikan
    cursor.execute("""
        SELECT IFNULL(SUM(jumlah),0) as total_tarik
        FROM penarikan
        WHERE nasabah_id=%s AND status='approved'
    """, (nasabah['id'],))
    total_tarik = cursor.fetchone()['total_tarik']
    # Riwayat Setor (FIXED)
    cursor.execute("""
        SELECT 
            ts.tanggal,
            ts.kode_transaksi,
            ds.berat,
            ds.subtotal,
            ks.nama_kategori,
            ks.kelompok,
            CASE 
                WHEN ks.kelompok = 'anorganik_low' THEN 'Low Value'
                WHEN ks.kelompok = 'anorganik_high' THEN 'High Value'
                ELSE '-'
            END as value_label
        FROM transaksi_setor ts
        JOIN detail_setor ds ON ts.id = ds.transaksi_id
        JOIN kategori_sampah ks ON ds.kategori_id = ks.id
        WHERE ts.nasabah_id=%s
        ORDER BY ts.tanggal DESC
    """, (nasabah['id'],))
    riwayat_setor = cursor.fetchall()
    # Riwayat Penarikan
    cursor.execute("""
        SELECT * FROM penarikan
        WHERE nasabah_id=%s
        ORDER BY tanggal DESC
    """, (nasabah['id'],))
    riwayat_penarikan = cursor.fetchall()

    # Grafik Bulanan
    cursor.execute("""
        SELECT MONTH(tanggal) as bulan, 
            IFNULL(SUM(total_berat),0) as total
        FROM transaksi_setor
        WHERE nasabah_id=%s
        GROUP BY MONTH(tanggal)
        ORDER BY MONTH(tanggal)
    """, (nasabah['id'],))
    grafik = cursor.fetchall()

    nama_bulan = [
        "", "Januari", "Februari", "Maret", "April",
        "Mei", "Juni", "Juli", "Agustus",
        "September", "Oktober", "November", "Desember"
    ]

    bulan_labels = [nama_bulan[int(g['bulan'])] for g in grafik]
    bulan_data = [float(g['total']) for g in grafik]
    # Ambil kategori untuk form setor
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM notifikasi
        WHERE user_id=%s
    """, (session['user_id'],))

    total_notif = cursor.fetchone()['total']
    cursor.close()
    db.close()

    return render_template(
        "nasabah_dashboard.html",
        nasabah=nasabah,
        total_setor=total_setor,
        total_tarik=total_tarik,
        riwayat_setor=riwayat_setor,
        notifications=notifications,
        riwayat_penarikan=riwayat_penarikan,
        bulan_labels=bulan_labels,
        bulan_data=bulan_data,
        total_notif=total_notif
    )
@app.route('/profil_nasabah', methods=['GET','POST'])
@login_required
@role_required('nasabah')
def profil_nasabah():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.id, u.nama, u.email
        FROM users u
        WHERE u.id=%s
    """, (session['user_id'],))

    user = cursor.fetchone()

    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']

        cursor.execute("""
            UPDATE users
            SET nama=%s, email=%s
            WHERE id=%s
        """, (nama, email, session['user_id']))

        db.commit()
        session['nama'] = nama

        flash("Profil berhasil diperbarui!", "success")
        return redirect(url_for('profil_nasabah'))

    cursor.close()
    db.close()

    return render_template('profil_nasabah.html', user=user)
from decimal import Decimal
import time
@app.route('/ajukan_penarikan', methods=['POST'])
@login_required
@role_required('nasabah')
def ajukan_penarikan():

    try:
        jumlah = Decimal(request.form['jumlah'])
    except:
        flash("Format jumlah tidak valid!", "danger")
        return redirect(url_for('penarikan'))

    metode = request.form.get('metode', 'tunai')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM nasabah WHERE user_id=%s",
            (session['user_id'],)
        )
        nasabah = cursor.fetchone()

        saldo = Decimal(str(nasabah['saldo']))

        # ===== VALIDASI =====
        if jumlah <= 0:
            flash("Jumlah tidak valid!", "danger")
            return redirect(url_for('penarikan'))

        if jumlah < Decimal('50000'):
            flash("Minimal penarikan Rp 50.000!", "danger")
            return redirect(url_for('penarikan'))

        if jumlah > saldo:
            flash("Saldo tidak mencukupi!", "danger")
            return redirect(url_for('penarikan'))

        # Cek pending
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM penarikan
            WHERE nasabah_id=%s AND status='pending'
        """, (nasabah['id'],))

        if cursor.fetchone()['total'] > 0:
            flash("Masih ada penarikan yang belum diproses!", "warning")
            return redirect(url_for('penarikan'))

        # ===== INSERT =====
        kode = f"WD{nasabah['id']}{int(time.time())}"

        cursor.execute("""
            INSERT INTO penarikan
            (kode_penarikan, nasabah_id, jumlah, metode, status)
            VALUES (%s,%s,%s,%s,'pending')
        """, (
            kode,
            nasabah['id'],
            jumlah,
            metode
        ))

        db.commit()
        flash("Pengajuan penarikan berhasil dikirim!", "success")

    except Exception as e:
        db.rollback()
        print("ERROR AJUKAN:", e)
        flash("Terjadi kesalahan sistem!", "danger")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for('penarikan'))
@app.route('/penarikan')
@login_required
@role_required('nasabah')
def penarikan():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT n.*, u.nama, u.email
        FROM nasabah n
        JOIN users u ON n.user_id = u.id
        WHERE n.user_id=%s
    """, (session['user_id'],))

    nasabah = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("nasabah_penarikan.html", nasabah=nasabah)
@app.route('/setor_sampah', methods=['POST'])
@login_required
@role_required('nasabah')
def setor_sampah():

    kategori_id = request.form['kategori_id']
    berat = Decimal(request.form['berat'])

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM nasabah WHERE user_id=%s", (session['user_id'],))
    nasabah = cursor.fetchone()

    cursor.execute("SELECT * FROM kategori_sampah WHERE id=%s", (kategori_id,))
    kategori = cursor.fetchone()

    harga = Decimal(kategori['harga_per_kg'])
    subtotal = berat * harga

    try:
        # Insert transaksi_setor (petugas_id = NULL)
        # Generate kode unik
        kode = "TRX" + uuid.uuid4().hex[:10].upper()

        cursor.execute("""
            INSERT INTO transaksi_setor 
            (kode_transaksi, nasabah_id, petugas_id, total_berat, total_harga)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            kode,
            nasabah['id'],
            None,
            berat,
            subtotal
        ))
        transaksi_id = cursor.lastrowid

        # Insert detail_setor (WAJIB isi harga juga!)
        cursor.execute("""
            INSERT INTO detail_setor
            (transaksi_id, kategori_id, berat, harga, subtotal)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            transaksi_id,
            kategori_id,
            berat,
            harga,
            subtotal
        ))

        # Update saldo
        cursor.execute("""
            UPDATE nasabah 
            SET saldo = saldo + %s,
                total_berat_terkumpul = total_berat_terkumpul + %s
            WHERE id=%s
        """, (subtotal, berat, nasabah['id']))

        db.commit()
        flash("Setor sampah berhasil!", "success")

    except Exception as e:
        db.rollback()
        print("ERROR SETOR:", e)
        flash("Gagal menyimpan setoran!", "danger")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for('form_setor'))
@app.route('/form_setor')
@login_required
@role_required('nasabah')
def form_setor():

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM kategori_sampah ORDER BY nama_kategori ASC")
    kategori = cursor.fetchall()
    cursor.execute("""
        SELECT n.*, u.nama, u.email
        FROM nasabah n
        JOIN users u ON n.user_id = u.id
        WHERE n.user_id=%s
    """, (session['user_id'],))

    nasabah = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template("form_setor_sampah.html", kategori=kategori, nasabah=nasabah)
# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)