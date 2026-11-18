#!/usr/bin/env python3
"""Generator Kalender 2027 (3 Lembar, 4 Bulan/Lembar) untuk Yayasan Baitul Qowwam.

Fitur:
- Kalender Masehi 2027
- Kalender Hijriah (1448-1449 H, selaras Kemenag RI & SKB 3 Menteri 2027)
- Kalender Jawa (1960-1961 & Pasaran: Legi, Pahing, Pon, Wage, Kliwon)
- Jadwal Waktu Sholat Harian WIB Kota Yogyakarta & sekitarnya (metode Kemenag RI:
  Subuh 20 deg, Isya 18 deg, ihtiyati +2 menit)
- Daftar Hari Libur Nasional & Cuti Bersama 2027 (SKB 3 Menteri)
"""

from __future__ import annotations

import calendar
import datetime as dt
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Konfigurasi Lokasi: Kota Yogyakarta (WIB / UTC+7)
# ---------------------------------------------------------------------------
LAT = -7.7956
LON = 110.3695
TZ = 7.0
FAJR_ANGLE = 20.0   # Standar Kemenag RI
ISHA_ANGLE = 18.0   # Standar Kemenag RI
IHTIYATI_MIN = 2.0  # Pengaman +2 menit standar Kemenag RI

# ---------------------------------------------------------------------------
# Referensi 1 Januari 2027:
# - Jumat Pon
# - 23 Rajab 1448 H (Kemenag RI)
# - 22 Rejeb 1960 Jawa (Tahun Ba, Windu Sancaya)
# ---------------------------------------------------------------------------
PASARAN_NAMES = ("Legi", "Pahing", "Pon", "Wage", "Kliwon")
# 1 Jan 2027 = Pon (index 2)
BASE_DATE = dt.date(2027, 1, 1)
BASE_PASARAN_IDX = 2

DAY_NAMES_ID = ("Ahad", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu")
MONTH_NAMES_ID = (
    "",
    "JANUARI",
    "FEBRUARI",
    "MARET",
    "APRIL",
    "MEI",
    "JUNI",
    "JULI",
    "AGUSTUS",
    "SEPTEMBER",
    "OKTOBER",
    "NOVEMBER",
    "DESEMBER",
)

# Panjang bulan Hijriah 1448-1449 H selaras kalender Kemenag RI & SKB 3 Menteri 2027:
# 1 Jan 2027 = 23 Rajab 1448 H
# 5 Jan 2027 = 27 Rajab 1448 H (Isra Mikraj 1448 H)
# 10 Mar 2027 = 1 Syawal 1448 H (Idulfitri 1448 H)
# 17 Mei 2027 = 10 Dzulhijjah 1448 H (Iduladha 1448 H)
# 6 Jun 2027 = 1 Muharram 1449 H (Tahun Baru Islam 1449 H)
# 15 Agu 2027 = 12 Rabiul Awal 1449 H (Maulid Nabi 1449 H)
# 26 Des 2027 = 27 Rajab 1449 H (Isra Mikraj 1449 H)
HIJRI_MONTHS = [
    # (year, month_num, name_id, short_id, jawa_name, days)
    (1448, 7, "Rajab", "Raj", "Rejeb", 30),
    (1448, 8, "Sya'ban", "Syb", "Ruwah", 30),
    (1448, 9, "Ramadan", "Ram", "Pasa", 30),
    (1448, 10, "Syawal", "Syw", "Sawal", 29),
    (1448, 11, "Dzulqadah", "Dzq", "Sela", 30),
    (1448, 12, "Dzulhijjah", "Dzh", "Besar", 29),
    (1449, 1, "Muharram", "Muh", "Sura", 30),
    (1449, 2, "Safar", "Saf", "Sapar", 29),
    (1449, 3, "Rabiul Awal", "Raw", "Mulud", 30),
    (1449, 4, "Rabiul Akhir", "Rak", "Bakda Mulud", 29),
    (1449, 5, "Jumadil Awal", "Jaw", "Jumadil Awal", 30),
    (1449, 6, "Jumadil Akhir", "Jak", "Jumadil Akhir", 29),
    (1449, 7, "Rajab", "Raj", "Rejeb", 30),
    (1449, 8, "Sya'ban", "Syb", "Ruwah", 29),
]

# Hari Libur Nasional & Cuti Bersama 2027 (SKB 3 Menteri)
# type: "libur" | "cuti"
HOLIDAYS_2027: dict[dt.date, tuple[str, str]] = {
    dt.date(2027, 1, 1): ("libur", "Tahun Baru 2027 Masehi"),
    dt.date(2027, 1, 5): ("libur", "Isra Mikraj Nabi Muhammad SAW 1448 H"),
    dt.date(2027, 2, 5): ("cuti", "Cuti Bersama Tahun Baru Imlek"),
    dt.date(2027, 2, 6): ("libur", "Tahun Baru Imlek 2578 Kongzili"),
    dt.date(2027, 3, 8): ("libur", "Hari Suci Nyepi (Tahun Baru Saka 1949)"),
    dt.date(2027, 3, 9): ("cuti", "Cuti Bersama Hari Raya Idulfitri 1448 H"),
    dt.date(2027, 3, 10): ("libur", "Hari Raya Idulfitri 1448 H"),
    dt.date(2027, 3, 11): ("libur", "Hari Raya Idulfitri 1448 H"),
    dt.date(2027, 3, 12): ("cuti", "Cuti Bersama Hari Raya Idulfitri 1448 H"),
    dt.date(2027, 3, 15): ("cuti", "Cuti Bersama Hari Raya Idulfitri 1448 H"),
    dt.date(2027, 3, 25): ("cuti", "Cuti Bersama Wafat Yesus Kristus"),
    dt.date(2027, 3, 26): ("libur", "Wafat Yesus Kristus"),
    dt.date(2027, 3, 28): ("libur", "Kebangkitan Yesus Kristus (Paskah)"),
    dt.date(2027, 5, 1): ("libur", "Hari Buruh Internasional"),
    dt.date(2027, 5, 6): ("libur", "Kenaikan Yesus Kristus"),
    dt.date(2027, 5, 17): ("libur", "Hari Raya Iduladha 1448 H"),
    dt.date(2027, 5, 18): ("cuti", "Cuti Bersama Hari Raya Iduladha 1448 H"),
    dt.date(2027, 5, 19): ("cuti", "Cuti Bersama Hari Raya Waisak 2571 BE"),
    dt.date(2027, 5, 20): ("libur", "Hari Raya Waisak 2571 BE"),
    dt.date(2027, 6, 1): ("libur", "Hari Lahir Pancasila"),
    dt.date(2027, 6, 6): ("libur", "Tahun Baru Islam 1449 H"),
    dt.date(2027, 8, 15): ("libur", "Maulid Nabi Muhammad SAW 1449 H"),
    dt.date(2027, 8, 17): ("libur", "Hari Kemerdekaan Republik Indonesia"),
    dt.date(2027, 12, 24): ("cuti", "Cuti Bersama Hari Raya Natal"),
    dt.date(2027, 12, 25): ("libur", "Hari Raya Natal"),
    dt.date(2027, 12, 26): ("libur", "Isra Mikraj Nabi Muhammad SAW 1449 H"),
}


def get_pasaran(d: dt.date) -> str:
    delta = (d - BASE_DATE).days
    return PASARAN_NAMES[(BASE_PASARAN_IDX + delta) % 5]


def build_hijri_jawa_map() -> dict[dt.date, dict]:
    """Bangun peta tanggal Masehi 2027 -> Hijriah & Jawa."""
    # 1 Jan 2027 = 23 Rajab 1448 H, 22 Rejeb 1960 Jawa
    mapping: dict[dt.date, dict] = {}
    cur_date = dt.date(2027, 1, 1)
    end_date = dt.date(2027, 12, 31)

    m_idx = 0
    h_day = 23
    # Jawa 1960: Rejeb 30 hari, Ruwah 29, Pasa 30, Sawal 29, Sela 30, Besar 29
    # sehingga 1 Sura 1961 jatuh pada 6 Juni 2027 (selaras 1 Muharram 1449 H).
    jawa_months = [
        (1960, "Rejeb", 30),
        (1960, "Ruwah", 29),
        (1960, "Pasa", 30),
        (1960, "Sawal", 29),
        (1960, "Sela", 30),
        (1960, "Besar", 30),  # 22..30 Rejeb (9) + 29 + 30 + 29 + 30 + 30 = 157 hari? Mari hitung tepat!
    ]
    # Hitung selisih hari 1 Jan 2027 -> 6 Jun 2027:
    # Jan(30 tersisa) + Feb(28) + Mar(31) + Apr(30) + Mei(31) + Jun(6) = 156 hari.
    # 1 Jan = 22 Rejeb -> tersisa 23..30 Rejeb = 8 hari (jika Rejeb 30 hari).
    # 156 - 8 = 148 hari untuk Ruwah..Besar.
    # Ruwah(29) + Pasa(30) + Sawal(29) + Sela(30) + Besar(30) = 148 hari -> 6 Jun = 1 Sura 1961!
    jawa_months = [
        (1960, "Rejeb", 30),
        (1960, "Ruwah", 29),
        (1960, "Pasa", 30),
        (1960, "Sawal", 29),
        (1960, "Sela", 30),
        (1960, "Besar", 30),
        (1961, "Sura", 30),
        (1961, "Sapar", 29),
        (1961, "Mulud", 30),
        (1961, "Bakda Mulud", 29),
        (1961, "Jumadil Awal", 30),
        (1961, "Jumadil Akhir", 29),
        (1961, "Rejeb", 30),
        (1961, "Ruwah", 29),
    ]
    j_idx = 0
    j_day = 22

    while cur_date <= end_date:
        hy, hm, hname, hshort, _, hlen = HIJRI_MONTHS[m_idx]
        jy, jname, jlen = jawa_months[j_idx]

        mapping[cur_date] = {
            "h_year": hy,
            "h_month": hm,
            "h_name": hname,
            "h_short": hshort,
            "h_day": h_day,
            "j_year": jy,
            "j_name": jname,
            "j_day": j_day,
            "pasaran": get_pasaran(cur_date),
        }

        cur_date += dt.timedelta(days=1)
        h_day += 1
        if h_day > hlen:
            h_day = 1
            m_idx += 1

        j_day += 1
        if j_day > jlen:
            j_day = 1
            j_idx += 1

    return mapping


def _julian_day(d: dt.date) -> float:
    y, m, day = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + (a // 4)
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + b - 1524.5


def _sun_position(jd: float) -> tuple[float, float]:
    """Kembalikan (declination_deg, equation_of_time_hours)."""
    d = jd - 2451545.0
    g = math.radians((357.529 + 0.98560028 * d) % 360.0)
    q = (280.459 + 0.98564736 * d) % 360.0
    l = math.radians((q + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) % 360.0)
    e = math.radians(23.439 - 0.00000036 * d)

    ra = math.degrees(math.atan2(math.cos(e) * math.sin(l), math.cos(l))) / 15.0
    ra = ra % 24.0
    eqt = (q / 15.0) - ra
    if eqt > 12.0:
        eqt -= 24.0
    elif eqt < -12.0:
        eqt += 24.0

    decl = math.degrees(math.asin(math.sin(e) * math.sin(l)))
    return decl, eqt


def _hour_angle(lat_deg: float, decl_deg: float, angle_deg: float) -> float:
    lat = math.radians(lat_deg)
    decl = math.radians(decl_deg)
    alt = math.radians(-angle_deg)
    cos_ha = (math.sin(alt) - math.sin(lat) * math.sin(decl)) / (
        math.cos(lat) * math.cos(decl)
    )
    cos_ha = max(-1.0, min(1.0, cos_ha))
    return math.degrees(math.acos(cos_ha)) / 15.0


def _asr_hour_angle(lat_deg: float, decl_deg: float, shadow_factor: int = 1) -> float:
    lat = math.radians(lat_deg)
    decl = math.radians(decl_deg)
    angle = math.degrees(math.atan(1.0 / (shadow_factor + math.tan(abs(lat - decl)))))
    cos_ha = (math.sin(math.radians(angle)) - math.sin(lat) * math.sin(decl)) / (
        math.cos(lat) * math.cos(decl)
    )
    cos_ha = max(-1.0, min(1.0, cos_ha))
    return math.degrees(math.acos(cos_ha)) / 15.0


def _fmt_time(hours: float) -> str:
    total_min = round(hours * 60.0)
    hh = (total_min // 60) % 24
    mm = total_min % 60
    return f"{hh:02d}:{mm:02d}"


def prayer_times_yogya(d: dt.date) -> dict[str, str]:
    """Hitung jadwal sholat harian WIB untuk Kota Yogyakarta (metode Kemenag RI)."""
    jd = _julian_day(d) + 0.5 - (TZ / 24.0)
    decl, eqt = _sun_position(jd)
    dhuhr = 12.0 + TZ - (LON / 15.0) - eqt

    fajr = dhuhr - _hour_angle(LAT, decl, FAJR_ANGLE)
    asr = dhuhr + _asr_hour_angle(LAT, decl, 1)
    maghrib = dhuhr + _hour_angle(LAT, decl, 0.8333)
    isha = dhuhr + _hour_angle(LAT, decl, ISHA_ANGLE)

    ihtiyati = IHTIYATI_MIN / 60.0
    return {
        "subuh": _fmt_time(fajr + ihtiyati),
        "dzuhur": _fmt_time(dhuhr + ihtiyati),
        "ashar": _fmt_time(asr + ihtiyati),
        "maghrib": _fmt_time(maghrib + ihtiyati),
        "isya": _fmt_time(isha + ihtiyati),
    }

