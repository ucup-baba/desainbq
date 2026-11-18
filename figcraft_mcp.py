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
        # Protokolnya newline-delimited: pesan WAJIB satu baris, tanpa newline
        # di dalamnya, atau frame-nya pecah dan perintah tidak pernah sampai.
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
