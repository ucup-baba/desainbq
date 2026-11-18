import datetime as dt

import generate_kalender as gk
from kalender_data import RentangSholat, rentang_lima_hari, ringkas_sholat


def test_rentang_januari_berakhir_di_31():
    assert rentang_lima_hari(2027, 1) == [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25), (26, 31)]


def test_rentang_februari_2027_berakhir_di_28():
    assert rentang_lima_hari(2027, 2) == [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25), (26, 28)]


def test_tidak_ada_rentang_sisa_yang_kependekan():
    # Rentang terakhir menyerap sisa hari, bukan menyisakan potongan 1-2 hari.
    for bulan in range(1, 13):
        r = rentang_lima_hari(2027, bulan)
        assert r[-1][1] - r[-1][0] + 1 >= 3, (bulan, r)


def test_tiap_hari_tercakup_tepat_sekali():
    import calendar

    for bulan in range(1, 13):
        tercakup = [h for a, b in rentang_lima_hari(2027, bulan) for h in range(a, b + 1)]
        akhir = calendar.monthrange(2027, bulan)[1]
        assert tercakup == list(range(1, akhir + 1)), bulan


def test_sel_memuat_waktu_paling_akhir_dalam_rentang():
    hasil = ringkas_sholat(2027, 1)
    pertama = hasil[0]
    assert isinstance(pertama, RentangSholat)
    assert (pertama.dari, pertama.sampai) == (1, 5)
    for kunci in ("subuh", "dzuhur", "ashar", "maghrib", "isya"):
        harian = [gk.prayer_times_yogya(dt.date(2027, 1, h))[kunci] for h in range(1, 6)]
        assert getattr(pertama, kunci) == max(harian), kunci


def test_jumlah_rentang_enam_per_bulan():
    for bulan in range(1, 13):
        assert len(ringkas_sholat(2027, bulan)) == 6, bulan
