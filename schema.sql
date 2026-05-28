-- Drop tables if they exist to ensure clean setup
DROP TABLE IF EXISTS riwayat_deteksi;
DROP TABLE IF EXISTS gejala;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS admin;

-- 1. Tabel Users
CREATE TABLE IF NOT EXISTS users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

-- 2. Tabel Gejala (Untuk 7 Pertanyaan Insomnia Severity Index)
CREATE TABLE IF NOT EXISTS gejala (
    id_gejala INT AUTO_INCREMENT PRIMARY KEY,
    kode_gejala VARCHAR(10) NOT NULL,
    pertanyaan TEXT NOT NULL,
    kategori VARCHAR(50) NOT NULL,
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

-- Seed Data untuk Gejala (ISI)
INSERT INTO gejala (kode_gejala, pertanyaan, kategori, bobot) VALUES
('G01', 'Kesulitan memulai tidur (dalam 1 bulan terakhir)', 'onset', 0),
('G02', 'Kesulitan mempertahankan tidur / sering terbangun', 'maintenance', 0),
('G03', 'Masalah bangun tidur terlalu pagi dan tidak bisa tidur kembali', 'early', 0),
('G04', 'Seberapa puas/tidak puas Anda dengan pola tidur Anda saat ini?', 'satisfaction', 0),
('G05', 'Seberapa besar masalah tidur Anda mengganggu aktivitas siang hari Anda (misal: kelelahan, konsentrasi, memori, suasana hati)?', 'daytime', 0),
('G06', 'Seberapa terlihat oleh orang lain bahwa masalah tidur Anda menurunkan kualitas hidup Anda?', 'visibility', 0),
('G07', 'Seberapa khawatir/tertekan Anda tentang masalah tidur Anda saat ini?', 'distress', 0);

-- Seed Data untuk Admin Default (password: admin123)
INSERT INTO users (username, email, password, role) VALUES
('admin', 'admin@insomnify.com', '$2b$12$bC0jYtXUhkQbb05/6mqTh.plMrdk4cJnvql.07DwLlhET74SpSkQS', 'admin');