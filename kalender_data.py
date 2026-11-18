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
