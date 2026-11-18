import tema
from blok_bulan import perintah_blok_bulan
from kalender_data import bangun_bulan

JAN = bangun_bulan(2027, 1)


def perintah(nama_awalan, daftar):
    return [p for p in daftar if p.get("as", "").startswith(nama_awalan)]


def test_menghasilkan_tujuh_nama_hari():
    assert len(perintah("hari_", perintah_blok_bulan(JAN, 0, 0))) == 7


def test_hanya_hari_dalam_bulan_yang_dibuat():
    # Januari 31 hari: 31 angka tanggal, bukan 42.
    assert len(perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))) == 31


def test_minggu_memakai_rust_dan_bukan_merah():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))
    tiga_jan = next(p for p in tgl if p["as"] == "tgl_3")   # 3 Jan 2027 = Minggu
    assert tiga_jan["params"]["props"]["fill"] == tema.PALET["rust"]


def test_hari_biasa_memakai_ink():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))
    empat_jan = next(p for p in tgl if p["as"] == "tgl_4")
    assert empat_jan["params"]["props"]["fill"] == tema.PALET["ink"]


def test_hari_libur_mendapat_alas_kuning():
    alas = perintah("alas_", perintah_blok_bulan(JAN, 0, 0))
    # 1 Jan (Tahun Baru) dan 5 Jan (Isra Mikraj)
    assert {p["as"] for p in alas} == {"alas_1", "alas_5"}
    assert alas[0]["params"]["props"]["fill"] == tema.PALET["sun"]


def test_angka_tanggal_memakai_font_teks_bukan_tulisan_tangan():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))
    for p in tgl:
        assert p["params"]["props"]["fontFamily"] == tema.FONT_TEKS


def test_nama_bulan_memakai_font_display():
    nama = next(p for p in perintah_blok_bulan(JAN, 0, 0) if p["as"] == "nama_bulan")
    assert nama["params"]["props"]["fontFamily"] == tema.FONT_DISPLAY
    assert nama["params"]["text"] == "JANUARI"


def test_posisi_tanggal_pertama_berada_di_kolom_jumat():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 100.0, 200.0))
    satu = next(p for p in tgl if p["as"] == "tgl_1")
    diharapkan = 100.0 + 5 * tema.LEBAR_KOLOM_HARI
    assert abs(satu["params"]["x"] - diharapkan) < tema.LEBAR_KOLOM_HARI


def test_seluruh_perintah_punya_nama_unik():
    daftar = perintah_blok_bulan(JAN, 0, 0)
    nama = [p["as"] for p in daftar]
    assert len(nama) == len(set(nama))


def test_tidak_ada_bayangan_atau_gradien():
    for p in perintah_blok_bulan(JAN, 0, 0):
        props = p["params"].get("props", {})
        assert "effects" not in props
        assert not str(props.get("fill", "")).startswith("{")
