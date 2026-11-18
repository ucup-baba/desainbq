import tema
from build_kalender import perintah_lembar
from kalender_data import bangun_lembar

LEMBAR = bangun_lembar(1)
PERINTAH = perintah_lembar(LEMBAR)


def test_memuat_header_empat_bulan_dan_pita():
    nama = {p["as"] for p in PERINTAH}
    assert "angka_tahun" in nama
    assert "judul_pita" in nama
    assert sum(1 for n in nama if n.startswith("bulan_1_nama_bulan")) == 1


def test_nama_perintah_unik_di_seluruh_halaman():
    nama = [p["as"] for p in PERINTAH]
    assert len(nama) == len(set(nama)), [n for n in nama if nama.count(n) > 1][:5]


def test_kertas_menutupi_halaman_sampai_area_bleed():
    kertas = next(p for p in PERINTAH if p["as"] == "kertas")
    assert kertas["params"]["props"]["fill"] == tema.PALET["paper"]
    assert kertas["params"]["x"] < 0 and kertas["params"]["y"] < 0
    assert kertas["params"]["width"] > tema.LEBAR_HALAMAN
    assert kertas["params"]["height"] > tema.TINGGI_HALAMAN
    assert PERINTAH[0]["as"] == "kertas", "kertas harus layer paling bawah"


def test_semua_elemen_di_dalam_margin():
    # Kertas sengaja melewati margin: ia menutupi area bleed.
    for p in (q for q in PERINTAH if q["as"] != "kertas"):
        assert p["params"]["x"] >= tema.MARGIN - 3.0, p["as"]
        assert p["params"]["x"] <= tema.LEBAR_HALAMAN - tema.MARGIN + 3.0, p["as"]
        assert p["params"]["y"] >= tema.MARGIN - 3.0, p["as"]
        assert p["params"]["y"] <= tema.TINGGI_HALAMAN - tema.MARGIN, p["as"]


def test_jumlah_perintah_wajar():
    # 4 bulan × (±31 hari × 3 teks) + kisi + pita + header
    assert 500 < len(PERINTAH) < 1200, len(PERINTAH)


# --- konversi satuan ----------------------------------------------------
from build_kalender import MM_KE_PT, ke_titik  # noqa: E402


def test_konversi_mm_ke_pt_pada_koordinat_dan_ukuran():
    asal = [{"command": "node.create", "as": "x",
             "params": {"x": 10.0, "y": 20.0, "width": 100.0, "height": 50.0,
                        "props": {"fontSize": 8.4, "strokeWeight": 0.7,
                                  "letterSpacing": "0.5px", "fill": "#024959"}}}]
    jadi = ke_titik(asal)[0]["params"]
    assert jadi["x"] == round(10.0 * MM_KE_PT, 4)
    assert jadi["width"] == round(100.0 * MM_KE_PT, 4)
    assert jadi["props"]["fontSize"] == round(8.4 * MM_KE_PT, 4)
    assert jadi["props"]["letterSpacing"] == f"{round(0.5 * MM_KE_PT, 4)}px"
    assert jadi["props"]["fill"] == "#024959", "warna tidak boleh ikut diskalakan"


def test_konversi_tidak_merusak_perintah_asli():
    asal = [{"command": "node.create", "as": "x", "params": {"x": 10.0, "props": {"fontSize": 4.0}}}]
    ke_titik(asal)
    assert asal[0]["params"]["x"] == 10.0, "daftar asal harus tetap dalam mm"


def test_lembar_a2_dalam_titik_mendekati_ukuran_sebenarnya():
    kertas = ke_titik([p for p in PERINTAH if p["as"] == "kertas"])[0]["params"]
    # A2 420x594 mm + bleed 3 mm keliling = 426 x 600 mm
    assert abs(kertas["width"] - 426.0 * MM_KE_PT) < 0.1
    assert abs(kertas["height"] - 600.0 * MM_KE_PT) < 0.1
    assert abs(kertas["width"] - 1207.6) < 1.0, kertas["width"]
