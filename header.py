"""Perintah FigCraft untuk header lembar: identitas, angka tahun, slot foto."""

from __future__ import annotations

import tema
from blok_bulan import _bidang, _teks
from kalender_data import Lembar

LEBAR_KIRI = 139.0
LEBAR_KANAN = tema.LEBAR_ISI - LEBAR_KIRI - tema.GUTTER     # 244.0
TINGGI_UTAMA = 84.0
TINGGI_PENDUKUNG = 40.0
LEBAR_PENDUKUNG = (LEBAR_KANAN - 2 * 5.0) / 3

SLOT_FOTO: dict[str, tuple[float, float]] = {
    "foto_utama": (LEBAR_KANAN, TINGGI_UTAMA),
    "foto_1": (LEBAR_PENDUKUNG, TINGGI_PENDUKUNG),
    "foto_2": (LEBAR_PENDUKUNG, TINGGI_PENDUKUNG),
    "foto_3": (LEBAR_PENDUKUNG, TINGGI_PENDUKUNG),
}

PERIODE = {
    1: "JANUARI — APRIL",
    2: "MEI — AGUSTUS",
    3: "SEPTEMBER — DESEMBER",
}

_WARNA_SLOT = ("sun", "amber", "mint")


def perintah_header(lembar: Lembar, x: float, y: float,
                    induk: str | None = None) -> list[dict]:
    p = tema.PALET
    hasil: list[dict] = []

    # --- kolom kiri: identitas -------------------------------------------
    hasil.append(_teks("label_kalender", "KALENDER", x, y,
                       {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 3.0,
                        "fill": p["teal"], "letterSpacing": "2.6px"}, induk))
    hasil.append(_teks("angka_tahun", "2027", x - 2.0, y + 4.0,
                       {"fontFamily": tema.FONT_DISPLAY, "fontSize": tema.UKURAN["tahun"],
                        "fill": p["ink"], "rotation": 2.5}, induk))
    hasil.append(_teks("nama_yayasan", "Yayasan Islam\nBaitul Qowwam", x, y + 56.0,
                       {"fontFamily": tema.FONT_TANGAN,
                        "fontSize": tema.UKURAN["nama_yayasan"],
                        "fill": p["ink"], "lineHeight": "106%"}, induk))
    hasil.append(_teks("wilayah", "D.I. YOGYAKARTA", x, y + 78.0,
                       {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 2.9,
                        "fill": p["teal"], "letterSpacing": "1px"}, induk))
    hasil.append(_bidang("garis_identitas", x, y + 85.0, LEBAR_KIRI * 0.72, 0.7,
                         {"fill": p["ink"]}, induk))
    hasil.append(_teks("periode", f"{PERIODE[lembar.nomor]} · {lembar.nomor}/3",
                       x, y + 89.0,
                       {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 3.4,
                        "fill": p["ink"], "letterSpacing": "1.4px"}, induk))

    # --- kolom kanan: slot foto ------------------------------------------
    x_kanan = x + LEBAR_KIRI + tema.GUTTER
    hasil.append(_bidang("foto_utama", x_kanan, y, LEBAR_KANAN, TINGGI_UTAMA,
                         {"fill": p["mint"], "stroke": p["ink"], "strokeWeight": 0.7}, induk))
    hasil.append(_teks("label_foto_utama", "FOTO UTAMA KEGIATAN YAYASAN",
                       x_kanan, y + TINGGI_UTAMA / 2,
                       {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 2.8,
                        "fill": p["ink"], "textAlign": "center",
                        "letterSpacing": "0.5px"}, induk, LEBAR_KANAN))

    y_pendukung = y + TINGGI_UTAMA + 5.0
    for i in range(3):
        nama = f"foto_{i + 1}"
        slot_x = x_kanan + i * (LEBAR_PENDUKUNG + 5.0)
        hasil.append(_bidang(nama, slot_x, y_pendukung, LEBAR_PENDUKUNG, TINGGI_PENDUKUNG,
                             {"fill": p[_WARNA_SLOT[i]], "stroke": p["ink"],
                              "strokeWeight": 0.7}, induk))
        hasil.append(_teks(f"label_{nama}", f"FOTO {i + 1}",
                           slot_x, y_pendukung + TINGGI_PENDUKUNG / 2,
                           {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 2.8,
                            "fill": p["ink"], "textAlign": "center"},
                           induk, LEBAR_PENDUKUNG))
    return hasil
