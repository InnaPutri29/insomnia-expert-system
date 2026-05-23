import pymysql
pymysql.install_as_MySQLdb()

import os
import MySQLdb
from dotenv import load_dotenv

# Load environment variables dari .env
load_dotenv()

# Baca kredensial dari .env
host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
db = os.getenv('MYSQL_DB', 'defaultdb')
port = int(os.getenv('MYSQL_PORT', 3306))

print("=== MIGRASI DATABASE TO AIVEN ===")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"User: {user}")
print(f"Database: {db}")
print("================================")

# Cek file CA Certificate
ssl_config = {}
ca_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ca.pem')
if os.path.exists(ca_path):
    ssl_config['ca'] = ca_path
    print("Menggunakan CA Certificate (ca.pem) untuk SSL...")
elif host and 'aivencloud.com' in host:
    print("Menghubungkan dengan SSL (enkripsi standar)...")

try:
    # Membuat koneksi dengan SSL jika terdeteksi Aiven
    if ssl_config:
        conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db, port=port, ssl=ssl_config)
    elif host and 'aivencloud.com' in host:
        conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db, port=port, ssl={})
    else:
        conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db, port=port)
    
    cursor = conn.cursor()
    
    # Membaca file schema.sql
    schema_file = 'schema.sql'
    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"File {schema_file} tidak ditemukan di folder proyek!")
        
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Bersihkan baris komentar secara line-by-line agar aman
    lines = schema.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Lewati baris komentar
        if stripped.startswith('--') or stripped.startswith('#') or stripped.startswith('/*'):
            continue
        cleaned_lines.append(line)
        
    cleaned_schema = "\n".join(cleaned_lines)
    
    # Memisahkan query berdasarkan karakter ';'
    queries = cleaned_schema.split(';')
    
    for query in queries:
        clean_query = query.strip()
        if clean_query:
            # Lewati perintah CREATE DATABASE dan USE karena di Aiven / Cloud MySQL
            # kita wajib menggunakan database default yang sudah disediakan ('defaultdb')
            upper_query = clean_query.upper()
            if upper_query.startswith("CREATE DATABASE") or upper_query.startswith("USE "):
                print(f"Mengabaikan query (sudah otomatis pakai database Aiven): {clean_query.splitlines()[0][:60]}...")
                continue
                
            print(f"Menjalankan query: {clean_query.splitlines()[0][:60]}...")
            cursor.execute(clean_query)
            
    conn.commit()
    print("\n[SUKSES] MIGRASI SELESAI! Semua tabel di schema.sql berhasil dibuat di database Aiven MySQL Anda.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"\n[ERROR] GAGAL MIGRASI: {e}")
