import tema
from header import SLOT_FOTO, perintah_header
from kalender_data import bangun_lembar

LEMBAR = bangun_lembar(1)


def test_empat_slot_foto_satu_utama_tiga_pendukung():
    assert set(SLOT_FOTO) == {"foto_utama", "foto_1", "foto_2", "foto_3"}
    assert SLOT_FOTO["foto_utama"][0] > SLOT_FOTO["foto_1"][0]


def test_slot_foto_dibuat_sebagai_layer_bernama():
    nama = {p["as"] for p in perintah_header(LEMBAR, 0, 0)}
    assert set(SLOT_FOTO).issubset(nama)


def test_angka_tahun_memakai_font_display():
    tahun = next(p for p in perintah_header(LEMBAR, 0, 0) if p["as"] == "angka_tahun")
    assert tahun["params"]["props"]["fontFamily"] == tema.FONT_DISPLAY
    assert tahun["params"]["text"] == "2027"


def test_nama_yayasan_memakai_font_tangan():
    nama = next(p for p in perintah_header(LEMBAR, 0, 0) if p["as"] == "nama_yayasan")
    assert nama["params"]["props"]["fontFamily"] == tema.FONT_TANGAN


def test_penanda_periode_sesuai_nomor_lembar():
    for nomor, diharapkan in ((1, "JANUARI — APRIL"), (2, "MEI — AGUSTUS"),
                              (3, "SEPTEMBER — DESEMBER")):
        daftar = perintah_header(bangun_lembar(nomor), 0, 0)
        periode = next(p for p in daftar if p["as"] == "periode")
        assert diharapkan in periode["params"]["text"]
        assert f"{nomor}/3" in periode["params"]["text"]


def test_header_tidak_melebihi_anggaran_tingginya():
    daftar = perintah_header(LEMBAR, 0, 0.0)
    terbawah = max(
        p["params"]["y"] + p["params"].get("height", 0.0) for p in daftar
    )
    assert terbawah <= tema.TINGGI_HEADER, terbawah


def test_slot_foto_tidak_memakai_sudut_membulat():
    for p in perintah_header(LEMBAR, 0, 0):
        if p["as"] in SLOT_FOTO:
            assert "cornerRadius" not in p["params"]["props"]
