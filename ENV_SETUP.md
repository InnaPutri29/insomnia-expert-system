# Panduan Setup Environment Variables

## Langkah-langkah Deploy

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install python-dotenv
```

### 2. Setup File `.env`

**Salin file `.env.example` ke `.env`:**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 3. Update File `.env` dengan Kredensial Aktual
Edit file `.env` dan ganti placeholder dengan nilai sebenarnya:

```env
# Konfigurasi Flask
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=xxxxxxxxxxxxx  # Ganti dengan kunci rahasia yang kuat dan unik

# Konfigurasi Database MySQL
MYSQL_HOST=nama-host-mysql
MYSQL_USER=username-database
MYSQL_PASSWORD=password-database
MYSQL_DB=insomnia_db
MYSQL_PORT=3306

# Konfigurasi Aplikasi
DEBUG=False
TESTING=False
```

### 4. Generate SECRET_KEY yang Aman (Opsional)
Jika ingin generate SECRET_KEY otomatis:
```python
import secrets
print(secrets.token_hex(32))
```

### 5. Setup Database
```bash
# Pastikan MySQL running, lalu buat database
mysql -u root -p < schema.sql
```

### 6. Run Aplikasi
```bash
# Development
flask run

# Production (gunakan gunicorn/uwsgi)
gunicorn app:app
```

## Catatan Keamanan

⚠️ **PENTING:**
- Jangan pernah commit file `.env` ke repository
- File `.env` sudah ada di `.gitignore`
- Gunakan kredensial yang kuat dan kompleks untuk production
- Jangan share file `.env` ke public atau tidak aman
- Ganti `SECRET_KEY` dengan nilai unik untuk setiap environment

## Environment Variables yang Didukung

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| FLASK_ENV | production | Mode Flask (development/production) |
| FLASK_APP | app.py | File utama Flask |
| SECRET_KEY | - | Kunci rahasia untuk session Flask |
| MYSQL_HOST | localhost | Host database MySQL |
| MYSQL_USER | root | Username database |
| MYSQL_PASSWORD | (kosong) | Password database |
| MYSQL_DB | insomnia_db | Nama database |
| MYSQL_PORT | 3306 | Port MySQL |
| DEBUG | False | Mode debug (jangan enable di production) |
| TESTING | False | Mode testing |

