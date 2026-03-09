from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/deteksi")
def deteksi():
    return render_template("deteksi.html")

@app.route("/edukasi")
def edukasi():
    return render_template("edukasi.html")

if __name__ == "__main__":
    app.run(debug=True)