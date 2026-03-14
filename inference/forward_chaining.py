def hitung_insomnia(jawaban):

    total_skor = sum(jawaban)

    if total_skor <= 15:
        kategori = "Normal (Tidak Insomnia)"

    elif total_skor <= 30:
        kategori = "Insomnia Ringan"

    elif total_skor <= 45:
        kategori = "Insomnia Sedang"

    else:
        kategori = "Insomnia Berat"

    return total_skor, kategori