import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import datetime

# ==============================
# CONFIG DATABASE
# ==============================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # isi kalau ada password mysql
        database="db_bank_sampah"
    )

# ==============================
# TAMBAH ADMIN
# ==============================
def add_admin(nama, username, email, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Hash password
        hashed_password = generate_password_hash(password)

        query = """
        INSERT INTO users 
        (nama, username, email, password, role, is_active, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            nama,
            username,
            email,
            hashed_password,
            "admin",      # role
            1,            # is_active
            "approved",   # status
            datetime.now()
        )

        cursor.execute(query, values)
        conn.commit()

        print("✅ Admin berhasil ditambahkan!")

    except mysql.connector.Error as err:
        print("❌ Error:", err)

    finally:
        cursor.close()
        conn.close()


# ==============================
# JALANKAN SCRIPT
# ==============================
if __name__ == "__main__":
    print("=== TAMBAH ADMIN BANK SAMPAH ===")

    nama = input("Nama lengkap: ")
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")

    add_admin(nama, username, email, password)