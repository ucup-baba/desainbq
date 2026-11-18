"""Perintah FigCraft untuk satu blok bulan.

Fungsi di sini murni: ia menghasilkan daftar perintah, tidak menyentuh
jaringan. Itu yang membuat tata letaknya bisa diuji tanpa menjalankan app.
"""

from __future__ import annotations

import tema
from kalender_data import Bulan

NAMA_HARI = ("MIN", "SEN", "SEL", "RAB", "KAM", "JUM", "SAB")


def _teks(nama: str, isi: str, x: float, y: float, props: dict, induk: str | None) -> dict:
    params: dict = {"text": isi, "x": round(x, 3), "y": round(y, 3), "props": props,
                    "select": False}
    if induk is not None:
        params["parent"] = induk
    return {"command": "text.create", "params": params, "as": nama}


def _bidang(nama: str, x: float, y: float, w: float, h: float, props: dict,
            induk: str | None) -> dict:
    params: dict = {"type": "rectangle", "x": round(x, 3), "y": round(y, 3),
                    "width": round(w, 3), "height": round(h, 3), "props": props,
                    "select": False}
    if induk is not None:
        params["parent"] = induk
    return {"command": "node.create", "params": params, "as": nama}


def perintah_blok_bulan(bulan: Bulan, x: float, y: float,
                        induk: str | None = None) -> list[dict]:
    p = tema.PALET
    lebar_kolom = tema.LEBAR_KOLOM_HARI
    hasil: list[dict] = []

    # --- kepala: nomor, nama bulan, rentang Hijriah & Jawa ---------------
    hasil.append(_teks("nomor_bulan", f"{bulan.nomor:02d}", x, y,
                       {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold",
                        "fontSize": 3.2, "fill": p["amber"], "letterSpacing": "0.5px"}, induk))
    hasil.append(_teks("nama_bulan", bulan.nama, x + 7.0, y - 2.0,
                       {"fontFamily": tema.FONT_DISPLAY, "fontSize": tema.UKURAN["nama_bulan"],
                        "fill": p["ink"]}, induk))
    hasil.append(_teks("rentang_hijriah", bulan.rentang_hijriah,
                       x + tema.LEBAR_BULAN, y,
                       {"fontFamily": tema.FONT_TEKS, "fontSize": 2.4, "fill": p["ink"],
                        "opacity": 0.8, "textAlign": "right"}, induk))
    hasil.append(_teks("rentang_jawa", bulan.rentang_jawa,
                       x + tema.LEBAR_BULAN, y + 3.4,
                       {"fontFamily": tema.FONT_TEKS, "fontSize": 2.4, "fill": p["ink"],
                        "opacity": 0.8, "textAlign": "right"}, induk))

    y_garis = y + tema.TINGGI_KEPALA_BULAN - 1.0
    hasil.append(_bidang("garis_kepala", x, y_garis, tema.LEBAR_BULAN, 0.7,
                         {"fill": p["ink"]}, induk))

    # --- baris nama hari --------------------------------------------------
    y_hari = y + tema.TINGGI_KEPALA_BULAN
    for kolom, nama in enumerate(NAMA_HARI):
        hasil.append(_teks(f"hari_{kolom}", nama,
                           x + kolom * lebar_kolom + lebar_kolom / 2, y_hari,
                           {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold",
                            "fontSize": tema.UKURAN["nama_hari"],
                            "fill": p["rust"] if kolom == 0 else p["teal"],
                            "letterSpacing": "0.5px", "textAlign": "center"}, induk))

    # --- kisi tanggal -----------------------------------------------------
    y_kisi = y_hari + tema.TINGGI_BARIS_HARI
    for indeks, hari in enumerate(bulan.sel):
        if hari is None:
            continue
        baris, kolom = divmod(indeks, 7)
        sel_x = x + kolom * lebar_kolom
        sel_y = y_kisi + baris * tema.TINGGI_SEL

        if hari.libur:
            hasil.append(_bidang(f"alas_{hari.masehi}", sel_x, sel_y,
                                 lebar_kolom, tema.TINGGI_SEL,
                                 {"fill": p["sun"], "opacity": 0.42}, induk))

        warna = p["rust"] if (kolom == 0 or hari.libur) else p["ink"]
        hasil.append(_teks(f"tgl_{hari.masehi}", str(hari.masehi),
                           sel_x + lebar_kolom / 2, sel_y + 1.6,
                           {"fontFamily": tema.FONT_TEKS, "fontStyle": "SemiBold",
                            "fontSize": tema.UKURAN["tanggal"], "fill": warna,
                            "textAlign": "center", "features": {"tnum": True}}, induk))
        hasil.append(_teks(f"hij_{hari.masehi}", str(hari.hijriah_hari),
                           sel_x + lebar_kolom - 2.2, sel_y + 1.6,
                           {"fontFamily": tema.FONT_TEKS, "fontStyle": "SemiBold",
                            "fontSize": tema.UKURAN["hijriah"], "fill": p["teal"],
                            "textAlign": "right", "features": {"tnum": True}}, induk))
        hasil.append(_teks(f"jaw_{hari.masehi}", f"{hari.jawa_hari} {hari.pasaran}",
                           sel_x + lebar_kolom / 2, sel_y + 11.5,
                           {"fontFamily": tema.FONT_TEKS, "fontSize": tema.UKURAN["jawa"],
                            "fill": p["teal"], "opacity": 0.85, "textAlign": "center"}, induk))

    # --- keterangan hari libur -------------------------------------------
    keterangan = "  ·  ".join(f"{h.masehi} — {h.libur}" for h in bulan.hari if h.libur)
    y_ket = y_kisi + 6 * tema.TINGGI_SEL + 2.0
    hasil.append(_bidang("garis_ket", x, y_ket - 2.0, tema.LEBAR_BULAN, 0.5,
                         {"fill": p["ink"]}, induk))
    hasil.append(_teks("ket_libur", keterangan or " ", x, y_ket,
                       {"fontFamily": tema.FONT_TEKS, "fontSize": tema.UKURAN["ket_libur"],
                        "fill": p["teal"]}, induk))
    return hasil
