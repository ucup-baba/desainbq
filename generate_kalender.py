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
import html
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


def render_month_html(
    year: int,
    month: int,
    hj_map: dict[dt.date, dict],
) -> str:
    cal = calendar.Calendar(firstweekday=6)  # Ahad sebagai hari pertama
    weeks = cal.monthdatescalendar(year, month)
    # Pastikan selalu 6 baris agar tinggi ke-4 bulan seragam rapi
    while len(weeks) < 6:
        last_day = weeks[-1][-1]
        weeks.append([last_day + dt.timedelta(days=i + 1) for i in range(7)])

    month_days = [
        dt.date(year, month, day)
        for day in range(1, calendar.monthrange(year, month)[1] + 1)
    ]
    first_info = hj_map[month_days[0]]
    last_info = hj_map[month_days[-1]]

    if first_info["h_name"] == last_info["h_name"]:
        hijri_span = f"{first_info['h_name']} {first_info['h_year']} H"
    elif first_info["h_year"] == last_info["h_year"]:
        hijri_span = f"{first_info['h_name']} – {last_info['h_name']} {first_info['h_year']} H"
    else:
        hijri_span = (
            f"{first_info['h_name']} {first_info['h_year']} – "
            f"{last_info['h_name']} {last_info['h_year']} H"
        )

    if first_info["j_name"] == last_info["j_name"]:
        jawa_span = f"{first_info['j_name']} {first_info['j_year']}"
    elif first_info["j_year"] == last_info["j_year"]:
        jawa_span = f"{first_info['j_name']} – {last_info['j_name']} {first_info['j_year']}"
    else:
        jawa_span = (
            f"{first_info['j_name']} {first_info['j_year']} – "
            f"{last_info['j_name']} {last_info['j_year']}"
        )

    rows_html = []
    for week in weeks:
        cells = []
        for idx, d in enumerate(week):
            if d.month != month:
                cells.append('<td class="cell empty"></td>')
                continue

            info = hj_map[d]
            pt = prayer_times_yogya(d)
            holiday = HOLIDAYS_2027.get(d)
            is_sunday = idx == 0
            is_friday = idx == 5

            classes = ["cell"]
            if is_sunday or (holiday and holiday[0] == "libur"):
                classes.append("holiday")
            elif holiday and holiday[0] == "cuti":
                classes.append("cuti")
            elif is_friday:
                classes.append("friday")

            h_label = (
                f"{info['h_day']} {info['h_short']}"
                if info["h_day"] == 1 or d.day == 1
                else f"{info['h_day']}"
            )
            j_label = f"{info['j_day']} {info['pasaran']}"
            title_attr = f' title="{html.escape(holiday[1])}"' if holiday else ""

            cell_html = f"""
            <td class="{' '.join(classes)}"{title_attr}>
              <div class="cell-top">
                <span class="m-day">{d.day}</span>
                <div class="sub-dates">
                  <span class="h-day">{html.escape(h_label)}</span>
                  <span class="j-day">{html.escape(j_label)}</span>
                </div>
              </div>
              <div class="prayer-grid">
                <span><b>S</b> {pt['subuh']}</span><span><b>D</b> {pt['dzuhur']}</span>
                <span><b>A</b> {pt['ashar']}</span><span><b>M</b> {pt['maghrib']}</span>
                <span><b>I</b> {pt['isya']}</span><span class="wib-tag">WIB</span>
              </div>
            </td>"""
            cells.append(cell_html)
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    headers = "".join(
        f'<th class="{"sun" if i == 0 else "fri" if i == 5 else ""}">{name}</th>'
        for i, name in enumerate(DAY_NAMES_ID)
    )

    return f"""
    <section class="month-card">
      <div class="month-header">
        <div class="month-title">{MONTH_NAMES_ID[month]} {year}</div>
        <div class="month-sub">
          <span class="hijri-badge">{html.escape(hijri_span)}</span>
          <span class="jawa-badge">{html.escape(jawa_span)}</span>
        </div>
      </div>
      <table class="cal-table">
        <thead><tr>{headers}</tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
      </table>
    </section>
    """


def render_sheet_html(
    sheet_num: int,
    months: list[int],
    hj_map: dict[dt.date, dict],
) -> str:
    period_label = f"{MONTH_NAMES_ID[months[0]]} – {MONTH_NAMES_ID[months[-1]]} 2027"
    month_cards = "".join(render_month_html(2027, m, hj_map) for m in months)

    # Kumpulkan hari libur & cuti bersama pada 4 bulan lembar ini
    sheet_holidays = [
        (d, kind, desc)
        for d, (kind, desc) in sorted(HOLIDAYS_2027.items())
        if d.month in months
    ]
    holiday_items = []
    for d, kind, desc in sheet_holidays:
        badge_cls = "badge-libur" if kind == "libur" else "badge-cuti"
        tag = "Libur" if kind == "libur" else "Cuti"
        m_short = MONTH_NAMES_ID[d.month][:3].title()
        holiday_items.append(
            f'<li><span class="{badge_cls}">{d.day} {m_short}</span> '
            f'({tag}) {html.escape(desc)}</li>'
        )

    return f"""
    <div class="sheet">
      <header class="sheet-header">
        <div class="brand-left">
          <div class="logo-placeholder" aria-label="Placeholder Logo Yayasan Baitul Qowwam">
            <svg viewBox="0 0 64 64" width="44" height="44" xmlns="http://www.w3.org/2000/svg">
              <rect x="2" y="2" width="60" height="60" rx="12" fill="#f0f7f4" stroke="#0f5c46" stroke-width="2" stroke-dasharray="4 3"/>
              <path d="M32 12 L37 25 L50 25 L39.5 33 L43.5 46 L32 38 L20.5 46 L24.5 33 L14 25 L27 25 Z" fill="none" stroke="#0f5c46" stroke-width="2"/>
              <text x="32" y="56" text-anchor="middle" font-size="7" font-family="sans-serif" fill="#0f5c46" font-weight="bold">LOGO</text>
            </svg>
          </div>
          <div class="brand-text">
            <div class="yayasan-kicker">KALENDER RESMI • PLACEHOLDER IDENTITAS</div>
            <h1 class="yayasan-name">YAYASAN BAITUL QOWWAM</h1>
            <div class="yayasan-sub">Jl. [Alamat Yayasan Baitul Qowwam], D.I. Yogyakarta • Telp/WA: [08xx-xxxx-xxxx]</div>
          </div>
        </div>

        <div class="header-right">
          <div class="year-pill">2027</div>
          <div class="period-box">
            <div class="period-title">{period_label}</div>
            <div class="period-meta">Masehi • Hijriah (1448–1449 H) • Jawa (1960–1961)</div>
            <div class="prayer-loc">Jadwal Sholat Harian WIB: Kota Yogyakarta &amp; Sekitarnya (Kemenag RI, Ihtiyati +2')</div>
          </div>
          <div class="sheet-badge">Lembar {sheet_num} / 3</div>
        </div>
      </header>

      <main class="months-grid">
        {month_cards}
      </main>

      <footer class="sheet-footer">
        <div class="holidays-box">
          <div class="footer-title">Hari Libur Nasional &amp; Cuti Bersama ({period_label.title()})</div>
          <ul class="holiday-list">
            {''.join(holiday_items)}
          </ul>
        </div>
        <div class="legend-box">
          <div class="footer-title">Keterangan &amp; Selisih Waktu DIY</div>
          <div class="legend-row"><b>Waktu Sholat:</b> <b>S</b> Subuh • <b>D</b> Dzuhur • <b>A</b> Ashar • <b>M</b> Maghrib • <b>I</b> Isya (WIB)</div>
          <div class="legend-row"><b>Koreksi DIY:</b> Kota Yogya / Sleman / Bantul <b>±0'</b> • Kulon Progo <b>+1'</b> • Gunungkidul <b>-1'</b></div>
          <div class="legend-row"><b>Catatan:</b> Penetapan awal Ramadan, Idulfitri &amp; Iduladha mengikuti Sidang Isbat Kemenag RI.</div>
        </div>
      </footer>
    </div>
    """


def generate_html() -> str:
    hj_map = build_hijri_jawa_map()
    sheets = [
        render_sheet_html(1, [1, 2, 3, 4], hj_map),
        render_sheet_html(2, [5, 6, 7, 8], hj_map),
        render_sheet_html(3, [9, 10, 11, 12], hj_map),
    ]

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8" />
  <title>Kalender 2027 — Yayasan Baitul Qowwam (DIY)</title>
  <style>
    @page {{
      size: A3 portrait;
      margin: 8mm;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
      color: #1c2422;
      background: #e9eceb;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    .sheet {{
      width: 281mm;
      height: 404mm;
      margin: 0 auto 10mm auto;
      background: #ffffff;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 4mm 4mm 3mm 4mm;
      page-break-after: always;
      break-after: page;
    }}
    .sheet:last-child {{
      page-break-after: auto;
      break-after: auto;
      margin-bottom: 0;
    }}
    @media print {{
      body {{
        background: #ffffff;
      }}
      .sheet {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 403mm;
      }}
    }}

    /* Header */
    .sheet-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(135deg, #0b4f3c 0%, #146c53 65%, #1d8366 100%);
      color: #ffffff;
      border-radius: 3mm;
      padding: 3.5mm 4.5mm;
      border-bottom: 1.2mm solid #d4a644;
    }}
    .brand-left {{
      display: flex;
      align-items: center;
      gap: 3.5mm;
    }}
    .logo-placeholder {{
      background: #ffffff;
      border-radius: 2.5mm;
      padding: 1.2mm;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 1px 3px rgba(0,0,0,0.18);
    }}
    .yayasan-kicker {{
      font-size: 6.5pt;
      letter-spacing: 0.9px;
      color: #f3d78a;
      font-weight: 700;
    }}
    .yayasan-name {{
      font-size: 16pt;
      font-weight: 800;
      letter-spacing: 0.4px;
      line-height: 1.15;
    }}
    .yayasan-sub {{
      font-size: 7.2pt;
      color: #d9efe7;
      margin-top: 0.6mm;
    }}
    .header-right {{
      display: flex;
      align-items: center;
      gap: 3.5mm;
      text-align: right;
    }}
    .year-pill {{
      background: #d4a644;
      color: #0b3327;
      font-size: 19pt;
      font-weight: 900;
      padding: 1.5mm 3.5mm;
      border-radius: 2.2mm;
      line-height: 1;
    }}
    .period-title {{
      font-size: 11.5pt;
      font-weight: 800;
      letter-spacing: 0.4px;
    }}
    .period-meta {{
      font-size: 7.2pt;
      color: #e6f4ef;
      margin-top: 0.5mm;
    }}
    .prayer-loc {{
      font-size: 6.6pt;
      color: #f6df9d;
      margin-top: 0.4mm;
      font-weight: 600;
    }}
    .sheet-badge {{
      background: rgba(255,255,255,0.16);
      border: 0.3mm solid rgba(255,255,255,0.35);
      border-radius: 2mm;
      padding: 1.5mm 2.5mm;
      font-size: 7.5pt;
      font-weight: 700;
      white-space: nowrap;
    }}

    /* 2x2 Months Grid */
    .months-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 3.5mm;
      flex: 1;
      margin: 3mm 0;
    }}
    .month-card {{
      border: 0.35mm solid #b8cbc4;
      border-radius: 2.5mm;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      background: #ffffff;
    }}
    .month-header {{
      background: #eff6f3;
      border-bottom: 0.45mm solid #0f5c46;
      padding: 1.8mm 2.8mm;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}
    .month-title {{
      font-size: 11.5pt;
      font-weight: 800;
      color: #0b4f3c;
      letter-spacing: 0.4px;
    }}
    .month-sub {{
      display: flex;
      gap: 2mm;
      font-size: 6.8pt;
      font-weight: 600;
    }}
    .hijri-badge {{
      background: #0f5c46;
      color: #ffffff;
      padding: 0.5mm 1.8mm;
      border-radius: 1.2mm;
    }}
    .jawa-badge {{
      background: #f5ebd1;
      color: #6b4e11;
      border: 0.25mm solid #d8be7a;
      padding: 0.5mm 1.8mm;
      border-radius: 1.2mm;
    }}

    /* Calendar Table */
    .cal-table {{
      width: 100%;
      flex: 1;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    .cal-table th {{
      background: #146c53;
      color: #ffffff;
      font-size: 6.8pt;
      font-weight: 700;
      padding: 1mm 0;
      border-right: 0.25mm solid #2a856b;
      text-transform: uppercase;
    }}
    .cal-table th:last-child {{
      border-right: none;
    }}
    .cal-table th.sun {{
      background: #a62626;
    }}
    .cal-table th.fri {{
      background: #0b4f3c;
    }}
    .cal-table td.cell {{
      border-top: 0.25mm solid #d7e2de;
      border-right: 0.25mm solid #d7e2de;
      padding: 0.9mm 1.1mm;
      vertical-align: top;
      height: 24.5mm;
    }}
    .cal-table td.cell:last-child {{
      border-right: none;
    }}
    .cal-table td.cell.empty {{
      background: #f8faf9;
    }}
    .cal-table td.cell.holiday {{
      background: #fff6f6;
    }}
    .cal-table td.cell.holiday .m-day {{
      color: #b91c1c;
    }}
    .cal-table td.cell.cuti {{
      background: #fffbeb;
    }}
    .cal-table td.cell.cuti .m-day {{
      color: #b45309;
    }}
    .cal-table td.cell.friday {{
      background: #f4fbf8;
    }}
    .cal-table td.cell.friday .m-day {{
      color: #0b5c44;
    }}

    .cell-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.7mm;
    }}
    .m-day {{
      font-size: 11.5pt;
      font-weight: 800;
      line-height: 1;
      color: #16221f;
    }}
    .sub-dates {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      line-height: 1.12;
    }}
    .h-day {{
      font-size: 5.8pt;
      font-weight: 700;
      color: #0f5c46;
    }}
    .j-day {{
      font-size: 5.2pt;
      color: #6b5320;
      font-weight: 600;
    }}

    /* Prayer Times Micro-Grid inside each cell */
    .prayer-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.2mm 0.8mm;
      border-top: 0.2mm dashed #d1ded9;
      padding-top: 0.6mm;
      font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
      font-size: 4.85pt;
      line-height: 1.22;
      color: #2f3e39;
    }}
    .prayer-grid b {{
      color: #0b4f3c;
      font-weight: 700;
    }}
    .prayer-grid .wib-tag {{
      color: #7c8d87;
      text-align: right;
      font-size: 4.3pt;
      align-self: center;
    }}

    /* Footer */
    .sheet-footer {{
      display: grid;
      grid-template-columns: 1.45fr 1fr;
      gap: 3.5mm;
      background: #f5f9f7;
      border: 0.3mm solid #c5d6d0;
      border-radius: 2.5mm;
      padding: 2.3mm 3.2mm;
    }}
    .footer-title {{
      font-size: 7.2pt;
      font-weight: 800;
      color: #0b4f3c;
      margin-bottom: 1mm;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }}
    .holiday-list {{
      list-style: none;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.6mm 2.5mm;
      font-size: 6.1pt;
      line-height: 1.25;
    }}
    .badge-libur {{
      background: #fee2e2;
      color: #991b1b;
      font-weight: 700;
      padding: 0.1mm 1mm;
      border-radius: 0.8mm;
    }}
    .badge-cuti {{
      background: #fef3c7;
      color: #92400e;
      font-weight: 700;
      padding: 0.1mm 1mm;
      border-radius: 0.8mm;
    }}
    .legend-row {{
      font-size: 6.2pt;
      line-height: 1.38;
      color: #2c3834;
    }}
  </style>
</head>
<body>
  {''.join(sheets)}
</body>
</html>
"""


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    html_path = out_dir / "kalender-baitul-qowwam-2027.html"
    html_path.write_text(generate_html(), encoding="utf-8")
    print(f"Generated: {html_path}")


if __name__ == "__main__":
    main()
