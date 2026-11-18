import tema


def test_palet_tepat_tujuh_warna():
    assert len(tema.PALET) == 7
    assert set(tema.PALET) == {"ink", "teal", "mint", "paper", "sun", "amber", "rust"}
    for nilai in tema.PALET.values():
        assert nilai.startswith("#") and len(nilai) == 7


def test_lebar_area_kerja_sesuai_spec():
    assert tema.LEBAR_ISI == 392.0
    assert tema.LEBAR_BULAN == (392.0 - tema.GUTTER) / 2


def test_isi_muat_di_halaman_dan_menyisakan_ruang_nafas():
    a = tema.anggaran_vertikal()
    assert a["terpakai"] < tema.TINGGI_HALAMAN - 2 * tema.MARGIN
    assert 30.0 <= a["sisa"] <= 55.0, a


def test_blok_bulan_setinggi_komponennya():
    a = tema.anggaran_vertikal()
    assert abs(a["tinggi_bulan"] - (tema.TINGGI_KEPALA_BULAN + tema.TINGGI_BARIS_HARI
                                    + 6 * tema.TINGGI_SEL + tema.TINGGI_KET_LIBUR)) < 0.01


def test_tidak_ada_warna_merah_murni():
    # Spec: peran "merah" diambil rust; merah murni tidak boleh masuk.
    assert "#FF0000" not in tema.PALET.values()
    assert tema.PALET["rust"] == "#A64F03"
