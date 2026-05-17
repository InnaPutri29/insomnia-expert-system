def hitung_insomnia(jawaban):
    total_skor = sum(jawaban)

    # =====================
    # KATEGORI (ISI)
    # =====================
    if total_skor <= 7:
        kategori = "Tidak Insomnia"
    elif total_skor <= 14:
        kategori = "Insomnia Ringan"
    elif total_skor <= 21:
        kategori = "Insomnia Sedang"
    else:
        kategori = "Insomnia Berat"

    # =====================
    # FORWARD CHAINING
    # =====================
    fakta = []
    kesimpulan = []

    # mapping fakta dari jawaban
    if jawaban[0] >= 2:
        fakta.append("Sulit memulai tidur")

    if jawaban[1] >= 2:
        fakta.append("Sulit mempertahankan tidur")

    if jawaban[2] >= 2:
        fakta.append("Bangun terlalu pagi")

    if jawaban[4] >= 2:
        fakta.append("Gangguan aktivitas siang hari")

    if jawaban[6] >= 2:
        fakta.append("Kecemasan terhadap tidur")

    # rule-based inference
    if "Sulit memulai tidur" in fakta and "Kecemasan terhadap tidur" in fakta:
        kesimpulan.append("Insomnia dipengaruhi oleh kecemasan")

    if "Gangguan aktivitas siang hari" in fakta:
        kesimpulan.append("Insomnia berdampak pada aktivitas harian")

    if "Bangun terlalu pagi" in fakta:
        kesimpulan.append("Gangguan pola tidur di pagi hari")

    return total_skor, kategori, fakta, kesimpulan