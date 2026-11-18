#!/usr/bin/env python3
"""Bangun kalender dinding A2 2027 Yayasan Islam Baitul Qowwam lewat FigCraft MCP.

Jalankan dengan app FigCraft yang sudah hidup:
    figcraft --control 40695 --automation-read-root . --automation-write-root ./dist
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import tema
from blok_bulan import perintah_blok_bulan
from figcraft_mcp import GalatMcp, KlienMcp
from header import SLOT_FOTO, perintah_header
from kalender_data import Lembar, bangun_lembar
from pita_sholat import perintah_pita_sholat

AKAR = Path(__file__).resolve().parent
CLI_BAWAAN = Path.home() / "project/artCraft/FIGCRAFT/target/release/figcraft-cli"

# FigCraft mengekspor 1 unit = 1 pt, bukan 1 mm. Seluruh tata letak ditulis
# dalam mm supaya enak dibaca manusia, lalu dikonversi tepat sekali di batas
# pengiriman. Tanpa ini lembar "A2" tercetak seukuran A5.
MM_KE_PT = 72.0 / 25.4          # 2.834645…

_KUNCI_PANJANG = ("x", "y", "width", "height")
_PROPS_PANJANG = ("fontSize", "strokeWeight", "cornerRadius")


def _skala(nilai):
    if isinstance(nilai, (int, float)):
        return round(nilai * MM_KE_PT, 4)
    if isinstance(nilai, str) and nilai.endswith("px"):
        try:
            return f"{round(float(nilai[:-2]) * MM_KE_PT, 4)}px"
        except ValueError:
            return nilai
    return nilai


def ke_titik(perintah: list[dict]) -> list[dict]:
    """Ubah seluruh ukuran dari mm ke pt, tepat sebelum dikirim."""
    hasil: list[dict] = []
    for p in perintah:
        params = dict(p["params"])
        for k in _KUNCI_PANJANG:
            if k in params:
                params[k] = _skala(params[k])
        if "props" in params:
            props = dict(params["props"])
            for k in _PROPS_PANJANG + ("letterSpacing",):
                if k in props:
                    props[k] = _skala(props[k])
            params["props"] = props
        salinan = dict(p)
        salinan["params"] = params
        hasil.append(salinan)
    return hasil


def _beri_awalan(perintah: list[dict], awalan: str) -> list[dict]:
    """Nama perintah harus unik dalam satu batch; blok bulan memakai nama yang sama."""
    hasil = []
    for p in perintah:
        salinan = dict(p)
        salinan["as"] = f"{awalan}{p['as']}"
        hasil.append(salinan)
    return hasil


def perintah_lembar(lembar: Lembar) -> list[dict]:
    x0, y0 = tema.MARGIN, tema.MARGIN

    # Bidang kertas digambar sebagai layer paling bawah, bukan mengandalkan
    # page.setBackground: ekspor hanya menggambar layer (contentsOnly), jadi
    # latar halaman tidak ikut dan hasilnya putih. Dilebihkan 5 mm ke segala
    # arah supaya area bleed ikut tertutup warna kertas.
    hasil: list[dict] = [{
        "command": "node.create",
        "as": "kertas",
        "params": {"type": "rectangle", "x": -3.0, "y": -3.0,
                   "width": tema.LEBAR_HALAMAN + 6.0,
                   "height": tema.TINGGI_HALAMAN + 6.0,
                   "props": {"fill": tema.PALET["paper"], "name": "Kertas"},
                   "select": False},
    }]
    hasil += perintah_header(lembar, x0, y0)

    anggaran = tema.anggaran_vertikal()
    nafas = anggaran["sisa"] / 3.0
    y_grid = y0 + tema.TINGGI_HEADER + tema.JEDA_HEADER + nafas

    for i, bulan in enumerate(lembar.bulan):
        baris, kolom = divmod(i, 2)
        bx = x0 + kolom * (tema.LEBAR_BULAN + tema.GUTTER)
        by = y_grid + baris * (anggaran["tinggi_bulan"] + tema.GUTTER)
        hasil += _beri_awalan(perintah_blok_bulan(bulan, bx, by), f"bulan_{bulan.nomor}_")

    y_pita = y_grid + anggaran["grid"] + tema.JEDA_PITA + nafas
    hasil += perintah_pita_sholat(lembar.bulan, x0, y_pita)

    hasil.append({
        "command": "text.create",
        "as": "kaki",
        "params": {
            "text": ("Yayasan Islam Baitul Qowwam  ·  Jl. [alamat]  ·  [telp/WA]  ·  "
                     "Awal Ramadan, Idulfitri & Iduladha mengikuti Sidang Isbat Kemenag RI"),
            "x": x0,
            "y": tema.TINGGI_HALAMAN - tema.MARGIN - 4.0,
            "props": {"fontFamily": tema.FONT_TEKS, "fontSize": 2.6,
                      "fill": tema.PALET["teal"]},
            "select": False,
        },
    })
    return hasil


def kirim_perintah(klien: KlienMcp, perintah: list[dict]) -> dict[str, int]:
    """Kirim per potongan 200 dan kembalikan peta nama `as` → id node.

    `batch` membalas daftar hasil berurutan posisi, sejajar dengan perintah
    yang dikirim. Itu satu-satunya cara mendapat id layer, karena `get_node`
    hanya menerima id, bukan nama.
    """
    peta: dict[str, int] = {}
    perintah = ke_titik(perintah)
    for mulai in range(0, len(perintah), 200):
        potongan = perintah[mulai:mulai + 200]
        hasil = klien.jalankan_batch(potongan)
        daftar = hasil if isinstance(hasil, list) else hasil.get("teks", [])
        for p, r in zip(potongan, daftar):
            if isinstance(r, dict) and "id" in r and "as" in p:
                peta[p["as"]] = r["id"]
    return peta


def pasang_foto(klien: KlienMcp, dir_foto: Path, id_slot: dict[str, int]) -> list[str]:
    """Pasang foto ke slot yang namanya cocok. Slot tanpa foto dibiarkan.

    Kunci `id_slot` berbentuk `foto_utama_1`, `foto_2_3`, dan seterusnya:
    nama slot diikuti nomor lembar. Nama berkas mengikuti kunci itu persis.
    """
    terisi: list[str] = []
    if not dir_foto.is_dir():
        return terisi
    for kunci, id_node in id_slot.items():
        for akhiran in (".jpg", ".jpeg", ".png"):
            berkas = dir_foto / f"{kunci}{akhiran}"
            if not berkas.exists():
                continue
            klien.panggil("run_command", {
                "command": "image.place",
                "params": {"path": str(berkas), "target": id_node, "mode": "fill"},
            })
            terisi.append(kunci)
            break
    return terisi


def main(argv: list[str] | None = None) -> int:
    uraian = argparse.ArgumentParser(description=__doc__)
    uraian.add_argument("--port", type=int, default=40695)
    uraian.add_argument("--cli", type=Path, default=CLI_BAWAAN)
    uraian.add_argument("--foto-dir", type=Path, default=AKAR / "assets/foto")
    uraian.add_argument("--keluar", type=Path, default=AKAR / "dist")
    uraian.add_argument("--lembar", type=int, action="append", choices=[1, 2, 3])
    arg = uraian.parse_args(argv)

    nomor_lembar = arg.lembar or [1, 2, 3]
    arg.keluar.mkdir(parents=True, exist_ok=True)
    id_slot: dict[str, int] = {}

    try:
        with KlienMcp(arg.cli, arg.port) as klien:
            for nomor in nomor_lembar:
                lembar = bangun_lembar(nomor)
                print(f"Lembar {nomor}: {', '.join(b.nama for b in lembar.bulan)}")
                if nomor == nomor_lembar[0]:
                    klien.panggil("run_command", {
                        "command": "page.setBackground",
                        "params": {"color": tema.PALET["paper"]},
                    })
                else:
                    klien.panggil("run_command", {
                        "command": "page.add",
                        "params": {"name": f"Lembar {nomor}"},
                    })
                    klien.panggil("run_command", {
                        "command": "page.setBackground",
                        "params": {"color": tema.PALET["paper"]},
                    })
                # Dipotong 200 supaya galat menunjuk bagian yang salah, dan
                # supaya satu permintaan tidak melewati batas waktu app.
                peta = kirim_perintah(klien, perintah_lembar(lembar))
                # Tiap lembar punya empat slotnya sendiri, jadi id disimpan
                # dengan nomor lembarnya; tanpa ini lembar terakhir menimpa
                # yang lain dan foto hanya muncul di satu lembar.
                for nama_slot in SLOT_FOTO:
                    if nama_slot in peta:
                        id_slot[f"{nama_slot}_{nomor}"] = peta[nama_slot]

            terisi = pasang_foto(klien, arg.foto_dir, id_slot)
            print(f"Foto terpasang: {', '.join(terisi) if terisi else 'belum ada'}")

            berkas = arg.keluar / "kalender-baitul-qowwam-2027.figcraft"
            klien.panggil("save_file", {"path": str(berkas)})

            # `export` tidak menerima parameter halaman: ia selalu mengambil
            # halaman yang sedang aktif. Jadi tiap lembar harus dipilih dulu,
            # dan tiap lembar menjadi berkasnya sendiri. Tanpa page.select,
            # ketiga berkas berisi halaman yang sama persis.
            for indeks, nomor in enumerate(nomor_lembar):
                klien.panggil("run_command", {
                    "command": "page.select", "params": {"index": indeks},
                })
                klien.panggil("export", {
                    "format": "pdf", "cmyk": True,
                    "path": str(arg.keluar / f"cetak-lembar-{nomor}.pdf"),
                })
                klien.panggil("export", {
                    "format": "pdf",
                    "path": str(arg.keluar / f"layar-lembar-{nomor}.pdf"),
                })
                klien.panggil("export", {
                    "format": "png", "scale": 2,
                    "path": str(arg.keluar / f"lembar-{nomor}.png"),
                })
    except GalatMcp as galat:
        print(f"Gagal: {galat}", file=sys.stderr)
        print("Pastikan app FigCraft jalan: figcraft --control 40695 ...", file=sys.stderr)
        return 1

    print(f"Selesai. Berkas ada di {arg.keluar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
