import calendar
import datetime as dt

import generate_kalender as gk
from kalender_data import bangun_bulan

PETA = gk.build_hijri_jawa_map()


def test_seluruh_365_hari_cocok_dengan_sumbernya():
    jumlah = 0
    for bulan in range(1, 13):
        for hari in bangun_bulan(2027, bulan).hari:
            asli = PETA[hari.tanggal]
            assert hari.hijriah_hari == asli["h_day"], hari.tanggal
            assert hari.hijriah_nama == asli["h_name"], hari.tanggal
            assert hari.jawa_hari == asli["j_day"], hari.tanggal
            assert hari.pasaran == asli["pasaran"], hari.tanggal
            jumlah += 1
    assert jumlah == 365


def test_setiap_hari_libur_nasional_muncul_di_modelnya():
    ditemukan = {
        h.tanggal
        for bulan in range(1, 13)
        for h in bangun_bulan(2027, bulan).hari
        if h.libur
    }
    assert ditemukan == set(gk.HOLIDAYS_2027)


def test_waktu_sholat_rentang_tidak_pernah_lebih_awal_dari_hari_mana_pun():
    for bulan in range(1, 13):
        for r in bangun_bulan(2027, bulan).sholat:
            for hari in range(r.dari, r.sampai + 1):
                harian = gk.prayer_times_yogya(dt.date(2027, bulan, hari))
                for kunci in ("subuh", "dzuhur", "ashar", "maghrib", "isya"):
                    assert getattr(r, kunci) >= harian[kunci], (bulan, hari, kunci)


def test_jumlah_hari_tiap_bulan_benar():
    for bulan in range(1, 13):
        assert len(bangun_bulan(2027, bulan).hari) == calendar.monthrange(2027, bulan)[1]
