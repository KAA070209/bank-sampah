import os
import sys
from dotenv import load_dotenv

# Pastikan path proyek bisa diimpor
sys.path.insert(0, os.path.dirname(__file__))

# Muat file .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Import Flask app dari file app.py
from app import app as application
