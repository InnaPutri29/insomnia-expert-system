-- 1. Buat Database
CREATE DATABASE IF NOT EXISTS db_insomnia;
USE db_insomnia;

-- 2. Tabel Gejala (Untuk 20 pertanyaan standar ULBK)
CREATE TABLE IF NOT EXISTS gejala (
    id_gejala INT AUTO_INCREMENT PRIMARY KEY,
    kode_gejala VARCHAR(10) NOT NULL,
    pertanyaan TEXT NOT NULL,
    bobot INT DEFAULT 0
);

-- 3. Tabel Riwayat Deteksi (Untuk Dashboard User)
CREATE TABLE IF NOT EXISTS riwayat_deteksi (
    id_riwayat INT AUTO_INCREMENT PRIMARY KEY,
    nama_user VARCHAR(100),
    skor_total INT,
    hasil_kategori VARCHAR(50),
    tanggal_deteksi DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabel Admin (Untuk Login Pekan Depan)
CREATE TABLE IF NOT EXISTS admin (
    id_admin INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);