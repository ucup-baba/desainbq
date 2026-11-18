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
