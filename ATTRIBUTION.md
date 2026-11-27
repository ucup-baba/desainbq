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

Berkas lisensi OFL ikut diunduh ke folder yang sama dengan font-nya.

## Foto & Ilustrasi Sketsa

- Ilustrasi sketsa cat air & tinta berlatar transparan di `assets/foto/*.png`
  serta ornamen latar pojok kanan bawah di `assets/latar/pojok_kanan_bawah.png`
  dibuat khusus (original AI-generated & diproses alpha transparan dengan
  `scripts/proses_sketsa.py`) untuk Yayasan Islam Baitul Qowwam, tanpa mengambil
  aset pihak ketiga.
- Slot `assets/foto/` tetap dapat diganti kapan saja dengan foto dokumentasi
  kegiatan resmi Yayasan Islam Baitul Qowwam (`.jpg`/`.jpeg` atau `.png`).

## Catatan

**Gaya Plus Jakarta Sans.** Berkas dari Google Fonts adalah font variabel
(`PlusJakartaSans[wght].ttf`), dan sempat diragukan apakah FigCraft bisa
memakai beratnya lewat `fontStyle`. Sudah diuji pada 18 November 2026 dengan
membuat layer teks lalu memeriksa hasilnya:

| Diminta | Yang terpasang |
|---|---|
| `fontFamily: "Plus Jakarta Sans"` | Plus Jakarta Sans / Regular |
| `fontStyle: "SemiBold"` | Plus Jakarta Sans / SemiBold |
| `fontStyle: "Bold"` | Plus Jakarta Sans / Bold |

`file.fontReport` melaporkan ketiga keluarga `available: true` dengan
`missing: 0`. Jadi berat diatur langsung lewat `fontStyle`, dan
`text.setVariations` tidak diperlukan.

**Cara memeriksa ulang.** `file.fontReport` hanya melaporkan font yang
*dipakai oleh layer teks* dalam dokumen. Pada dokumen kosong hasilnya selalu
kosong, dan itu bukan tanda font hilang. Untuk memeriksa, buat dulu layer teks
dengan font yang ditanya, baru jalankan laporannya.
