import tema
from kalender_data import bangun_lembar
from pita_sholat import perintah_pita_sholat

LEMBAR = bangun_lembar(1)


def test_empat_kolom_bulan():
    judul = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
             if p.get("as", "").startswith("judul_bulan_")]
    assert len(judul) == 4
    assert judul[0]["params"]["text"] == "JANUARI"


def test_enam_baris_rentang_per_bulan():
    baris = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
             if p.get("as", "").startswith("rentang_1_")]
    assert len(baris) == 6
    assert baris[0]["params"]["text"] == "1–5"


def test_kolom_maghrib_ditandai_kuning():
    alas = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
            if p.get("as", "").startswith("alas_maghrib_")]
    assert len(alas) == 4           # satu per bulan
    assert alas[0]["params"]["props"]["fill"] == tema.PALET["sun"]


def test_waktu_memakai_angka_lebar_seragam():
    waktu = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
             if p.get("as", "").startswith("waktu_")]
    assert waktu, "tidak ada sel waktu"
    for p in waktu:
        assert p["params"]["props"]["features"] == {"tnum": True}


def test_memuat_catatan_koreksi_wilayah():
    teks = " ".join(p["params"].get("text", "") for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0))
    assert "Kulon Progo" in teks and "Gunungkidul" in teks


def test_pita_tidak_melebihi_anggaran_tingginya():
    daftar = perintah_pita_sholat(LEMBAR.bulan, 0, 0.0)
    terbawah = max(p["params"]["y"] for p in daftar)
    assert terbawah <= tema.TINGGI_PITA_SHOLAT, terbawah
