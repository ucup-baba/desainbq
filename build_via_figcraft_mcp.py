#!/usr/bin/env python3
"""Bangun Kalender 2027 (3 Lembar x 4 Bulan) melalui FigCraft MCP server.

Tata letak mengikuti referensi kalender dinding Indonesia:
- Atas: Header Yayasan Baitul Qowwam + Badge KALENDER 2027 + Placeholder Foto Utama,
  3 Placeholder Foto Hexagon (kanan), & 4 Placeholder Foto Kotak (bawah hero)
- Tengah: Grid 4 Bulan (2x2) dengan angka Masehi besar, Hijriah, Jawa + Pasaran,
  serta strip hari libur nasional per bulan
- Bawah (di bawah kalender 4 bulan): Jadwal Waktu Sholat Harian WIB lengkap
  (Subuh, Dzuhur, Ashar, Maghrib, Isya) untuk Kota Yogyakarta & sekitarnya (DIY)
"""

from __future__ import annotations

import calendar
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from generate_kalender import (
    HOLIDAYS_2027,
    MONTH_NAMES_ID,
    build_hijri_jawa_map,
    prayer_times_yogya,
)

ROOT_DIR = Path(__file__).resolve().parent
REPO_DIR = ROOT_DIR.parent
FIGCRAFT_CLI = REPO_DIR / "target" / "release" / "figcraft-cli"

PAGE_W = 842.0   # A3 portrait width (pt)
PAGE_H = 1191.0  # A3 portrait height (pt)
MARGIN_X = 20.0
CONTENT_W = PAGE_W - 2 * MARGIN_X  # 802.0

DAY_NAMES_ID = ("Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jum'at", "Sabtu")

# Palet Warna Identitas Yayasan Baitul Qowwam (Emerald + Teal + Gold + Crimson Holiday)
C_WHITE = "#FFFFFF"
C_EMERALD_DARK = "#0A4234"
C_EMERALD = "#0F5C46"
C_EMERALD_MID = "#157358"
C_EMERALD_PALE = "#EBF5F1"
C_TEAL_BG = "#DDF0EA"
C_GOLD = "#E2A829"
C_GOLD_LIGHT = "#F8DF94"
C_RED = "#D91E2A"
C_RED_SOFT = "#FFF2F3"
C_AMBER = "#B45309"
C_AMBER_SOFT = "#FFFBEB"
C_TEXT = "#13201D"
C_MUTED = "#556862"
C_TRAIL = "#C6D0CD"
C_BORDER = "#BDD0C9"
C_CELL_BORDER = "#E1EAE6"
C_JAWA = "#6A4E14"
C_ROW_ALT = "#F4F9F7"
C_ROW_FRI = "#E7F4EE"


class McpClient:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [
                str(FIGCRAFT_CLI),
                "mcp",
                "--automation-read-root",
                str(ROOT_DIR),
                "--automation-write-root",
                str(ROOT_DIR),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._id = 0
        self._send(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "kalender-builder", "version": "2.0"},
                },
            }
        )
        self._read_resp()
        assert self.proc.stdin is not None
        self.proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        self.proc.stdin.flush()

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    def _send(self, payload: dict) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def _read_resp(self) -> dict:
        assert self.proc.stdout is not None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                err = self.proc.stderr.read() if self.proc.stderr else ""
                raise RuntimeError(f"MCP server closed unexpectedly: {err}")
            msg = json.loads(line)
            if "id" in msg:
                if "error" in msg:
                    raise RuntimeError(f"MCP error: {msg['error']}")
                return msg["result"]

    def call(self, tool_name: str, arguments: dict) -> dict:
        self._send(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            }
        )
        res = self._read_resp()
        if res.get("isError"):
            raise RuntimeError(f"Tool {tool_name} error: {res}")
        content = res.get("content", [])
        if content and content[0].get("type") == "text":
            return json.loads(content[0]["text"])
        return res

    def create_frame(
        self,
        name: str,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str = C_WHITE,
        parent: int | None = None,
        corner_radius: float = 0.0,
        stroke: str | None = None,
        stroke_weight: float = 1.0,
    ) -> int:
        props: dict = {"fills": [{"type": "solid", "color": fill}]}
        if corner_radius > 0:
            props["cornerRadius"] = corner_radius
        if stroke:
            props["strokes"] = [{"type": "solid", "color": stroke}]
            props["strokeWeight"] = stroke_weight
        args: dict = {
            "type": "frame",
            "name": name,
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "props": props,
        }
        if parent is not None:
            args["parent"] = parent
        return self.call("create_node", args)["id"]

    def create_rect(
        self,
        parent: int,
        name: str,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        corner_radius: float = 0.0,
        stroke: str | None = None,
        stroke_weight: float = 0.75,
    ) -> int:
        props: dict = {"fills": [{"type": "solid", "color": fill}]}
        if corner_radius > 0:
            props["cornerRadius"] = corner_radius
        if stroke:
            props["strokes"] = [{"type": "solid", "color": stroke}]
            props["strokeWeight"] = stroke_weight
        return self.call(
            "create_node",
            {
                "type": "rect",
                "parent": parent,
                "name": name,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "props": props,
            },
        )["id"]

    def create_polygon(
        self,
        parent: int,
        name: str,
        x: float,
        y: float,
        w: float,
        h: float,
        point_count: int,
        fill: str,
        stroke: str | None = None,
        stroke_weight: float = 2.0,
    ) -> int:
        props: dict = {
            "pointCount": point_count,
            "fills": [{"type": "solid", "color": fill}],
        }
        if stroke:
            props["strokes"] = [{"type": "solid", "color": stroke}]
            props["strokeWeight"] = stroke_weight
        return self.call(
            "create_node",
            {
                "type": "polygon",
                "parent": parent,
                "name": name,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "props": props,
            },
        )["id"]

    def create_text(
        self,
        parent: int,
        name: str,
        x: float,
        y: float,
        w: float,
        h: float,
        text: str,
        size: float,
        color: str,
        weight: int = 400,
        align: str = "LEFT",
    ) -> int:
        return self.call(
            "create_node",
            {
                "type": "text",
                "parent": parent,
                "name": name,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "text": text,
                "props": {
                    "fontSize": size,
                    "fontWeight": weight,
                    "textAlignHorizontal": align,
                    "textAutoResize": "NONE",
                    "fills": [{"type": "solid", "color": color}],
                },
            },
        )["id"]

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait(timeout=10)


def build_hero_section(mcp: McpClient, sheet_id: int, sheet_num: int, months: list[int]) -> None:
    """Bangun bagian atas (banner Yayasan Baitul Qowwam + KALENDER 2027 + placeholder foto)."""
    hero_id = mcp.create_frame(
        f"Hero Lembar {sheet_num}",
        MARGIN_X,
        16.0,
        CONTENT_W,
        270.0,
        fill=C_EMERALD_DARK,
        parent=sheet_id,
        corner_radius=8.0,
    )

    # Panel atas gelap dengan aksen emas & area foto kanan
    mcp.create_rect(hero_id, "Aksen Atas Emas", 0, 0, CONTENT_W, 4, C_GOLD)
    mcp.create_rect(hero_id, "Backdrop Kanan", 560, 4, 242, 266, "#083328")
    mcp.create_rect(hero_id, "Garis Pemisah Vertikal", 556, 4, 4, 266, C_GOLD)

    # Area Foto Utama (kiri tengah, bisa langsung diisi foto kegiatan Yayasan)
    mcp.create_rect(
        hero_id,
        "Placeholder Foto Utama",
        14,
        82,
        530,
        118,
        C_TEAL_BG,
        corner_radius=6.0,
        stroke=C_GOLD,
        stroke_weight=1.5,
    )
    mcp.create_text(
        hero_id,
        "Label Foto Utama",
        14,
        128,
        530,
        26,
        "PLACEHOLDER FOTO UTAMA KEGIATAN YAYASAN BAITUL QOWWAM\n(Klik frame ini di FigCraft untuk mengganti dengan foto)",
        8.5,
        C_EMERALD_DARK,
        weight=600,
        align="CENTER",
    )

    # Placeholder Logo + Judul Yayasan di bagian atas kiri
    logo_box = mcp.create_frame(
        "Placeholder Logo Yayasan",
        14,
        12,
        56,
        56,
        fill=C_WHITE,
        parent=hero_id,
        corner_radius=10.0,
        stroke=C_GOLD,
        stroke_weight=2.0,
    )
    mcp.create_text(
        logo_box,
        "Logo Teks",
        2,
        17,
        52,
        24,
        "LOGO\nBQ",
        9.0,
        C_EMERALD_DARK,
        weight=700,
        align="CENTER",
    )

    mcp.create_text(
        hero_id,
        "Judul Yayasan",
        80,
        12,
        465,
        28,
        "YAYASAN BAITUL QOWWAM",
        22.5,
        C_WHITE,
        weight=800,
    )
    mcp.create_text(
        hero_id,
        "Subjudul Wilayah",
        80,
        40,
        310,
        16,
        "D.I. YOGYAKARTA & SEKITARNYA",
        10.5,
        C_GOLD_LIGHT,
        weight=700,
    )
    mcp.create_rect(hero_id, "Ribbon Tagline", 80, 58, 360, 16, C_GOLD, corner_radius=8.0)
    mcp.create_text(
        hero_id,
        "Teks Tagline",
        80,
        61,
        360,
        12,
        "• PENDIDIKAN • SOSIAL • DAKWAH • PEMBERDAYAAN UMAT •",
        7.0,
        "#082920",
        weight=700,
        align="CENTER",
    )

    # 4 Placeholder Foto Kotak Kecil di bawah Foto Utama (persis seperti referensi)
    box_w = 126.5
    for idx in range(4):
        bx = 14.0 + idx * (box_w + 8.0)
        mcp.create_rect(
            hero_id,
            f"Bingkai Foto {idx + 1}",
            bx,
            206,
            box_w,
            56,
            C_WHITE,
            corner_radius=4.0,
            stroke=C_GOLD,
            stroke_weight=1.5,
        )
        mcp.create_rect(
            hero_id,
            f"Placeholder Foto {idx + 1}",
            bx + 4,
            210,
            box_w - 8,
            48,
            C_EMERALD_PALE,
            corner_radius=2.0,
        )
        mcp.create_text(
            hero_id,
            f"Label Foto {idx + 1}",
            bx + 4,
            228,
            box_w - 8,
            14,
            f"FOTO KEGIATAN {idx + 1}",
            7.2,
            C_EMERALD_DARK,
            weight=700,
            align="CENTER",
        )

    # Badge KALENDER 2027 di kanan atas
    mcp.create_rect(hero_id, "Badge Tahun", 574, 12, 214, 54, C_WHITE, corner_radius=8.0)
    mcp.create_rect(hero_id, "Strip Tahun Emas", 574, 12, 214, 16, C_GOLD, corner_radius=4.0)
    period_txt = f"KALENDER  •  {MONTH_NAMES_ID[months[0]][:3]}–{MONTH_NAMES_ID[months[-1]][:3]}  •  {sheet_num}/3"
    mcp.create_text(
        hero_id,
        "Label Kalender",
        574,
        15,
        214,
        12,
        period_txt,
        7.2,
        "#082920",
        weight=800,
        align="CENTER",
    )
    mcp.create_text(
        hero_id,
        "Angka 2027",
        574,
        29,
        214,
        34,
        "2027",
        27.0,
        C_EMERALD_DARK,
        weight=800,
        align="CENTER",
    )

    # 3 Placeholder Foto Hexagon di sisi kanan (seperti referensi)
    hex_positions = [
        (586, 74, 86),
        (686, 122, 86),
        (586, 174, 86),
    ]
    for idx, (hx, hy, hs) in enumerate(hex_positions, start=1):
        mcp.create_polygon(
            hero_id,
            f"Placeholder Hex Foto {idx}",
            hx,
            hy,
            hs,
            hs,
            6,
            C_TEAL_BG,
            stroke=C_WHITE,
            stroke_weight=3.0,
        )
        mcp.create_text(
            hero_id,
            f"Label Hex {idx}",
            hx,
            hy + hs * 0.42,
            hs,
            16,
            f"FOTO\nHEX {idx}",
            7.0,
            C_EMERALD_DARK,
            weight=700,
            align="CENTER",
        )


def build_month_card(
    mcp: McpClient,
    sheet_id: int,
    month: int,
    card_x: float,
    card_y: float,
    hj_map: dict[dt.date, dict],
) -> None:
    """Bangun 1 kartu bulan dengan angka Masehi besar, Hijriah, Jawa + Pasaran & strip libur."""
    card_w = 394.0
    card_h = 274.0
    card_id = mcp.create_frame(
        f"Bulan {MONTH_NAMES_ID[month]}",
        card_x,
        card_y,
        card_w,
        card_h,
        fill=C_WHITE,
        parent=sheet_id,
        corner_radius=6.0,
        stroke=C_BORDER,
        stroke_weight=0.8,
    )

    month_days = [
        dt.date(2027, month, d)
        for d in range(1, calendar.monthrange(2027, month)[1] + 1)
    ]
    first_info = hj_map[month_days[0]]
    last_info = hj_map[month_days[-1]]

    if first_info["h_name"] == last_info["h_name"]:
        hijri_span = f"{first_info['h_name']} {first_info['h_year']} H"
    elif first_info["h_year"] == last_info["h_year"]:
        hijri_span = f"{first_info['h_name']} {first_info['h_year']} - {last_info['h_name']} {last_info['h_year']}"
    else:
        hijri_span = f"{first_info['h_name']} {first_info['h_year']} - {last_info['h_name']} {last_info['h_year']}"

    if first_info["j_name"] == last_info["j_name"]:
        jawa_span = f"{first_info['j_name']} {first_info['j_year']}"
    elif first_info["j_year"] == last_info["j_year"]:
        jawa_span = f"{first_info['j_name']} {first_info['j_year']} - {last_info['j_name']} {last_info['j_year']}"
    else:
        jawa_span = f"{first_info['j_name']} {first_info['j_year']} - {last_info['j_name']} {last_info['j_year']}"

    # Header bulan gaya referensi: Pill nomor + Nama bulan di kiri, Hijriah & Jawa di kanan
    mcp.create_rect(card_id, "Bar Header Bulan", 0, 0, card_w, 26, C_EMERALD_PALE)
    mcp.create_rect(card_id, "Pill Bulan", 4, 3, 182, 20, C_EMERALD_DARK, corner_radius=10.0)
    mcp.create_rect(card_id, "Badge Nomor Bulan", 6, 5, 22, 16, C_WHITE, corner_radius=8.0)
    mcp.create_text(
        card_id,
        "Nomor Bulan",
        6,
        7,
        22,
        12,
        f"{month:02d}",
        8.5,
        C_RED,
        weight=800,
        align="CENTER",
    )
    mcp.create_text(
        card_id,
        "Nama Bulan",
        32,
        6,
        150,
        14,
        MONTH_NAMES_ID[month],
        11.0,
        C_WHITE,
        weight=800,
    )

    mcp.create_text(
        card_id,
        "Span Hijriah",
        192,
        4,
        196,
        10,
        hijri_span,
        6.2,
        C_EMERALD_DARK,
        weight=700,
        align="RIGHT",
    )
    mcp.create_text(
        card_id,
        "Span Jawa",
        192,
        14,
        196,
        10,
        jawa_span,
        6.0,
        C_JAWA,
        weight=600,
        align="RIGHT",
    )

    # Header hari (7 kolom x 56.28 pt = 394)
    col_w = card_w / 7.0
    for idx, day_name in enumerate(DAY_NAMES_ID):
        hx = idx * col_w
        bg = C_RED if idx == 0 else C_EMERALD
        mcp.create_rect(card_id, f"Hdr {day_name}", hx, 26, col_w, 16, bg)
        mcp.create_text(
            card_id,
            f"Txt {day_name}",
            hx,
            29,
            col_w,
            11,
            day_name,
            7.2,
            C_WHITE,
            weight=700,
            align="CENTER",
        )

    # Grid 6 minggu x 7 hari (y = 42 .. 258 -> row_h = 36.0 pt)
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(2027, month)
    while len(weeks) < 6:
        last_d = weeks[-1][-1]
        weeks.append([last_d + dt.timedelta(days=i + 1) for i in range(7)])

    row_h = 36.0
    start_y = 42.0
    for r_idx, week in enumerate(weeks):
        cy = start_y + r_idx * row_h
        for c_idx, d in enumerate(week):
            cx = c_idx * col_w
            if d.month != month:
                mcp.create_rect(
                    card_id,
                    f"Trail {r_idx}-{c_idx}",
                    cx,
                    cy,
                    col_w,
                    row_h,
                    C_WHITE,
                    stroke=C_CELL_BORDER,
                    stroke_weight=0.4,
                )
                mcp.create_text(
                    card_id,
                    f"TrailNum {r_idx}-{c_idx}",
                    cx,
                    cy + 8,
                    col_w,
                    20,
                    str(d.day),
                    15.0,
                    C_TRAIL,
                    weight=700,
                    align="CENTER",
                )
                continue

            info = hj_map[d]
            holiday = HOLIDAYS_2027.get(d)
            is_sunday = c_idx == 0

            bg = C_WHITE
            num_color = C_TEXT
            if is_sunday or (holiday and holiday[0] == "libur"):
                bg = C_RED_SOFT
                num_color = C_RED
            elif holiday and holiday[0] == "cuti":
                bg = C_AMBER_SOFT
                num_color = C_AMBER

            mcp.create_rect(
                card_id,
                f"Sel {d.isoformat()}",
                cx,
                cy,
                col_w,
                row_h,
                bg,
                stroke=C_CELL_BORDER,
                stroke_weight=0.45,
            )

            # Angka Masehi besar di kiri/tengah
            mcp.create_text(
                card_id,
                f"M {d.day}",
                cx + 2,
                cy + 3,
                32,
                22,
                str(d.day),
                18.5,
                num_color,
                weight=800,
                align="CENTER",
            )

            # Hijriah di kanan atas
            h_lbl = (
                f"{info['h_day']} {info['h_short']}"
                if info["h_day"] == 1 or d.day == 1
                else f"{info['h_day']}"
            )
            mcp.create_text(
                card_id,
                f"H {d.isoformat()}",
                cx + 26,
                cy + 4,
                col_w - 29,
                10,
                h_lbl,
                6.2,
                C_EMERALD,
                weight=700,
                align="RIGHT",
            )

            # Jawa + Pasaran di bagian bawah sel (rapi & jelas)
            j_lbl = f"{info['j_day']} {info['pasaran']}"
            mcp.create_text(
                card_id,
                f"J {d.isoformat()}",
                cx + 2,
                cy + 25.5,
                col_w - 4,
                9,
                j_lbl,
                5.7,
                C_JAWA,
                weight=600,
                align="CENTER",
            )

    # Strip Hari Libur di bawah kartu bulan (y = 256, h = 18)
    if month == 3:
        strip_txt = "8 Mar: Nyepi 1949 • 10-11 Mar: Idulfitri 1448 H (Cuti: 9,12,15) • 26 Mar: Wafat Yesus Kristus (Cuti: 25) • 28 Mar: Paskah"
    elif month == 5:
        strip_txt = "1 Mei: Hari Buruh • 6 Mei: Kenaikan Yesus Kristus • 17 Mei: Iduladha 1448 H (Cuti: 18) • 20 Mei: Waisak 2571 BE (Cuti: 19)"
    else:
        month_holidays = [
            (d, kind, desc)
            for d, (kind, desc) in sorted(HOLIDAYS_2027.items())
            if d.month == month
        ]
        if month_holidays:
            parts = []
            for d, kind, desc in month_holidays:
                tag = "Cuti" if kind == "cuti" else MONTH_NAMES_ID[month][:3]
                parts.append(f"{d.day} {tag}: {desc}")
            strip_txt = " • ".join(parts)
        else:
            strip_txt = f"{hijri_span.upper()}  •  {jawa_span.upper()}"

    mcp.create_rect(card_id, "Strip Libur Bulan", 0, 257, card_w, 17, C_EMERALD_DARK)
    mcp.create_text(
        card_id,
        "Teks Libur Bulan",
        6,
        261.5,
        card_w - 12,
        10,
        strip_txt,
        5.5,
        C_WHITE,
        weight=600,
    )


def build_prayer_section(mcp: McpClient, sheet_id: int, sheet_num: int, months: list[int]) -> None:
    """Bangun tabel Jadwal Waktu Sholat Harian WIB (4 bulan berdampingan) di bawah kalender."""
    sec_y = 864.0
    sec_h = 298.0
    sec_id = mcp.create_frame(
        f"Jadwal Sholat Lembar {sheet_num}",
        MARGIN_X,
        sec_y,
        CONTENT_W,
        sec_h,
        fill=C_WHITE,
        parent=sheet_id,
        corner_radius=6.0,
        stroke=C_BORDER,
        stroke_weight=0.8,
    )

    # Header bar bagian Jadwal Sholat
    mcp.create_rect(sec_id, "Header Jadwal Sholat", 0, 0, CONTENT_W, 20, C_EMERALD_DARK)
    mcp.create_text(
        sec_id,
        "Judul Jadwal Sholat",
        10,
        5,
        460,
        12,
        "JADWAL WAKTU SHOLAT HARIAN (WIB) • KOTA YOGYAKARTA & SEKITARNYA (KEMENAG RI +2' IHTIYATI)",
        7.3,
        C_WHITE,
        weight=700,
    )
    mcp.create_text(
        sec_id,
        "Koreksi Wilayah DIY",
        470,
        5.5,
        322,
        11,
        "Koreksi DIY: Yogya/Sleman/Bantul ±0' • Kulon Progo +1' • Gunungkidul -1'",
        6.5,
        C_GOLD_LIGHT,
        weight=600,
        align="RIGHT",
    )

    # 4 kolom tabel berdampingan (masing-masing 196 pt, gap 6 pt -> 4*196 + 3*6 = 802)
    tbl_w = 196.0
    gap = 6.0
    # Tinggi tabel = 278 pt (y = 20..298)
    # Title bulan = 13 pt, Header kolom = 12 pt, 31 baris x 8.15 pt = 252.65 pt (total 277.65 pt)
    col_xs = (2.0, 26.0, 60.0, 94.0, 128.0, 162.0)
    col_ws = (22.0, 32.0, 32.0, 32.0, 32.0, 32.0)
    headers = ("Tgl", "Subuh", "Dzuhur", "Ashar", "Maghrib", "Isya")

    for m_idx, month in enumerate(months):
        tx = m_idx * (tbl_w + gap)
        tbl_id = mcp.create_frame(
            f"Tabel Sholat {MONTH_NAMES_ID[month]}",
            tx,
            20.0,
            tbl_w,
            278.0,
            fill=C_WHITE,
            parent=sec_id,
            stroke=C_CELL_BORDER,
            stroke_weight=0.5,
        )

        # Strip nama bulan
        mcp.create_rect(tbl_id, "Hdr Bulan Sholat", 0, 0, tbl_w, 13, C_EMERALD_MID)
        mcp.create_text(
            tbl_id,
            "Nama Bulan Sholat",
            0,
            2.2,
            tbl_w,
            10,
            f"{MONTH_NAMES_ID[month]} 2027",
            7.0,
            C_WHITE,
            weight=700,
            align="CENTER",
        )

        # Header kolom waktu sholat
        mcp.create_rect(tbl_id, "Hdr Kolom Sholat", 0, 13, tbl_w, 12, C_EMERALD_PALE)
        for cx, cw, htxt in zip(col_xs, col_ws, headers):
            mcp.create_text(
                tbl_id,
                f"Kol {htxt}",
                cx,
                15,
                cw,
                9,
                htxt,
                5.8,
                C_EMERALD_DARK,
                weight=700,
                align="CENTER",
            )

        # Baris harian 1..num_days
        days_in_month = calendar.monthrange(2027, month)[1]
        row_h = 8.15
        for day in range(1, days_in_month + 1):
            d = dt.date(2027, month, day)
            ry = 25.0 + (day - 1) * row_h
            pt = prayer_times_yogya(d)
            holiday = HOLIDAYS_2027.get(d)
            is_sunday = d.weekday() == 6
            is_friday = d.weekday() == 4

            if is_sunday or (holiday and holiday[0] == "libur"):
                rbg = C_RED_SOFT
                tgl_color = C_RED
            elif is_friday:
                rbg = C_ROW_FRI
                tgl_color = C_EMERALD_DARK
            elif day % 2 == 0:
                rbg = C_ROW_ALT
                tgl_color = C_TEXT
            else:
                rbg = C_WHITE
                tgl_color = C_TEXT

            if rbg != C_WHITE:
                mcp.create_rect(tbl_id, f"Row {day}", 0, ry, tbl_w, row_h, rbg)

            vals = (
                str(day),
                pt["subuh"],
                pt["dzuhur"],
                pt["ashar"],
                pt["maghrib"],
                pt["isya"],
            )
            for c_i, (cx, cw, val) in enumerate(zip(col_xs, col_ws, vals)):
                mcp.create_text(
                    tbl_id,
                    f"R{day}C{c_i}",
                    cx,
                    ry + 0.8,
                    cw,
                    row_h,
                    val,
                    5.7,
                    tgl_color if c_i == 0 else C_TEXT,
                    weight=700 if c_i == 0 else 400,
                    align="CENTER",
                )


def build_sheet(
    mcp: McpClient,
    sheet_num: int,
    months: list[int],
    x_offset: float,
    hj_map: dict[dt.date, dict],
) -> int:
    period_label = f"{MONTH_NAMES_ID[months[0]]} - {MONTH_NAMES_ID[months[-1]]} 2027"
    sheet_id = mcp.create_frame(
        f"Lembar {sheet_num} ({period_label})",
        x_offset,
        0.0,
        PAGE_W,
        PAGE_H,
        fill=C_WHITE,
    )

    # 1. Bagian Atas: Banner Yayasan + Placeholder Foto
    build_hero_section(mcp, sheet_id, sheet_num, months)

    # 2. Bagian Tengah: Kalender 4 Bulan (2 x 2)
    positions = [
        (MARGIN_X, 296.0),
        (MARGIN_X + 408.0, 296.0),
        (MARGIN_X, 582.0),
        (MARGIN_X + 408.0, 582.0),
    ]
    for m, (mx, my) in zip(months, positions):
        build_month_card(mcp, sheet_id, m, mx, my, hj_map)

    # 3. Bagian Bawah: Jadwal Sholat 4 Bulan (di bawah kalender)
    build_prayer_section(mcp, sheet_id, sheet_num, months)

    # 4. Catatan Footer paling bawah
    mcp.create_text(
        sheet_id,
        f"Footer Catatan {sheet_num}",
        MARGIN_X,
        1167.0,
        CONTENT_W,
        12.0,
        "Yayasan Baitul Qowwam • Jl. [Alamat Yayasan], D.I. Yogyakarta • Telp/WA: [08xx-xxxx-xxxx]  |  Catatan: Awal Ramadan, Idulfitri & Iduladha mengikuti Sidang Isbat Kemenag RI.",
        6.2,
        C_MUTED,
        weight=500,
        align="CENTER",
    )

    return sheet_id


def main() -> None:
    if not FIGCRAFT_CLI.exists():
        print(f"figcraft-cli not found at {FIGCRAFT_CLI}", file=sys.stderr)
        sys.exit(1)

    hj_map = build_hijri_jawa_map()
    mcp = McpClient()
    try:
        s1 = build_sheet(mcp, 1, [1, 2, 3, 4], 0.0, hj_map)
        s2 = build_sheet(mcp, 2, [5, 6, 7, 8], 900.0, hj_map)
        s3 = build_sheet(mcp, 3, [9, 10, 11, 12], 1800.0, hj_map)

        figcraft_path = ROOT_DIR / "kalender-baitul-qowwam-2027.figcraft"
        pdf_path = ROOT_DIR / "kalender-baitul-qowwam-2027.pdf"

        mcp.call("save_file", {"path": str(figcraft_path)})
        print(f"Saved: {figcraft_path}")

        mcp.call("export", {"ids": [s1, s2, s3], "format": "pdf", "path": str(pdf_path)})
        print(f"Exported PDF: {pdf_path}")

        for idx, sid in enumerate((s1, s2, s3), start=1):
            png_path = ROOT_DIR / f"lembar-{idx}.png"
            mcp.call("export", {"ids": [sid], "format": "png", "scale": 1.5, "path": str(png_path)})
            print(f"Exported PNG: {png_path}")
    finally:
        mcp.close()


if __name__ == "__main__":
    main()
