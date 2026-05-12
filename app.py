from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from config import Config
from inference.forward_chaining import hitung_insomnia
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# --- INISIALISASI DATABASE ---
mysql = MySQL(app)

# --- KONFIGURASI LOGIN MANAGER ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses halaman ini.'
login_manager.login_message_category = 'info'

# ===============================
# USER & ROLE CLASS
# ===============================
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_user, username, role FROM users WHERE id_user = %s", (user_id,))
    data = cur.fetchone()
    cur.close()
    if data:
        return User(data['id_user'], data['username'], data['role'])
    return None

# ===============================
# ROUTE UMUM & EDUKASI
# ===============================
@app.route("/")
@app.route("/home")
def home():
    return render_template("user/home.html")

@app.route("/edukasi")
def edukasi():
    return render_template("user/edukasi.html")

@app.route("/about")
def about():
    return render_template("user/about.html")

# ===============================
# FITUR DETEKSI (USER)
# ===============================
@app.route("/deteksi")
@login_required
def deteksi():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM gejala ORDER BY id_gejala ASC")
    gejala = cur.fetchall()
    cur.close()
    return render_template("user/deteksi.html", gejala=gejala)

@app.route('/proses_deteksi', methods=['POST'])
@login_required
def proses_deteksi():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_gejala FROM gejala ORDER BY id_gejala ASC")
    gejala_db = cur.fetchall()
    cur.close()

    jawaban = []
    for g in gejala_db:
        nilai = request.form.get(f"q{g['id_gejala']}")
        if nilai is None:
            flash("Semua pertanyaan harus dijawab!", "danger")
            return redirect(url_for('deteksi'))
        jawaban.append(int(nilai))

    total_skor, hasil, fakta, kesimpulan = hitung_insomnia(jawaban)

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            """INSERT INTO riwayat_deteksi 
               (nama_user, skor_total, hasil_kategori, tanggal_deteksi) 
               VALUES (%s, %s, %s, %s)""",
            (current_user.username, total_skor, hasil, datetime.now())
        )
        mysql.connection.commit()
        flash("Hasil deteksi berhasil disimpan!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Gagal menyimpan riwayat: {str(e)}", "danger")
    finally:
        cur.close()

    return render_template("user/hasil.html", skor=total_skor, kategori=hasil, fakta=fakta, kesimpulan=kesimpulan)

@app.route("/riwayat")
@login_required
def riwayat():
    if current_user.role == 'admin':
        return redirect(url_for('admin_riwayat'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM riwayat_deteksi WHERE nama_user = %s ORDER BY tanggal_deteksi DESC", (current_user.username,))
    riwayat_data = cur.fetchall()
    cur.close()
    return render_template("user/riwayat.html", riwayat=riwayat_data)

# ===============================
# AUTHENTICATION
# ===============================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_pw = request.form.get('confirm_password')

        if password != confirm_pw:
            flash('Konfirmasi password tidak cocok!', 'danger')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, 'user')", (username, email, hashed))
            mysql.connection.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except:
            mysql.connection.rollback()
            flash('Username/Email sudah terdaftar.', 'danger')
        finally:
            cur.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            db_password = user_data['password']
            if isinstance(db_password, str):
                db_password = db_password.encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), db_password):
                user_obj = User(user_data['id_user'], user_data['username'], user_data['role'])
                login_user(user_obj)
                flash(f"Selamat datang {user_data['username']}!", "success")
                return redirect(url_for('admin_dashboard' if user_obj.role == 'admin' else 'home'))
            else:
                flash('Password salah.', 'danger')
        else:
            flash('Username tidak ditemukan.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil keluar.', 'info')
    return redirect(url_for('login'))

# ===============================
# ADMIN PANEL
# ===============================
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin': return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    
    stats = {}
    kategori = ['Tidak Insomnia', 'Insomnia Ringan', 'Insomnia Sedang', 'Insomnia Berat']
    for kat in kategori:
        cur.execute("SELECT COUNT(*) as cnt FROM riwayat_deteksi WHERE hasil_kategori = %s", (kat,))
        stats[kat] = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM users")
    total_user = cur.fetchone()['cnt']

    cur.execute("SELECT * FROM riwayat_deteksi ORDER BY tanggal_deteksi DESC LIMIT 5")
    riwayat_recent = cur.fetchall()
    cur.close()

    return render_template("admin/dashboard.html", 
        normal=stats['Tidak Insomnia'], ringan=stats['Insomnia Ringan'], 
        sedang=stats['Insomnia Sedang'], berat=stats['Insomnia Berat'],
        total=sum(stats.values()), total_user=total_user, riwayat=riwayat_recent)

@app.route("/admin/manage-deteksi")
@login_required
def admin_manage_deteksi():
    if current_user.role != 'admin': return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM gejala ORDER BY id_gejala ASC")
    gejala_list = cur.fetchall()
    cur.close()
    return render_template("admin/manage_deteksi.html", pertanyaan=gejala_list)

@app.route("/admin/add-gejala", methods=['POST'])
@login_required
def admin_add_gejala():
    if current_user.role != 'admin': return redirect(url_for('home'))
    kode = request.form.get('kode_gejala')
    pertanyaan = request.form.get('pertanyaan')
    kategori = request.form.get('kategori')
    
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO gejala (kode_gejala, pertanyaan, kategori, bobot) VALUES (%s, %s, %s, 0)", (kode, pertanyaan, kategori))
        mysql.connection.commit()
        flash("Gejala berhasil ditambahkan!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Gagal: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('admin_manage_deteksi'))

@app.route("/admin/edit-gejala/<int:id>", methods=['POST'])
@login_required
def admin_edit_gejala(id):
    if current_user.role != 'admin': return redirect(url_for('home'))
    kode = request.form.get('kode_gejala')
    pertanyaan = request.form.get('pertanyaan')
    kategori = request.form.get('kategori')
    
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE gejala SET kode_gejala=%s, pertanyaan=%s, kategori=%s WHERE id_gejala=%s", (kode, pertanyaan, kategori, id))
        mysql.connection.commit()
        flash("Gejala berhasil diperbarui!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Gagal: {str(e)}", "danger")
    finally:
        cur.close()
    return redirect(url_for('admin_manage_deteksi'))

@app.route("/admin/delete-gejala/<int:id>")
@login_required
def admin_delete_gejala(id):
    if current_user.role != 'admin': return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM gejala WHERE id_gejala = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Gejala dihapus.", "success")
    return redirect(url_for('admin_manage_deteksi'))

@app.route("/admin/manage-pengguna")
@login_required
def admin_manage_pengguna():
    if current_user.role != 'admin': return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_user, username, email, role FROM users")
    users_list = cur.fetchall()
    cur.close()
    return render_template("admin/manage_pengguna.html", users=users_list)

@app.route("/admin/delete-user/<int:id>")
@login_required
def admin_delete_user(id):
    if current_user.role != 'admin': return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id_user = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Pengguna dihapus.", "success")
    return redirect(url_for('admin_manage_pengguna'))

@app.route("/admin/riwayat")
@login_required
def admin_riwayat():
    if current_user.role != 'admin': return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM riwayat_deteksi ORDER BY tanggal_deteksi DESC")
    riwayat_all = cur.fetchall()
    cur.close()
    return render_template("admin/riwayat_deteksi.html", riwayat=riwayat_all)

@app.route("/admin/delete-riwayat/<int:id>")
@login_required
def admin_delete_riwayat(id):
    if current_user.role != 'admin': return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM riwayat_deteksi WHERE id_riwayat = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Riwayat dihapus.", "success")
    return redirect(url_for('admin_riwayat'))

if __name__ == "__main__":
    app.run(debug=True)