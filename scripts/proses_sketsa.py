#!/usr/bin/env python3
"""Konversi ilustrasi sketsa berlatar putih menjadi PNG RGBA transparan.

Menggunakan unpremultiplied watercolor alpha matting terhadap putih:
- Putih murni (dan derau latar dekat putih) menjadi transparan penuh (alpha = 0)
- Sapuan cat air tipis menjadi semi-transparan sehingga menyatu organik dengan
  kertas kalender (#F2EEED) tanpa halo putih
- Garis tinta gelap (#024959) tetap tajam dan pekat
"""

from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image


def putih_ke_transparan(
    img: Image.Image,
    ambang_putih: float = 0.955,
    opasitas: float = 1.0,
    feather_tepi: float = 0.04,
    feather_sisi: tuple[str, ...] = ("top", "bottom", "left", "right"),
    trim: bool = False,
) -> Image.Image:
    """Ubah latar putih menjadi alpha transparan dengan mempertahankan warna cat air."""
    rgb = img.convert("RGB")
    w, h = rgb.size
    src = rgb.load()
    out = Image.new("RGBA", (w, h))
    dst = out.load()

    # Tentukan margin feather dalam piksel
    fx = max(1, int(w * feather_tepi)) if feather_tepi > 0 else 0
    fy = max(1, int(h * feather_tepi)) if feather_tepi > 0 else 0
    f_top = "top" in feather_sisi
    f_bot = "bottom" in feather_sisi
    f_left = "left" in feather_sisi
    f_right = "right" in feather_sisi

    inv_ambang = 1.0 / max(1e-6, ambang_putih)

    for y in range(h):
        # Faktor pelunakan vertikal di tepi
        vy = 1.0
        if fy > 0:
            if f_top and y < fy:
                vy = min(vy, y / fy)
            if f_bot and (h - 1 - y) < fy:
                vy = min(vy, (h - 1 - y) / fy)

        for x in range(w):
            r, g, b = src[x, y]
            rf, gf, bf = r / 255.0, g / 255.0, b / 255.0

            # Nilai saluran paling gelap menentukan seberapa pekat tinta di atas putih
            min_c = min(rf, gf, bf)
            if min_c >= ambang_putih:
                dst[x, y] = (0, 0, 0, 0)
                continue

            # Normalisasi terhadap ambang putih agar latar sedikit abu tetap bersih total
            rn = min(1.0, rf * inv_ambang)
            gn = min(1.0, gf * inv_ambang)
            bn = min(1.0, bf * inv_ambang)
            min_n = min(rn, gn, bn)

            alpha = 1.0 - min_n
            if alpha <= 0.004:
                dst[x, y] = (0, 0, 0, 0)
                continue

            # Unpremultiply dari latar putih: C_ink = 1 - (1 - C_obs) / alpha
            ir = max(0.0, min(1.0, 1.0 - (1.0 - rn) / alpha))
            ig = max(0.0, min(1.0, 1.0 - (1.0 - gn) / alpha))
            ib = max(0.0, min(1.0, 1.0 - (1.0 - bn) / alpha))

            # Pelunakan tepi opsional agar tidak pernah terlihat garis potong kotak
            vx = 1.0
            if fx > 0:
                if f_left and x < fx:
                    vx = min(vx, x / fx)
                if f_right and (w - 1 - x) < fx:
                    vx = min(vx, (w - 1 - x) / fx)

            a_akhir = alpha * opasitas * vx * vy
            a_byte = max(0, min(255, int(round(a_akhir * 255.0))))
            if a_byte == 0:
                dst[x, y] = (0, 0, 0, 0)
            else:
                dst[x, y] = (
                    int(round(ir * 255.0)),
                    int(round(ig * 255.0)),
                    int(round(ib * 255.0)),
                    a_byte,
                )

    if trim:
        bbox = out.getbbox()
        if bbox:
            pad = max(8, int(min(w, h) * 0.02))
            x0 = max(0, bbox[0] - pad)
            y0 = max(0, bbox[1] - pad)
            x1 = min(w, bbox[2] + pad)
            y1 = min(h, bbox[3] + pad)
            out = out.crop((x0, y0, x1, y1))

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sumber", type=Path)
    parser.add_argument("tujuan", type=Path)
    parser.add_argument("--ambang", type=float, default=0.955)
    parser.add_argument("--opasitas", type=float, default=1.0)
    parser.add_argument("--feather", type=float, default=0.04)
    parser.add_argument("--sisi", default="top,bottom,left,right")
    parser.add_argument("--trim", action="store_true")
    args = parser.parse_args()

    sisi = tuple(s.strip() for s in args.sisi.split(",") if s.strip())
    with Image.open(args.sumber) as im:
        hasil = putih_ke_transparan(
            im,
            ambang_putih=args.ambang,
            opasitas=args.opasitas,
            feather_tepi=args.feather,
            feather_sisi=sisi,
            trim=args.trim,
        )
    args.tujuan.parent.mkdir(parents=True, exist_ok=True)
    hasil.save(args.tujuan, format="PNG", optimize=True)
    print(f"OK: {args.tujuan} ({hasil.size[0]}x{hasil.size[1]}, RGBA)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
