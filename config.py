import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'insomnia_db')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # --- SSL CONFIGURATION (Untuk Aiven MySQL / Production) ---
    # Jika file ca.pem ada di proyek, gunakan SSL dengan verifikasi CA.
    # Jika tidak ada tetapi host adalah Aiven, gunakan enkripsi SSL standar.
    ca_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ca.pem')
    if os.path.exists(ca_path):
        MYSQL_CUSTOM_OPTIONS = {
            'ssl': {
                'ca': ca_path
            }
        }
    elif 'aivencloud.com' in MYSQL_HOST:
        MYSQL_CUSTOM_OPTIONS = {
            'ssl': {}
        }