# Kalender Baitul Qowwam 2027 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Menghasilkan kalender dinding A2 2027 Yayasan Islam Baitul Qowwam — 3 lembar × 4 bulan, Masehi + Hijriah + Jawa, jadwal sholat WIB DIY per 5 hari — sebagai file `.figcraft` yang bisa disunting dan PDF siap cetak CMYK.

**Architecture:** Fungsi murni menghasilkan *daftar perintah* (list of dict) untuk FigCraft, lalu satu klien tipis mengirimkannya lewat MCP `batch`. Pemisahan ini membuat seluruh tata letak bisa diuji tanpa menjalankan aplikasi: tes memeriksa daftar perintah, bukan piksel. Data tanggal dan waktu sholat diambil dari `generate_kalender.py` yang sudah ada dan terbukti benar.

**Tech Stack:** Python 3.12 (pustaka standar saja), FigCraft MCP server mode attached, pytest.

**Spec:** `docs/superpowers/specs/2026-11-18-kalender-baitul-qowwam-2027-design.md`

## Global Constraints

- Satuan: 1 unit FigCraft = 1 mm. Halaman 420 × 594 mm portrait.
- Margin aman 14 mm. Lebar area kerja 392 mm. Gutter 9 mm.
- Palet, tepat tujuh warna: ink `#024959`, teal `#038C8C`, mint `#6EC4C0`, paper `#F2EEED`, sun `#F9D83F`, amber `#F29F05`, rust `#A64F03`.
- Tidak ada gradien, tidak ada bayangan, di mana pun.
- Font tulisan tangan (Caveat Brush, Patrick Hand) hanya untuk angka tahun, nama bulan, nama yayasan, judul bagian. Seluruh data memakai Plus Jakarta Sans.
- Aturan rentang sholat: tiap sel memuat waktu **paling akhir** dalam rentangnya.
- Rentang: 1–5, 6–10, 11–15, 16–20, 21–25, 26–akhir bulan.
- Hari Minggu dan hari libur memakai rust `#A64F03`, bukan merah.
- Semua keluaran build ditulis ke `dist/`. Tidak ada tulis ke luar folder proyek — root otomasi app menolaknya.
- App FigCraft harus berjalan attached di port 40695 sebelum build dijalankan.
- Proyek ini repo tersendiri. Jangan pernah commit apa pun ke repo FigCraft.

---

## File Structure

| Berkas | Tanggung jawab |
|---|---|
| `tema.py` | Token: geometri, palet, peran font. Tidak ada logika. |
| `kalender_data.py` | Model data lembar/bulan/hari + peringkas sholat. Membungkus `generate_kalender.py`. |
| `figcraft_mcp.py` | Klien MCP attached: kirim perintah, baca balasan, laporkan galat. |
| `blok_bulan.py` | Perintah untuk satu blok bulan. |
| `pita_sholat.py` | Perintah untuk pita jadwal sholat. |
| `header.py` | Perintah untuk header: identitas, angka tahun, slot foto. |
| `build_kalender.py` | Orkestrator: 3 halaman, simpan, ekspor. |
| `scripts/pasang_font.sh` | Unduh dan pasang font OFL ke `~/.fonts`. |
| `tests/test_kalender_data.py` | Rentang sholat, model data, paritas 365 hari. |
| `tests/test_tema.py` | Anggaran vertikal dan palet. |
| `tests/test_blok_bulan.py` | Struktur perintah blok bulan. |
| `tests/test_pita_sholat.py` | Struktur perintah pita sholat. |
| `tests/test_header.py` | Struktur perintah header. |
| `ATTRIBUTION.md` | Catatan lisensi font dan foto. |

`generate_kalender.py` dipertahankan sebagai sumber data. Modul render HTML di dalamnya dan `build_via_figcraft_mcp.py` dihapus pada Task 10.

---

### Task 1: Pasang font dan catat lisensinya

**Files:**
- Create: `scripts/pasang_font.sh`
- Create: `ATTRIBUTION.md`

**Interfaces:**
- Consumes: —
- Produces: Font `Caveat Brush`, `Patrick Hand`, `Plus Jakarta Sans` tersedia bagi FigCraft.

- [ ] **Step 1: Tulis skrip pemasang font**

```bash
#!/usr/bin/env bash
# Pasang font OFL yang dipakai kalender ke ~/.fonts
set -euo pipefail

TUJUAN="${HOME}/.fonts/baitul-qowwam"
BASIS="https://raw.githubusercontent.com/google/fonts/main/ofl"
mkdir -p "$TUJUAN"

unduh() { # $1 = path relatif di repo google/fonts, $2 = nama berkas tujuan
  curl -fsSL --max-time 60 "$BASIS/$1" -o "$TUJUAN/$2"
  echo "  terpasang: $2"
}

echo "Mengunduh font:"
unduh "caveatbrush/CaveatBrush-Regular.ttf"          "CaveatBrush-Regular.ttf"
unduh "patrickhand/PatrickHand-Regular.ttf"          "PatrickHand-Regular.ttf"
unduh "plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf" "PlusJakartaSans-Variable.ttf"
unduh "caveatbrush/OFL.txt"                          "OFL-CaveatBrush.txt"
unduh "patrickhand/OFL.txt"                          "OFL-PatrickHand.txt"
unduh "plusjakartasans/OFL.txt"                      "OFL-PlusJakartaSans.txt"

fc-cache -f "$TUJUAN" >/dev/null
echo "Selesai. Font terdaftar:"
fc-list : family | grep -iE "caveat brush|patrick hand|plus jakarta" | sort -u
```

- [ ] **Step 2: Jalankan dan pastikan ketiga keluarga terdaftar**

Run: `chmod +x scripts/pasang_font.sh && ./scripts/pasang_font.sh`
Expected: tiga baris keluaran yang memuat `Caveat Brush`, `Patrick Hand`, `Plus Jakarta Sans`.

Kalau salah satu tidak muncul, hentikan dan laporkan — jangan lanjut dengan font pengganti, karena seluruh ukuran pada spec dihitung untuk font-font ini.

- [ ] **Step 3: Restart app FigCraft supaya font terbaca**

FigCraft memindai font sistem saat start, jadi font baru tidak terlihat oleh proses yang sedang jalan.

```bash
pkill -f 'figcraft --control 40695' || true
sleep 2
PROJ="$PWD"
FIGCRAFT_BIN="$HOME/project/artCraft/FIGCRAFT/target/release/figcraft"
nohup "$FIGCRAFT_BIN" --control 40695 \
  --automation-read-root "$PROJ" \
  --automation-write-root "$PROJ/dist" > "$PROJ/.figcraft-app.log" 2>&1 &
sleep 6
grep -q "listening" "$PROJ/.figcraft-app.log" && echo "app siap"
```

- [ ] **Step 4: Pastikan FigCraft benar-benar melihat ketiga font**

```bash
printf '%s\n%s\n' \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"p","version":"1"}}}' \
'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"run_command","arguments":{"command":"file.fontReport","params":{}}}}' \
| "$HOME/project/artCraft/FIGCRAFT/target/release/figcraft-cli" mcp --attach 40695 2>/dev/null \
| grep -ioE "caveat brush|patrick hand|plus jakarta sans" | sort -u
```

Expected: ketiga nama muncul. Kalau `Plus Jakarta Sans` muncul tetapi gayanya hanya `Regular`, catat itu: berarti berat tebal diatur lewat `text.setVariations` dengan `{"wght": 600}`, bukan lewat `fontStyle`. Tulis temuan ini di `ATTRIBUTION.md` bagian catatan.

- [ ] **Step 5: Tulis ATTRIBUTION.md**

```markdown
# Atribusi Aset

Seluruh aset di proyek ini original, berlisensi terbuka, atau milik yayasan.

## Font

Tidak disertakan dalam repositori. Dipasang ke `~/.fonts/baitul-qowwam`
oleh `scripts/pasang_font.sh`.

| Font | Pembuat | Sumber | Lisensi |
|---|---|---|---|
| Caveat Brush | Impallari Type | github.com/google/fonts `ofl/caveatbrush` | OFL-1.1 |
| Patrick Hand | Patrick Wagesreiter | github.com/google/fonts `ofl/patrickhand` | OFL-1.1 |
| Plus Jakarta Sans | Tokotype | github.com/google/fonts `ofl/plusjakartasans` | OFL-1.1 |

## Foto

Foto kegiatan di `assets/foto/` adalah milik Yayasan Islam Baitul Qowwam dan
dipakai atas izin pemilik. Tidak ada foto stok, ikon, atau ilustrasi dari
produk pihak lain di proyek ini.

## Catatan

(Isi temuan Task 1 Step 4 tentang gaya Plus Jakarta Sans di sini.)
```

- [ ] **Step 6: Commit**

```bash
git add scripts/pasang_font.sh ATTRIBUTION.md
git commit -m "Pasang font OFL dan catat atribusinya"
```

---

### Task 2: Meringkas jadwal sholat menjadi rentang 5 hari

**Files:**
- Create: `kalender_data.py`
- Create: `tests/test_kalender_data.py`

**Interfaces:**
- Consumes: `generate_kalender.prayer_times_yogya(date) -> dict[str, str]` dengan kunci `subuh`, `dzuhur`, `ashar`, `maghrib`, `isya`.
- Produces:
  - `rentang_lima_hari(tahun: int, bulan: int) -> list[tuple[int, int]]`
  - `RentangSholat` (dataclass beku): `dari: int`, `sampai: int`, `subuh: str`, `dzuhur: str`, `ashar: str`, `maghrib: str`, `isya: str`
  - `ringkas_sholat(tahun: int, bulan: int) -> list[RentangSholat]`

- [ ] **Step 1: Tulis tes yang gagal**

```python
# tests/test_kalender_data.py
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
    for bulan in range(1, 13):
        tercakup = [h for a, b in rentang_lima_hari(2027, bulan) for h in range(a, b + 1)]
        akhir = (dt.date(2027, bulan % 12 + 1, 1) - dt.timedelta(days=1)).day if bulan != 12 else 31
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
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_kalender_data.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'kalender_data'`

- [ ] **Step 3: Tulis implementasi minimal**

```python
# kalender_data.py
"""Model data kalender: membungkus generate_kalender.py dengan bentuk yang
siap dipakai oleh modul tata letak."""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import generate_kalender as gk

KUNCI_SHOLAT = ("subuh", "dzuhur", "ashar", "maghrib", "isya")


@dataclass(frozen=True)
class RentangSholat:
    dari: int
    sampai: int
    subuh: str
    dzuhur: str
    ashar: str
    maghrib: str
    isya: str


def rentang_lima_hari(tahun: int, bulan: int) -> list[tuple[int, int]]:
    """Rentang 1-5, 6-10, ... dengan rentang terakhir menyerap sisa hari."""
    akhir = calendar.monthrange(tahun, bulan)[1]
    hasil: list[tuple[int, int]] = []
    mulai = 1
    while mulai <= akhir:
        habis = min(mulai + 4, akhir)
        if akhir - habis < 3:
            habis = akhir
        hasil.append((mulai, habis))
        mulai = habis + 1
    return hasil


def ringkas_sholat(tahun: int, bulan: int) -> list[RentangSholat]:
    """Satu baris per rentang, berisi waktu PALING AKHIR dalam rentang itu.

    Diambil yang paling akhir supaya tidak mungkin seseorang sholat atau
    berbuka sebelum waktunya masuk.
    """
    hasil: list[RentangSholat] = []
    for dari, sampai in rentang_lima_hari(tahun, bulan):
        terakhir = {k: "" for k in KUNCI_SHOLAT}
        for hari in range(dari, sampai + 1):
            waktu = gk.prayer_times_yogya(dt.date(tahun, bulan, hari))
            for k in KUNCI_SHOLAT:
                if waktu[k] > terakhir[k]:
                    terakhir[k] = waktu[k]
        hasil.append(RentangSholat(dari=dari, sampai=sampai, **terakhir))
    return hasil
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_kalender_data.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add kalender_data.py tests/test_kalender_data.py
git commit -m "Ringkas jadwal sholat menjadi rentang 5 hari"
```

---

### Task 3: Model lembar, bulan, dan hari

**Files:**
- Modify: `kalender_data.py`
- Modify: `tests/test_kalender_data.py`

**Interfaces:**
- Consumes: `generate_kalender.build_hijri_jawa_map()`, `generate_kalender.HOLIDAYS_2027`, `generate_kalender.MONTH_NAMES_ID`.
- Produces:
  - `Hari`: `tanggal: dt.date`, `masehi: int`, `kolom: int` (0=Minggu), `hijriah_hari: int`, `hijriah_nama: str`, `jawa_hari: int`, `jawa_nama: str`, `pasaran: str`, `libur: str | None`, `jenis_libur: str | None`
  - `Bulan`: `nomor: int`, `nama: str`, `hari: tuple[Hari, ...]`, `sel: tuple[Hari | None, ...]` (42 sel kisi), `sholat: tuple[RentangSholat, ...]`, `rentang_hijriah: str`, `rentang_jawa: str`
  - `Lembar`: `nomor: int`, `bulan: tuple[Bulan, ...]`
  - `bangun_lembar(nomor: int) -> Lembar` untuk nomor 1, 2, 3
  - `bangun_bulan(tahun: int, bulan: int) -> Bulan`

- [ ] **Step 1: Tulis tes yang gagal**

```python
# tambahkan ke tests/test_kalender_data.py
from kalender_data import Hari, bangun_bulan, bangun_lembar


def test_satu_januari_2027_jatuh_jumat_pon():
    jan = bangun_bulan(2027, 1)
    satu = jan.hari[0]
    assert satu.kolom == 5          # 0=Minggu, jadi 5=Jum'at
    assert satu.pasaran == "Pon"
    assert satu.hijriah_hari == 23
    assert satu.hijriah_nama == "Rajab"


def test_kisi_selalu_42_sel():
    for bulan in range(1, 13):
        assert len(bangun_bulan(2027, bulan).sel) == 42, bulan


def test_sel_kosong_di_luar_bulan():
    jan = bangun_bulan(2027, 1)
    assert jan.sel[0] is None       # 1 Jan jatuh Jum'at, jadi 5 sel pertama kosong
    assert jan.sel[4] is None
    assert jan.sel[5] is not None and jan.sel[5].masehi == 1


def test_hari_libur_tercatat():
    jan = bangun_bulan(2027, 1)
    tahun_baru = jan.hari[0]
    assert tahun_baru.libur is not None
    assert "Tahun Baru" in tahun_baru.libur


def test_lembar_memuat_empat_bulan_berurutan():
    assert [b.nomor for b in bangun_lembar(1).bulan] == [1, 2, 3, 4]
    assert [b.nomor for b in bangun_lembar(2).bulan] == [5, 6, 7, 8]
    assert [b.nomor for b in bangun_lembar(3).bulan] == [9, 10, 11, 12]


def test_rentang_hijriah_terbaca():
    jan = bangun_bulan(2027, 1)
    assert jan.rentang_hijriah == "Rajab – Sya'ban 1448"
    assert jan.rentang_jawa == "Rejeb – Ruwah 1960"
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_kalender_data.py -v`
Expected: FAIL — `ImportError: cannot import name 'bangun_bulan'`

- [ ] **Step 3: Tulis implementasi**

```python
# tambahkan ke kalender_data.py

_PETA = None


def _peta():
    global _PETA
    if _PETA is None:
        _PETA = gk.build_hijri_jawa_map()
    return _PETA


@dataclass(frozen=True)
class Hari:
    tanggal: dt.date
    masehi: int
    kolom: int
    hijriah_hari: int
    hijriah_nama: str
    jawa_hari: int
    jawa_nama: str
    pasaran: str
    libur: str | None
    jenis_libur: str | None


@dataclass(frozen=True)
class Bulan:
    nomor: int
    nama: str
    hari: tuple[Hari, ...]
    sel: tuple[Hari | None, ...]
    sholat: tuple[RentangSholat, ...]
    rentang_hijriah: str
    rentang_jawa: str


@dataclass(frozen=True)
class Lembar:
    nomor: int
    bulan: tuple[Bulan, ...]


def bangun_bulan(tahun: int, bulan: int) -> Bulan:
    peta = _peta()
    akhir = calendar.monthrange(tahun, bulan)[1]
    daftar: list[Hari] = []
    for nomor in range(1, akhir + 1):
        tanggal = dt.date(tahun, bulan, nomor)
        info = peta[tanggal]
        libur = gk.HOLIDAYS_2027.get(tanggal)
        daftar.append(
            Hari(
                tanggal=tanggal,
                masehi=nomor,
                kolom=(tanggal.weekday() + 1) % 7,  # Python: Senin=0; kita: Minggu=0
                hijriah_hari=info["h_day"],
                hijriah_nama=info["h_name"],
                jawa_hari=info["j_day"],
                jawa_nama=info["j_name"],
                pasaran=info["pasaran"],
                libur=libur[1] if libur else None,
                jenis_libur=libur[0] if libur else None,
            )
        )

    geser = daftar[0].kolom
    sel: list[Hari | None] = [None] * geser + list(daftar)
    sel += [None] * (42 - len(sel))

    awal, akhir_h = daftar[0], daftar[-1]
    rentang_hijriah = f"{awal.hijriah_nama} – {akhir_h.hijriah_nama} {peta[akhir_h.tanggal]['h_year']}"
    rentang_jawa = f"{awal.jawa_nama} – {akhir_h.jawa_nama} {peta[akhir_h.tanggal]['j_year']}"

    return Bulan(
        nomor=bulan,
        nama=gk.MONTH_NAMES_ID[bulan],
        hari=tuple(daftar),
        sel=tuple(sel),
        sholat=tuple(ringkas_sholat(tahun, bulan)),
        rentang_hijriah=rentang_hijriah,
        rentang_jawa=rentang_jawa,
    )


def bangun_lembar(nomor: int) -> Lembar:
    if nomor not in (1, 2, 3):
        raise ValueError(f"nomor lembar harus 1, 2 atau 3; diberi {nomor}")
    mulai = (nomor - 1) * 4 + 1
    return Lembar(nomor=nomor, bulan=tuple(bangun_bulan(2027, b) for b in range(mulai, mulai + 4)))
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_kalender_data.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add kalender_data.py tests/test_kalender_data.py
git commit -m "Model data lembar, bulan dan hari"
```

---

### Task 4: Token tema dan anggaran vertikal

**Files:**
- Create: `tema.py`
- Create: `tests/test_tema.py`

**Interfaces:**
- Produces: konstanta geometri dan warna, serta `anggaran_vertikal() -> dict[str, float]`.

- [ ] **Step 1: Tulis tes yang gagal**

```python
# tests/test_tema.py
import tema


def test_palet_tepat_tujuh_warna():
    assert len(tema.PALET) == 7
    assert set(tema.PALET) == {"ink", "teal", "mint", "paper", "sun", "amber", "rust"}
    for nilai in tema.PALET.values():
        assert nilai.startswith("#") and len(nilai) == 7


def test_lebar_area_kerja_sesuai_spec():
    assert tema.LEBAR_ISI == 392.0
    assert tema.LEBAR_BULAN == (392.0 - tema.GUTTER) / 2


def test_isi_muat_di_halaman_dan_menyisakan_ruang_nafas():
    a = tema.anggaran_vertikal()
    assert a["terpakai"] < tema.TINGGI_HALAMAN - 2 * tema.MARGIN
    assert 30.0 <= a["sisa"] <= 55.0, a


def test_blok_bulan_setinggi_komponennya():
    a = tema.anggaran_vertikal()
    assert abs(a["tinggi_bulan"] - (tema.TINGGI_KEPALA_BULAN + tema.TINGGI_BARIS_HARI
                                    + 6 * tema.TINGGI_SEL + tema.TINGGI_KET_LIBUR)) < 0.01


def test_tidak_ada_warna_merah_murni():
    # Spec: peran "merah" diambil rust; merah murni tidak boleh masuk.
    assert "#FF0000" not in tema.PALET.values()
    assert tema.PALET["rust"] == "#A64F03"
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_tema.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tema'`

- [ ] **Step 3: Tulis implementasi**

```python
# tema.py
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
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_tema.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add tema.py tests/test_tema.py
git commit -m "Token tema dan anggaran vertikal halaman"
```

---

### Task 5: Klien MCP attached

**Files:**
- Create: `figcraft_mcp.py`
- Create: `tests/test_figcraft_mcp.py`

**Interfaces:**
- Produces:
  - `KlienMcp(cli: Path, port: int, timeout_detik: int = 180)`
  - `KlienMcp.panggil(nama_tool: str, argumen: dict) -> dict`
  - `KlienMcp.jalankan_batch(perintah: list[dict]) -> dict`
  - `KlienMcp.tutup() -> None`, serta dukungan `with`
  - `GalatMcp(Exception)`

- [ ] **Step 1: Tulis tes yang gagal**

Tes ini tidak memerlukan app: ia memalsukan proses lewat `subprocess` tiruan.

```python
# tests/test_figcraft_mcp.py
import io
import json

import pytest

from figcraft_mcp import GalatMcp, KlienMcp


class ProsesPalsu:
    """Meniru subprocess.Popen: membaca baris permintaan, membalas antrean."""

    def __init__(self, balasan):
        self._balasan = list(balasan)
        self.stdin = io.StringIO()
        self.stdout = self
        self.terkirim = []

    def readline(self):
        if not self._balasan:
            return ""
        return json.dumps(self._balasan.pop(0)) + "\n"

    def poll(self):
        return None

    def kill(self):
        pass

    def wait(self, timeout=None):
        return 0


def klien_dengan(balasan):
    k = KlienMcp.__new__(KlienMcp)
    k.proc = ProsesPalsu(balasan)
    k._id = 1
    return k


def test_hasil_teks_dikembalikan_sebagai_dict():
    isi = {"id": 2, "node": {"id": 7}}
    k = klien_dengan([{"id": 2, "result": {"isError": False,
                                           "content": [{"type": "text", "text": json.dumps(isi)}]}}])
    assert k.panggil("create_node", {"type": "rectangle"}) == isi


def test_galat_tool_dilaporkan_dengan_pesannya():
    k = klien_dengan([{"id": 2, "result": {"isError": True,
                                           "content": [{"type": "text", "text": "unknown argument `fill`"}]}}])
    with pytest.raises(GalatMcp, match="unknown argument"):
        k.panggil("create_node", {"fill": "#fff"})


def test_balasan_tanpa_json_tetap_dikembalikan_apa_adanya():
    k = klien_dengan([{"id": 2, "result": {"isError": False,
                                           "content": [{"type": "text", "text": "selesai"}]}}])
    assert k.panggil("undo", {}) == {"teks": "selesai"}


def test_koneksi_putus_di_tengah_dilaporkan():
    k = klien_dengan([])  # readline mengembalikan "" = EOF
    with pytest.raises(GalatMcp, match="terputus"):
        k.panggil("undo", {})
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_figcraft_mcp.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'figcraft_mcp'`

- [ ] **Step 3: Tulis implementasi**

```python
# figcraft_mcp.py
"""Klien tipis untuk FigCraft MCP server dalam mode attached."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class GalatMcp(RuntimeError):
    """Perintah ditolak, atau sambungan ke server bermasalah."""


class KlienMcp:
    def __init__(self, cli: Path, port: int, timeout_detik: int = 180) -> None:
        self.proc = subprocess.Popen(
            [str(cli), "mcp", "--attach", str(port), "--timeout", str(timeout_detik)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self._id = 0
        self._kirim({
            "jsonrpc": "2.0",
            "id": self._id_berikut(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "kalender-baitul-qowwam", "version": "1.0"},
            },
        })
        self._baca()

    def _id_berikut(self) -> int:
        self._id += 1
        return self._id

    def _kirim(self, pesan: dict) -> None:
        if self.proc.stdin is None:
            raise GalatMcp("sambungan ke server terputus")
        self.proc.stdin.write(json.dumps(pesan) + "\n")
        self.proc.stdin.flush()

    def _baca(self) -> dict:
        while True:
            baris = self.proc.stdout.readline()
            if baris == "":
                raise GalatMcp("sambungan ke server terputus sebelum balasan diterima")
            baris = baris.strip()
            if not baris.startswith("{"):
                continue          # baris informasi, bukan JSON-RPC
            pesan = json.loads(baris)
            if "result" in pesan or "error" in pesan:
                return pesan

    def panggil(self, nama_tool: str, argumen: dict) -> dict:
        self._kirim({
            "jsonrpc": "2.0",
            "id": self._id_berikut(),
            "method": "tools/call",
            "params": {"name": nama_tool, "arguments": argumen},
        })
        pesan = self._baca()
        if "error" in pesan:
            raise GalatMcp(f"{nama_tool}: {pesan['error']}")
        hasil = pesan["result"]
        isi = hasil.get("content") or [{}]
        teks = isi[0].get("text", "")
        if hasil.get("isError"):
            raise GalatMcp(f"{nama_tool}: {teks}")
        try:
            return json.loads(teks)
        except (json.JSONDecodeError, TypeError):
            return {"teks": teks}

    def jalankan_batch(self, perintah: list[dict]) -> dict:
        """Satu langkah undo untuk seluruh perintah; gagal satu, batal semua."""
        return self.panggil("batch", {"commands": perintah})

    def tutup(self) -> None:
        try:
            if self.proc.stdin is not None:
                self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()

    def __enter__(self) -> "KlienMcp":
        return self

    def __exit__(self, *_) -> None:
        self.tutup()
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_figcraft_mcp.py -v`
Expected: 4 passed

- [ ] **Step 5: Uji asap terhadap app sungguhan**

App harus sudah jalan dari Task 1 Step 3.

```bash
python3 -c "
from pathlib import Path
from figcraft_mcp import KlienMcp
cli = Path.home()/'project/artCraft/FIGCRAFT/target/release/figcraft-cli'
with KlienMcp(cli, 40695) as k:
    print(k.panggil('inspect_document', {})['name'])
"
```

Expected: mencetak nama dokumen (`Untitled` kalau belum ada file dibuka).

- [ ] **Step 6: Commit**

```bash
git add figcraft_mcp.py tests/test_figcraft_mcp.py
git commit -m "Klien MCP attached untuk FigCraft"
```

---

### Task 6: Blok bulan

**Files:**
- Create: `blok_bulan.py`
- Create: `tests/test_blok_bulan.py`

**Interfaces:**
- Consumes: `kalender_data.Bulan`, `tema`.
- Produces: `perintah_blok_bulan(bulan: Bulan, x: float, y: float, induk: str | None = None) -> list[dict]` — daftar perintah siap kirim ke `batch`. Tiap perintah berbentuk `{"command": str, "params": dict, "as": str}`.

Catatan teknis: teks dibuat dengan `text.create` (params `text`, `x`, `y`, `props`), bidang dengan `node.create` (params `type`, `x`, `y`, `width`, `height`, `props`). Angka memakai `features: {"tnum": True}` supaya lebarnya seragam dan kolom tidak goyang.

- [ ] **Step 1: Tulis tes yang gagal**

```python
# tests/test_blok_bulan.py
import tema
from blok_bulan import perintah_blok_bulan
from kalender_data import bangun_bulan

JAN = bangun_bulan(2027, 1)


def perintah(nama_awalan, daftar):
    return [p for p in daftar if p.get("as", "").startswith(nama_awalan)]


def test_menghasilkan_tujuh_nama_hari():
    assert len(perintah("hari_", perintah_blok_bulan(JAN, 0, 0))) == 7


def test_hanya_hari_dalam_bulan_yang_dibuat():
    # Januari 31 hari: 31 angka tanggal, bukan 42.
    assert len(perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))) == 31


def test_minggu_memakai_rust_dan_bukan_merah():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))
    tiga_jan = next(p for p in tgl if p["as"] == "tgl_3")   # 3 Jan 2027 = Minggu
    assert tiga_jan["params"]["props"]["fill"] == tema.PALET["rust"]


def test_hari_biasa_memakai_ink():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))
    empat_jan = next(p for p in tgl if p["as"] == "tgl_4")
    assert empat_jan["params"]["props"]["fill"] == tema.PALET["ink"]


def test_hari_libur_mendapat_alas_kuning():
    alas = perintah("alas_", perintah_blok_bulan(JAN, 0, 0))
    # 1 Jan (Tahun Baru) dan 5 Jan (Isra Mikraj)
    assert {p["as"] for p in alas} == {"alas_1", "alas_5"}
    assert alas[0]["params"]["props"]["fill"] == tema.PALET["sun"]


def test_angka_tanggal_memakai_font_teks_bukan_tulisan_tangan():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 0, 0))
    for p in tgl:
        assert p["params"]["props"]["fontFamily"] == tema.FONT_TEKS


def test_nama_bulan_memakai_font_display():
    nama = next(p for p in perintah_blok_bulan(JAN, 0, 0) if p["as"] == "nama_bulan")
    assert nama["params"]["props"]["fontFamily"] == tema.FONT_DISPLAY
    assert nama["params"]["text"] == "JANUARI"


def test_posisi_tanggal_pertama_berada_di_kolom_jumat():
    tgl = perintah("tgl_", perintah_blok_bulan(JAN, 100.0, 200.0))
    satu = next(p for p in tgl if p["as"] == "tgl_1")
    diharapkan = 100.0 + 5 * tema.LEBAR_KOLOM_HARI
    assert abs(satu["params"]["x"] - diharapkan) < tema.LEBAR_KOLOM_HARI


def test_seluruh_perintah_punya_nama_unik():
    daftar = perintah_blok_bulan(JAN, 0, 0)
    nama = [p["as"] for p in daftar]
    assert len(nama) == len(set(nama))


def test_tidak_ada_bayangan_atau_gradien():
    for p in perintah_blok_bulan(JAN, 0, 0):
        props = p["params"].get("props", {})
        assert "effects" not in props
        assert not str(props.get("fill", "")).startswith("{")
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_blok_bulan.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'blok_bulan'`

- [ ] **Step 3: Tulis implementasi**

```python
# blok_bulan.py
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
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_blok_bulan.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add blok_bulan.py tests/test_blok_bulan.py
git commit -m "Perintah tata letak blok bulan"
```

---

### Task 7: Pita jadwal sholat

**Files:**
- Create: `pita_sholat.py`
- Create: `tests/test_pita_sholat.py`

**Interfaces:**
- Consumes: `kalender_data.Bulan.sholat`, `tema`.
- Produces: `perintah_pita_sholat(bulan: tuple[Bulan, ...], x: float, y: float, induk: str | None = None) -> list[dict]`

- [ ] **Step 1: Tulis tes yang gagal**

```python
# tests/test_pita_sholat.py
import tema
from kalender_data import bangun_lembar
from pita_sholat import perintah_pita_sholat

LEMBAR = bangun_lembar(1)


def test_empat_kolom_bulan():
    judul = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
             if p.get("as", "").startswith("judul_bulan_")]
    assert len(judul) == 4
    assert judul[0]["params"]["text"] == "JANUARI"


def test_enam_baris_rentang_per_bulan():
    baris = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
             if p.get("as", "").startswith("rentang_1_")]
    assert len(baris) == 6
    assert baris[0]["params"]["text"] == "1–5"


def test_kolom_maghrib_ditandai_kuning():
    alas = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
            if p.get("as", "").startswith("alas_maghrib_")]
    assert len(alas) == 4           # satu per bulan
    assert alas[0]["params"]["props"]["fill"] == tema.PALET["sun"]


def test_waktu_memakai_angka_lebar_seragam():
    waktu = [p for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0)
             if p.get("as", "").startswith("waktu_")]
    assert waktu, "tidak ada sel waktu"
    for p in waktu:
        assert p["params"]["props"]["features"] == {"tnum": True}


def test_memuat_catatan_koreksi_wilayah():
    teks = " ".join(p["params"].get("text", "") for p in perintah_pita_sholat(LEMBAR.bulan, 0, 0))
    assert "Kulon Progo" in teks and "Gunungkidul" in teks


def test_pita_tidak_melebihi_anggaran_tingginya():
    daftar = perintah_pita_sholat(LEMBAR.bulan, 0, 0.0)
    terbawah = max(p["params"]["y"] for p in daftar)
    assert terbawah <= tema.TINGGI_PITA_SHOLAT, terbawah
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_pita_sholat.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pita_sholat'`

- [ ] **Step 3: Tulis implementasi**

```python
# pita_sholat.py
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

        # alas kolom Maghrib: dicari paling sering, jadi ditandai
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
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_pita_sholat.py -v`
Expected: 6 passed

Kalau `test_pita_tidak_melebihi_anggaran_tingginya` gagal, kecilkan `TINGGI_BARIS`, jangan besarkan `tema.TINGGI_PITA_SHOLAT` — anggaran halaman sudah pas dan menambahnya akan memakan ruang nafas.

- [ ] **Step 5: Commit**

```bash
git add pita_sholat.py tests/test_pita_sholat.py
git commit -m "Perintah tata letak pita jadwal sholat"
```

---

### Task 8: Header, angka tahun, dan slot foto

**Files:**
- Create: `header.py`
- Create: `tests/test_header.py`

**Interfaces:**
- Consumes: `kalender_data.Lembar`, `tema`.
- Produces:
  - `perintah_header(lembar: Lembar, x: float, y: float, induk: str | None = None) -> list[dict]`
  - `SLOT_FOTO: dict[str, tuple[float, float]]` — nama slot → (lebar, tinggi) dalam mm, dipakai Task 9 untuk memasang foto.

- [ ] **Step 1: Tulis tes yang gagal**

```python
# tests/test_header.py
import tema
from header import SLOT_FOTO, perintah_header
from kalender_data import bangun_lembar

LEMBAR = bangun_lembar(1)


def test_empat_slot_foto_satu_utama_tiga_pendukung():
    assert set(SLOT_FOTO) == {"foto_utama", "foto_1", "foto_2", "foto_3"}
    assert SLOT_FOTO["foto_utama"][0] > SLOT_FOTO["foto_1"][0]


def test_slot_foto_dibuat_sebagai_layer_bernama():
    nama = {p["as"] for p in perintah_header(LEMBAR, 0, 0)}
    assert set(SLOT_FOTO).issubset(nama)


def test_angka_tahun_memakai_font_display():
    tahun = next(p for p in perintah_header(LEMBAR, 0, 0) if p["as"] == "angka_tahun")
    assert tahun["params"]["props"]["fontFamily"] == tema.FONT_DISPLAY
    assert tahun["params"]["text"] == "2027"


def test_nama_yayasan_memakai_font_tangan():
    nama = next(p for p in perintah_header(LEMBAR, 0, 0) if p["as"] == "nama_yayasan")
    assert nama["params"]["props"]["fontFamily"] == tema.FONT_TANGAN


def test_penanda_periode_sesuai_nomor_lembar():
    for nomor, diharapkan in ((1, "JANUARI — APRIL"), (2, "MEI — AGUSTUS"), (3, "SEPTEMBER — DESEMBER")):
        daftar = perintah_header(bangun_lembar(nomor), 0, 0)
        periode = next(p for p in daftar if p["as"] == "periode")
        assert diharapkan in periode["params"]["text"]
        assert f"{nomor}/3" in periode["params"]["text"]


def test_header_tidak_melebihi_anggaran_tingginya():
    daftar = perintah_header(LEMBAR, 0, 0.0)
    terbawah = max(
        p["params"]["y"] + p["params"].get("height", 0.0) for p in daftar
    )
    assert terbawah <= tema.TINGGI_HEADER, terbawah


def test_slot_foto_tidak_memakai_sudut_membulat():
    for p in perintah_header(LEMBAR, 0, 0):
        if p["as"] in SLOT_FOTO:
            assert "cornerRadius" not in p["params"]["props"]
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_header.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'header'`

- [ ] **Step 3: Tulis implementasi**

```python
# header.py
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
                       x_kanan + LEBAR_KANAN / 2, y + TINGGI_UTAMA / 2,
                       {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 2.8,
                        "fill": p["ink"], "textAlign": "center",
                        "letterSpacing": "0.5px"}, induk))

    y_pendukung = y + TINGGI_UTAMA + 5.0
    for i in range(3):
        nama = f"foto_{i + 1}"
        slot_x = x_kanan + i * (LEBAR_PENDUKUNG + 5.0)
        hasil.append(_bidang(nama, slot_x, y_pendukung, LEBAR_PENDUKUNG, TINGGI_PENDUKUNG,
                             {"fill": p[_WARNA_SLOT[i]], "stroke": p["ink"],
                              "strokeWeight": 0.7}, induk))
        hasil.append(_teks(f"label_{nama}", f"FOTO {i + 1}",
                           slot_x + LEBAR_PENDUKUNG / 2,
                           y_pendukung + TINGGI_PENDUKUNG / 2,
                           {"fontFamily": tema.FONT_TEKS, "fontStyle": "Bold", "fontSize": 2.8,
                            "fill": p["ink"], "textAlign": "center"}, induk))
    return hasil
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_header.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add header.py tests/test_header.py
git commit -m "Perintah tata letak header dan slot foto"
```

---

### Task 9: Orkestrator — bangun 3 lembar, simpan, ekspor

**Files:**
- Create: `build_kalender.py`
- Create: `tests/test_build_kalender.py`

**Interfaces:**
- Consumes: semua modul sebelumnya.
- Produces:
  - `perintah_lembar(lembar: Lembar) -> list[dict]` — seluruh perintah satu halaman, sudah ditempatkan pada koordinat halaman.
  - `kirim_perintah(klien, perintah: list[dict]) -> dict[str, int]` — mengirim per potongan dan mengembalikan peta `nama "as"` → `id node`.
  - `pasang_foto(klien, dir_foto: Path, id_slot: dict[str, int]) -> list[str]` — nama slot yang terisi.
  - `main(argv: list[str] | None = None) -> int`

**Fakta API yang sudah diverifikasi** (jangan diubah tanpa mengecek ulang):
- Halaman baru dibuat dengan `page.add {name?}`. **Tidak ada `page.create`.**
- Latar halaman diatur dengan `page.setBackground {id?, color}`.
- `get_node` hanya menerima `id`, **bukan `name`**. Maka id slot foto harus diambil dari hasil `batch`.
- `batch` mengembalikan daftar hasil **berurutan posisi**, sejajar dengan urutan `commands` yang dikirim — bukan kamus berkunci `as`. Jadi id diambil dengan `zip(perintah, hasil)`.

Argumen CLI: `--port` (default 40695), `--foto-dir` (default `assets/foto`), `--keluar` (default `dist`), `--lembar` (boleh diulang; default ketiganya).

- [ ] **Step 1: Tulis tes yang gagal**

```python
# tests/test_build_kalender.py
import tema
from build_kalender import perintah_lembar
from kalender_data import bangun_lembar

LEMBAR = bangun_lembar(1)
PERINTAH = perintah_lembar(LEMBAR)


def test_memuat_header_empat_bulan_dan_pita():
    nama = {p["as"] for p in PERINTAH}
    assert "angka_tahun" in nama
    assert "judul_pita" in nama
    assert sum(1 for n in nama if n.startswith("bulan_1_nama_bulan")) == 1


def test_nama_perintah_unik_di_seluruh_halaman():
    nama = [p["as"] for p in PERINTAH]
    assert len(nama) == len(set(nama)), [n for n in nama if nama.count(n) > 1][:5]


def test_semua_elemen_di_dalam_margin():
    for p in PERINTAH:
        assert p["params"]["x"] >= tema.MARGIN - 3.0, p["as"]
        assert p["params"]["x"] <= tema.LEBAR_HALAMAN - tema.MARGIN + 3.0, p["as"]
        assert p["params"]["y"] >= tema.MARGIN - 3.0, p["as"]
        assert p["params"]["y"] <= tema.TINGGI_HALAMAN - tema.MARGIN, p["as"]


def test_jumlah_perintah_wajar():
    # 4 bulan × (±31 hari × 3 teks) + kisi + pita + header
    assert 500 < len(PERINTAH) < 1200, len(PERINTAH)
```

- [ ] **Step 2: Jalankan tes, pastikan gagal**

Run: `python3 -m pytest tests/test_build_kalender.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_kalender'`

- [ ] **Step 3: Tulis implementasi**

```python
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
    hasil: list[dict] = list(perintah_header(lembar, x0, y0))

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

            klien.panggil("export", {
                "format": "pdf", "path": str(arg.keluar / "kalender-2027-cetak.pdf"),
                "cmyk": True, "bleed": tema.BLEED, "bleedMarks": True,
            })
            klien.panggil("export", {
                "format": "pdf", "path": str(arg.keluar / "kalender-2027-layar.pdf"),
            })
            for nomor in nomor_lembar:
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
```

- [ ] **Step 4: Jalankan tes, pastikan lulus**

Run: `python3 -m pytest tests/test_build_kalender.py -v`
Expected: 4 passed

- [ ] **Step 5: Bangun lembar 1 sungguhan dan lihat hasilnya**

```bash
python3 build_kalender.py --lembar 1
```

Buka `dist/lembar-1.png` dan **lihat**. Periksa satu per satu:
- Tidak ada teks yang luber keluar selnya atau bertindih.
- Angka tanggal Minggu berwarna oranye bata, bukan hitam.
- 1 dan 5 Januari beralas kuning.
- Nama bulan tampil dengan goresan tangan, angka tanggal tidak.
- Kolom Maghrib bertanda kuning di keempat bulan.
- Isi mengisi tinggi halaman, tidak menumpuk di atas.

Kalau ada yang meleset, perbaiki modul yang bersangkutan dan jalankan ulang. Jangan lanjut ke Step 6 sebelum lembar 1 benar.

- [ ] **Step 6: Bangun ketiga lembar**

Run: `python3 build_kalender.py`
Expected: `dist/` memuat `.figcraft`, dua PDF, dan tiga PNG. Lihat ketiga PNG.

- [ ] **Step 7: Commit**

```bash
git add build_kalender.py tests/test_build_kalender.py
git commit -m "Orkestrator build tiga lembar kalender"
```

---

### Task 10: Uji paritas data 365 hari

**Files:**
- Create: `tests/test_paritas.py`

**Interfaces:**
- Consumes: `kalender_data`, `generate_kalender`.

Tes ini menjaga hal yang paling mudah rusak tanpa ketahuan: satu hari meleset di tengah tahun tidak akan terlihat mata, tetapi membuat kalender salah cetak.

- [ ] **Step 1: Tulis tes**

```python
# tests/test_paritas.py
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
```

- [ ] **Step 2: Jalankan dan pastikan lulus**

Run: `python3 -m pytest tests/test_paritas.py -v`
Expected: 4 passed

Kalau `test_waktu_sholat_rentang_tidak_pernah_lebih_awal` gagal, itu berarti aturan "ambil waktu paling akhir" rusak — perbaiki `ringkas_sholat`, jangan longgarkan tesnya. Tes inilah yang menjaga agar tidak ada yang berbuka sebelum waktunya.

- [ ] **Step 3: Commit**

```bash
git add tests/test_paritas.py
git commit -m "Uji paritas data 365 hari terhadap sumbernya"
```

---

### Task 11: Bersihkan modul lama dan tulis README

**Files:**
- Modify: `generate_kalender.py` (hapus fungsi render HTML)
- Delete: `build_via_figcraft_mcp.py`
- Create: `README.md`

- [ ] **Step 1: Pastikan seluruh tes hijau sebelum menghapus apa pun**

Run: `python3 -m pytest -q`
Expected: semua lulus. Kalau ada yang merah, perbaiki dulu — jangan menghapus kode saat tes merah.

- [ ] **Step 2: Hapus modul render HTML yang tidak dipakai lagi**

Buang dari `generate_kalender.py`: `render_month_html`, `render_sheet_html`, `generate_html`, `main`, dan `import html`. Sisakan data dan hitungan: `PASARAN_NAMES`, `MONTH_NAMES_ID`, `HIJRI_MONTHS`, `HOLIDAYS_2027`, `get_pasaran`, `build_hijri_jawa_map`, seluruh fungsi astronomi, dan `prayer_times_yogya`.

Alasannya: tata letak sekarang ada di modul FigCraft. Membiarkan dua jalur render berarti dua sumber kebenaran yang akan menyimpang diam-diam.

- [ ] **Step 3: Hapus pembangun versi pertama**

```bash
git rm build_via_figcraft_mcp.py
```

- [ ] **Step 4: Jalankan seluruh tes lagi**

Run: `python3 -m pytest -q`
Expected: semua lulus. Ini membuktikan penghapusan tadi tidak memutus apa pun.

- [ ] **Step 5: Tulis README**

````markdown
# Kalender Dinding 2027 — Yayasan Islam Baitul Qowwam

Tiga lembar A2 (42 × 59,4 cm), empat bulan per lembar, memuat tanggal Masehi,
Hijriah dan Jawa, serta jadwal sholat WIB untuk D.I. Yogyakarta.

## Menyiapkan

```bash
./scripts/pasang_font.sh          # sekali saja
```

## Membangun

Hidupkan app FigCraft lebih dulu:

```bash
FIGCRAFT=~/project/artCraft/FIGCRAFT/target/release/figcraft
"$FIGCRAFT" --control 40695 \
  --automation-read-root "$PWD" \
  --automation-write-root "$PWD/dist" &
```

Lalu:

```bash
python3 build_kalender.py            # ketiga lembar
python3 build_kalender.py --lembar 1 # satu lembar saja
```

Keluaran di `dist/`:

| Berkas | Untuk |
|---|---|
| `kalender-2027-cetak.pdf` | Percetakan: CMYK, bleed 3 mm, bleed marks |
| `kalender-2027-layar.pdf` | Dibagikan dan diperiksa |
| `lembar-{1,2,3}.png` | Pratinjau cepat |
| `kalender-baitul-qowwam-2027.figcraft` | Berkas sumber, bisa disunting di FigCraft |

## Mengganti foto

Taruh foto di `assets/foto/`. Namanya adalah nama slot diikuti nomor lembar,
jadi tiap lembar punya fotonya sendiri (boleh `.jpg`, `.jpeg` atau `.png`):

```
assets/foto/foto_utama_1.jpg   foto_1_1.jpg   foto_2_1.jpg   foto_3_1.jpg
assets/foto/foto_utama_2.jpg   foto_1_2.jpg   foto_2_2.jpg   foto_3_2.jpg
assets/foto/foto_utama_3.jpg   foto_1_3.jpg   foto_2_3.jpg   foto_3_3.jpg
```

Lalu bangun ulang. Slot yang fotonya belum ada tetap tampil sebagai bidang
warna berlabel, jadi kalender tetap layak dilihat meski belum lengkap.

Resolusi minimum supaya tajam saat dicetak:

| Slot | Ukuran cetak | Minimum piksel |
|---|---|---|
| `foto_utama_*` | 244 × 84 mm | 2882 × 992 |
| `foto_1..3_*` | 78 × 40 mm | 921 × 472 |

Foto yang lebih kecil tetap terpasang, tetapi akan pecah saat dicetak.

## Menjalankan tes

```bash
python3 -m pytest -q
```

## Yang perlu diketahui sebelum cetak

- Tanggal Hijriah di sini adalah **hitungan**, bukan ketetapan. Awal Ramadan,
  Idulfitri dan Iduladha ditentukan Sidang Isbat Kemenag RI dan bisa bergeser
  satu hari.
- Waktu sholat dihitung dengan metode Kemenag RI (Subuh 20°, Isya 18°,
  ihtiyati +2 menit) untuk Kota Yogyakarta. Tiap sel memuat waktu **paling
  akhir** dalam rentang 5 harinya, supaya tidak mungkin sholat atau berbuka
  sebelum waktunya masuk.
- **Minta proof cetak** sebelum cetak massal. Konversi CMYK belum pernah diuji
  pada proyek ini, dan teal pekat adalah warna yang paling rawan bergeser.
````

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "Hapus jalur render lama dan tulis README"
```

---

## Self-Review

**Cakupan spec.** Tiap pasal spec ada tasknya: §3 geometri → Task 4; §4 tipografi → Task 1 dan 6; §5 warna → Task 4 dan 6; §6 blok bulan → Task 6; §7 pita sholat → Task 2 dan 7; §8 slot foto → Task 8 dan 9; §9 pipeline data → Task 2, 3, 11; §10 pipeline build → Task 5 dan 9; §11 aset dan lisensi → Task 1; §12 verifikasi → Task 9 Step 5 dan Task 10; §13 batasan → README di Task 11.

**Konsistensi nama.** `perintah_blok_bulan`, `perintah_pita_sholat`, `perintah_header`, `perintah_lembar` dipakai dengan nama yang sama di modul dan tesnya. `KlienMcp.panggil` dan `KlienMcp.jalankan_batch` konsisten di Task 5 dan 9. `SLOT_FOTO` didefinisikan di Task 8 dan dipakai di Task 9.

**Koreksi setelah verifikasi terhadap app yang berjalan.** Tiga anggapan dalam draf pertama rencana ini salah dan sudah diperbaiki di atas:

1. `page.create` tidak ada; yang benar `page.add {name?}`.
2. `get_node` tidak menerima `name`, hanya `id`. Karena itu id slot foto diambil dari hasil `batch`, lewat `kirim_perintah`.
3. `batch` membalas daftar hasil berurutan posisi, bukan kamus berkunci `as` — pemetaan dilakukan dengan `zip`.

Satu cacat logika juga ditemukan saat memperbaikinya: `id_slot` semula ditimpa pada tiap lembar, sehingga foto hanya akan terpasang di lembar terakhir. Kini id disimpan per lembar dan nama berkas foto memuat nomor lembarnya.

**Risiko tersisa.** `fontStyle` untuk Plus Jakarta Sans variabel mungkin tidak menerima `"SemiBold"` atau `"Bold"`. Task 1 Step 4 memeriksanya sebelum kode apa pun ditulis; kalau hanya `Regular` yang tersedia, berat diatur lewat `text.setVariations` dengan `{"wght": 600}` atau `{"wght": 700}`, dan seluruh `props` yang memakai `fontStyle` di Task 6, 7 dan 8 harus menyesuaikan. Ini risiko yang dampaknya terlihat jelas di layar, bukan kesalahan senyap.
