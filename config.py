import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    # Secret key untuk session Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "bank_sampah_secret_key")  # Ganti dengan key yang lebih aman di produksi

    # Konfigurasi Database MySQL
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "db_bank_sampah")

    @staticmethod
    def get_db_config():
        """Mengembalikan konfigurasi database dalam bentuk dict untuk mysql.connector"""
        return {
            "host": Config.DB_HOST,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "database": Config.DB_NAME
        }

    # Konfigurasi keamanan session
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"  # Bisa "Strict" jika HTTPS
    SESSION_COOKIE_SECURE = False    # Ubah ke True jika sudah pakai HTTPS
