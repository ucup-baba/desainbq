"""Token desain kalender. Satu unit FigCraft = 1 mm."""

from __future__ import annotations

# --- Halaman -----------------------------------------------------------
LEBAR_HALAMAN = 420.0
TINGGI_HALAMAN = 594.0
MARGIN = 14.0
GUTTER = 9.0
BLEED = "3mm"
LEBAR_ISI = LEBAR_HALAMAN - 2 * MARGIN          # 392.0
LEBAR_BULAN = (LEBAR_ISI - GUTTER) / 2          # 191.5

# --- Blok bulan --------------------------------------------------------
TINGGI_KEPALA_BULAN = 15.0
TINGGI_BARIS_HARI = 7.0
TINGGI_SEL = 18.4
TINGGI_KET_LIBUR = 10.0
LEBAR_KOLOM_HARI = LEBAR_BULAN / 7

# --- Blok lain ---------------------------------------------------------
TINGGI_HEADER = 129.0
TINGGI_PITA_SHOLAT = 70.0
TINGGI_KAKI = 10.0
JEDA_HEADER = 10.0
JEDA_PITA = 12.0

# --- Palet -------------------------------------------------------------
PALET = {
    "ink": "#024959",
    "teal": "#038C8C",
    "mint": "#6EC4C0",
    "paper": "#F2EEED",
    "sun": "#F9D83F",
    "amber": "#F29F05",
    "rust": "#A64F03",
}

# --- Font --------------------------------------------------------------
FONT_DISPLAY = "Caveat Brush"      # angka tahun, nama bulan
FONT_TANGAN = "Patrick Hand"       # nama yayasan
FONT_TEKS = "Plus Jakarta Sans"    # seluruh data

UKURAN = {
    "tahun": 52.0,
    "nama_bulan": 11.0,
    "nama_yayasan": 9.4,
    "tanggal": 8.4,
    "nama_hari": 3.0,
    "hijriah": 2.9,
    "jawa": 2.9,
    "sholat": 3.3,
    "ket_libur": 2.9,
}


def anggaran_vertikal() -> dict[str, float]:
    """Berapa tinggi yang dipakai tiap blok, dan berapa yang tersisa.

    Sisa ruang disebar sebagai ruang kosong antar blok, bukan dipadatkan:
    pada kalender dinding, ruang kosong yang membuatnya terbaca dari jauh.
    """
    tinggi_bulan = (
        TINGGI_KEPALA_BULAN + TINGGI_BARIS_HARI + 6 * TINGGI_SEL + TINGGI_KET_LIBUR
    )
    grid = tinggi_bulan * 2 + GUTTER
    terpakai = (
        TINGGI_HEADER + JEDA_HEADER + grid + JEDA_PITA + TINGGI_PITA_SHOLAT + TINGGI_KAKI
    )
    return {
        "tinggi_bulan": tinggi_bulan,
        "grid": grid,
        "terpakai": terpakai,
        "sisa": TINGGI_HALAMAN - 2 * MARGIN - terpakai,
    }
