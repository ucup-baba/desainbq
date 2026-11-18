"""Perintah FigCraft untuk pita jadwal sholat di kaki lembar."""

from __future__ import annotations

import tema
from blok_bulan import _bidang, _teks
from kalender_data import Bulan

KEPALA = ("Subuh", "Dzuhur", "Ashar", "Maghrib", "Isya")
LEBAR_KOLOM_TGL = 11.0
TINGGI_BARIS = 6.2
KOREKSI = ("Koreksi wilayah: Yogyakarta / Sleman / Bantul ±0 menit  ·  "
           "Kulon Progo +1 menit  ·  Gunungkidul −1 menit")


def perintah_pita_sholat(bulan: tuple[Bulan, ...], x: float, y: float,
                         induk: str | None = None) -> list[dict]:
    p = tema.PALET
    hasil: list[dict] = []

    hasil.append(_teks("judul_pita",
                       "JADWAL SHOLAT WIB  ·  D.I. YOGYAKARTA & SEKITARNYA  ·  PER 5 HARI",
                       x, y,
                       {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 3.9,
                        "fill": p["ink"], "letterSpacing": "0.8px"}, induk))
    hasil.append(_bidang("garis_pita", x, y + 5.5, tema.LEBAR_ISI, 0.7,
                         {"fill": p["ink"]}, induk))

    lebar_kolom_bulan = (tema.LEBAR_ISI - 3 * tema.GUTTER) / 4
    lebar_waktu = (lebar_kolom_bulan - LEBAR_KOLOM_TGL) / 5
    y_judul = y + 9.0
    y_kepala = y_judul + 5.0
    y_baris0 = y_kepala + 4.6

    for i, b in enumerate(bulan):
        kolom_x = x + i * (lebar_kolom_bulan + tema.GUTTER)

        # alas kolom Maghrib: paling sering dicari, jadi ditandai
        x_maghrib = kolom_x + LEBAR_KOLOM_TGL + 3 * lebar_waktu
        hasil.append(_bidang(f"alas_maghrib_{b.nomor}", x_maghrib, y_kepala - 1.0,
                             lebar_waktu, TINGGI_BARIS * len(b.sholat) + 5.6,
                             {"fill": p["sun"], "opacity": 0.45}, induk))

        hasil.append(_teks(f"judul_bulan_{b.nomor}", b.nama, kolom_x, y_judul,
                           {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold",
                            "fontSize": 3.7, "fill": p["teal"],
                            "letterSpacing": "0.5px"}, induk))

        hasil.append(_teks(f"kepala_tgl_{b.nomor}", "TGL", kolom_x, y_kepala,
                           {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold",
                            "fontSize": 3.0, "fill": p["teal"]}, induk))
        for k, nama in enumerate(KEPALA):
            hasil.append(_teks(f"kepala_{b.nomor}_{k}", nama,
                               kolom_x + LEBAR_KOLOM_TGL + k * lebar_waktu + lebar_waktu / 2,
                               y_kepala,
                               {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold",
                                "fontSize": 3.0, "fill": p["teal"],
                                "textAlign": "center"}, induk))

        for j, r in enumerate(b.sholat):
            baris_y = y_baris0 + j * TINGGI_BARIS
            hasil.append(_teks(f"rentang_{b.nomor}_{j}", f"{r.dari}–{r.sampai}",
                               kolom_x, baris_y,
                               {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold",
                                "fontSize": tema.UKURAN["sholat"], "fill": p["ink"],
                                "features": {"tnum": True}}, induk))
            for k, nilai in enumerate((r.subuh, r.dzuhur, r.ashar, r.maghrib, r.isya)):
                hasil.append(_teks(f"waktu_{b.nomor}_{j}_{k}", nilai,
                                   kolom_x + LEBAR_KOLOM_TGL + k * lebar_waktu + lebar_waktu / 2,
                                   baris_y,
                                   {"fontFamily": tema.FONT_TEKS,
                                    "fontSize": tema.UKURAN["sholat"], "fill": p["ink"],
                                    "textAlign": "center",
                                    "features": {"tnum": True}}, induk))

    y_catatan = y_baris0 + 6 * TINGGI_BARIS + 3.0
    hasil.append(_teks("koreksi_wilayah", KOREKSI, x, y_catatan,
                       {"fontFamily": tema.FONT_TEKS, "fontSize": 2.7, "fill": p["teal"]}, induk))
    return hasil
