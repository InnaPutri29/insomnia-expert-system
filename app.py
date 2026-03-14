from flask import Flask, render_template, request
from inference.forward_chaining import hitung_insomnia
from config import pertanyaan

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/edukasi")
def edukasi():
    return render_template("edukasi.html")

@app.route("/deteksi")
def deteksi():
    return render_template("deteksi.html", pertanyaan=pertanyaan)

@app.route('/proses_deteksi', methods=['POST'])
def proses_deteksi():

    jawaban = []

    for i in range(1, 21):
        nilai = int(request.form.get(f"q{i}", 0))
        jawaban.append(nilai)

    total_skor, kategori = hitung_insomnia(jawaban)

    return render_template(
        "hasil.html",
        skor=total_skor,
        kategori=kategori
    )

if __name__ == "__main__":
    app.run(debug=True)