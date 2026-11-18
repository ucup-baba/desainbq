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


def test_baris_bukan_json_dilewati():
    # Server menulis baris informasi sebelum balasan JSON-RPC.
    k = klien_dengan([{"id": 2, "result": {"isError": False,
                                           "content": [{"type": "text", "text": "{}"}]}}])
    k.proc._balasan.insert(0, "figcraft MCP server on stdio")
    assert k.panggil("undo", {}) == {}
