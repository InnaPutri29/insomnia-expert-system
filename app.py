from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from config import Config
from inference.forward_chaining import hitung_insomnia
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses halaman ini.'


# ===============================
# USER CLASS
# ===============================
class User(UserMixin):
    def __init__(self, id_admin, username):
        self.id = id_admin
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_admin, username FROM admin WHERE id_admin = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()

    if user_data:
        return User(user_data['id_admin'], user_data['username'])
    return None


# ===============================
# HOME
# ===============================
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


# ===============================
# EDUKASI
# ===============================
@app.route("/edukasi")
def edukasi():
    return render_template("edukasi.html")


# ===============================
# DETEKSI (AMBIL DARI DB)
# ===============================
@app.route("/deteksi")
@login_required
def deteksi():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM gejala ORDER BY id_gejala ASC")
    gejala = cur.fetchall()
    cur.close()

    return render_template("deteksi.html", gejala=gejala)


# ===============================
# PROSES DETEKSI (ISI + FORWARD CHAINING)
# ===============================
@app.route('/proses_deteksi', methods=['POST'])
@login_required
def proses_deteksi():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_gejala FROM gejala ORDER BY id_gejala ASC")
    gejala_db = cur.fetchall()
    cur.close()

    jawaban = []

    # Ambil jawaban user
    for g in gejala_db:
        nilai = request.form.get(f"q{g['id_gejala']}")

        if nilai is None:
            flash("Semua pertanyaan harus dijawab!", "danger")
            return redirect(url_for('deteksi'))

        jawaban.append(int(nilai))

    # ===============================
    # HITUNG (ISI + FORWARD CHAINING)
    # ===============================
    total_skor, hasil, fakta, kesimpulan = hitung_insomnia(jawaban)

    # ===============================
    # SIMPAN KE DATABASE
    # ===============================
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            """
            INSERT INTO riwayat_deteksi 
            (nama_user, skor_total, hasil_kategori, tanggal_deteksi) 
            VALUES (%s, %s, %s, %s)
            """,
            (current_user.username, total_skor, hasil, datetime.now())
        )
        mysql.connection.commit()
        flash("Hasil berhasil disimpan!", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Gagal menyimpan: {str(e)}", "danger")
    finally:
        cur.close()

    # ===============================
    # TAMPILKAN HASIL
    # ===============================
    return render_template(
        "hasil.html",
        skor=total_skor,
        kategori=hasil,
        fakta=fakta,
        kesimpulan=kesimpulan
    )


# ===============================
# RIWAYAT
# ===============================
@app.route("/riwayat")
@login_required
def riwayat():
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            SELECT * FROM riwayat_deteksi 
            WHERE nama_user = %s 
            ORDER BY tanggal_deteksi DESC
            """,
            (current_user.username,)
        )
        riwayat_data = cur.fetchall()
        cur.close()

        return render_template("riwayat.html", riwayat=riwayat_data)

    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return redirect(url_for('home'))


# ===============================
# REGISTER
# ===============================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Username dan password harus diisi!', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Password tidak cocok!', 'danger')
            return render_template('register.html')

        if len(password) < 4:
            flash('Password minimal 4 karakter!', 'danger')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO admin (username, password) VALUES (%s, %s)",
                (username, hashed)
            )
            mysql.connection.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            if "Duplicate entry" in str(e):
                flash('Username sudah digunakan.', 'danger')
            else:
                flash(f'Error: {str(e)}', 'danger')
        finally:
            cur.close()

    return render_template('register.html')


# ===============================
# LOGIN
# ===============================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()

        if user_data:
            stored_password = user_data['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                user = User(user_data['id_admin'], user_data['username'])
                login_user(user)
                flash('Login berhasil!', 'success')
                return redirect(url_for('home'))

        flash('Username atau password salah.', 'danger')

    return render_template('login.html')


# ===============================
# LOGOUT
# ===============================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('home'))


# ===============================
# ABOUT
# ===============================
@app.route("/about")
def about():
    return render_template("about.html")


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)