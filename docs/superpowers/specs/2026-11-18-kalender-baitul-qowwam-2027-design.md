# Kalender Dinding 2027 — Yayasan Islam Baitul Qowwam

Desain, 18 November 2026. Arah visual: **A — Risograph editorial**.

## 1. Tujuan

Kalender dinding 2027 untuk Yayasan Islam Baitul Qowwam (D.I. Yogyakarta): 3 lembar, tiap lembar 4
bulan, memuat tanggal Masehi, Hijriah dan Jawa, ditambah jadwal waktu sholat WIB untuk wilayah DIY.
Hasil akhir siap serah ke percetakan, dan file sumbernya bisa dibuka serta disunting sendiri oleh
pengurus yayasan.

Versi sebelumnya (`generate_kalender.py` + `build_via_figcraft_mcp.py`) sudah benar secara data
tetapi lemah secara visual: semua elemen dibungkus kotak rounded bertumpuk bayangan, foto dipaksa
jadi heksagon, empat bulan tampil sebagai empat kartu identik tanpa hierarki, dan jadwal sholat
disajikan 31 baris per bulan sehingga memadati lembar. Dokumen ini merombak lapisan visualnya dan
mempertahankan lapisan datanya.

## 2. Keputusan yang sudah terkunci

| Hal | Keputusan |
|---|---|
| Ukuran | A2, 420 × 594 mm, portrait |
| Jumlah lembar | 3 (Jan–Apr, Mei–Agu, Sep–Des) |
| Sistem penanggalan | Masehi + Hijriah + Jawa (hari pasaran) |
| Jadwal sholat | WIB, Kota Yogyakarta sebagai acuan, rentang per 5 hari |
| Foto | Foto asli yayasan, disediakan pemilik, dipasang ke slot |
| Logo & kontak | Slot disiapkan, isi menyusul |
| Toolchain | Python → FigCraft MCP (attached) → `.figcraft` + PDF + PNG |
| Palet | Palet yayasan (7 warna, pasal 5) |

## 3. Geometri halaman

Semua ukuran dalam milimeter; 1 unit FigCraft = 1 mm pada spesifikasi ini.

- Ukuran jadi: 420 × 594 (A2 portrait)
- Bleed: 3 mm di keempat sisi, dengan bleed marks (ekspor PDF)
- Margin aman: 14 mm
- Lebar area kerja: 392 mm
- Kolom: 12 kolom, gutter 6 mm, lebar kolom 27,17 mm

Anggaran vertikal per lembar (dari margin atas):

| Blok | Tinggi |
|---|---|
| Header (identitas + foto) | 129 |
| Jeda | 10 |
| Grid 4 bulan (2 × 142,4 + gutter 9) | 293,8 |
| Jeda | 12 |
| Pita jadwal sholat | ±70 |
| Kaki halaman | 10 |
| **Terpakai** | **±525** |
| Sisa ruang nafas | ±41 |

Sisa 41 mm dibagikan sebagai ruang kosong di antara blok, bukan dipadatkan. Pada kalender dinding,
ruang kosong adalah yang membuatnya terbaca dari jarak 2 meter.

## 4. Sistem tipografi

Dua keluarga font, dengan pembagian tugas yang tegas.

| Peran | Font | Lisensi | Ukuran |
|---|---|---|---|
| Angka tahun | Caveat Brush | OFL-1.1 | 52 mm, rotasi −2,5° |
| Nama bulan | Caveat Brush | OFL-1.1 | 11 mm |
| Nama yayasan | Patrick Hand | OFL-1.1 | 9,4 mm |
| Angka tanggal | Plus Jakarta Sans 600 | OFL-1.1 | 8,4 mm |
| Nama hari | Plus Jakarta Sans 700 | OFL-1.1 | 3 mm, tracking 0,5 |
| Hijriah & Jawa | Plus Jakarta Sans 400/600 | OFL-1.1 | 2,9 mm |
| Jadwal sholat | Plus Jakarta Sans 400/700 | OFL-1.1 | 3,3 mm |
| Keterangan libur | Plus Jakarta Sans 400 | OFL-1.1 | 2,9 mm |

**Aturan yang tidak boleh dilanggar:** font tulisan tangan hanya untuk display — angka tahun, nama
bulan, nama yayasan, judul bagian. Seluruh data (tanggal, Hijriah, Jawa, jam sholat) memakai
Plus Jakarta Sans. Tulisan tangan pada data berukuran kecil adalah penyebab utama kalender terlihat
murah, dan pada A2 yang dibaca dari jauh itu merusak keterbacaan.

Plus Jakarta Sans dipilih karena dirancang oleh Tokotype (Jakarta) dan angkanya tegas pada ukuran
kecil. Caveat Brush dipilih karena goresannya tebal sehingga tetap kuat saat dicetak besar.

## 5. Peran warna

Palet yayasan, satu peran per warna. Tidak ada gradien dan tidak ada bayangan di mana pun.

| Hex | Nama | Peran |
|---|---|---|
| `#024959` | ink | Teks utama, garis hairline, angka tanggal |
| `#038C8C` | teal | Label sekunder, nama hari, Hijriah/Jawa, judul |
| `#6EC4C0` | mint | Bidang foto, raster tipis |
| `#F2EEED` | paper | Latar lembar |
| `#F9D83F` | sun | Penanda hari libur, kolom Maghrib |
| `#F29F05` | amber | Aksen: dua digit "27", nomor bulan |
| `#A64F03` | rust | Hari Minggu dan tanggal merah |

**Catatan penting:** palet ini tidak memuat merah. Kalender Indonesia menandai Minggu dan hari libur
dengan merah, dan peran itu di sini diambil `#A64F03` (oranye bata). Keputusan ini disengaja, bukan
kelalaian. Kalau pemilik menghendaki merah sungguhan, itu warna kedelapan di luar palet dan harus
diputuskan tersendiri.

Latar memakai `#F2EEED`, bukan putih. Kertas krem membuat teal terbaca sebagai tinta cetak dan
langsung menjauhkan kesan "render layar".

## 6. Anatomi blok bulan

Empat blok dalam grid 2 × 2, masing-masing 191,5 mm lebar dan 142,4 mm tinggi.

```
┌──────────────────────────────────────────────┐
│ 01  JANUARI            Rajab – Sya'ban 1448  │  kepala, garis bawah 0,7 mm
│                        Rejeb – Ruwah 1960    │
├──────────────────────────────────────────────┤
│ MIN  SEN  SEL  RAB  KAM  JUM  SAB            │  nama hari, teal, MIN rust
├──────────────────────────────────────────────┤
│                              1 ²³            │  tanggal 8,4 mm
│                            22 Pon            │  Jawa + pasaran 2,9 mm
│  3 ²⁴   4 ²⁵   5 ²⁶  ...                     │  6 baris × 18,4 mm
├──────────────────────────────────────────────┤
│ 1 — Tahun Baru 2027 · 5 — Isra Mikraj 1448 H │  keterangan libur
└──────────────────────────────────────────────┘
```

- Hijriah sebagai angka superskrip di pojok kanan atas sel; nama bulan Hijriah tidak diulang per
  sel, cukup di kepala blok sebagai rentang.
- Jawa sebagai "tanggal + pasaran" di bawah angka Masehi.
- Tidak ada kotak mengelilingi blok. Pemisah hanya hairline: 0,7 mm di bawah kepala, 0,35 mm antar
  baris dengan opasitas rendah.
- Sel hari libur diberi alas `#F9D83F` opasitas 42%, dan angkanya memakai rust.
- Sel di luar bulan berjalan: angka diredam ke opasitas 20%, Hijriah dan Jawa disembunyikan.

## 7. Pita jadwal sholat

Satu pita selebar area kerja di bawah grid bulan, empat kolom (satu per bulan).

- Rentang per 5 hari: 1–5, 6–10, 11–15, 16–20, 21–25, 26–akhir bulan. Enam baris per bulan.
- Kolom: rentang tanggal, Subuh, Dzuhur, Ashar, Maghrib, Isya.
- Kolom Maghrib diberi alas `#F9D83F` opasitas 45% karena paling sering dicari (buka puasa).
- **Aturan pembulatan:** tiap sel memuat waktu **paling akhir** dalam rentangnya. Dengan begitu
  tidak mungkin seseorang sholat atau berbuka sebelum waktunya masuk. Selisih dalam satu rentang
  paling besar sekitar 2 menit.
- Perhitungan: metode Kemenag RI, sudut Subuh 20°, Isya 18°, ihtiyati +2 menit, acuan Kota
  Yogyakarta (−7,7956; 110,3695; UTC+7).
- Di bawah pita dicantumkan koreksi wilayah: Yogya/Sleman/Bantul ±0 menit, Kulon Progo +1,
  Gunungkidul −1.

## 8. Slot foto

Per lembar: 1 foto utama dan 3 foto pendukung; total 12 slot untuk 3 lembar.

| Slot | Ukuran tempat | Resolusi minimum @300dpi |
|---|---|---|
| Foto utama | 244 × 84 mm | 2882 × 992 px |
| Foto pendukung (3×) | 78 × 40 mm | 921 × 472 px |

- Tiap slot adalah layer berisi bidang warna (mint/sun/amber bergantian) dengan garis tepi ink
  0,7 mm. Foto dipasang ke layer itu lewat `image.place` dengan `target` dan `mode: "fill"`, jadi
  foto mengisi bingkai tanpa mengubah tata letak.
- Mengganti foto nanti cukup dengan `image.replace`, yang mempertahankan bingkai, crop dan posisi.
- Selama foto belum ada, slot tetap tampil sebagai bidang warna berlabel, bukan kotak abu-abu
  bertuliskan "placeholder". Lembar harus tetap layak dilihat dalam keadaan kosong.

## 9. Pipeline data

`generate_kalender.py` yang ada dipertahankan sebagai sumber data dan dipakai ulang; tidak ditulis
ulang. Yang dipakai:

- `build_hijri_jawa_map()` — peta tanggal → Hijriah, Jawa, pasaran, untuk seluruh 2027.
- `prayer_times_yogya(date)` — waktu sholat harian.
- `HOLIDAYS_2027` — hari libur nasional dan cuti bersama menurut SKB 3 Menteri.

Yang ditambahkan:

- `prayer_ranges(year, month)` — meringkas waktu harian menjadi rentang 5 hari dengan aturan
  "ambil waktu paling akhir" dari pasal 7.

Modul render lama (`render_month_html`, `render_sheet_html`, `generate_html`) tidak dipakai lagi
oleh pipeline baru. Modul itu dihapus agar tidak ada dua sumber kebenaran untuk tata letak.

## 10. Pipeline build

`build_kalender.py` menggantikan `build_via_figcraft_mcp.py`, menyusun dokumen lewat FigCraft MCP
pada server yang berjalan dalam mode attached.

Urutan:

1. Buat dokumen baru, 3 halaman A2, latar `#F2EEED`.
2. Per halaman: bangun header, empat blok bulan, pita sholat, kaki halaman — seluruhnya sebagai
   layer bernama agar mudah ditemukan saat disunting manual.
3. Pasang foto apabila berkas tersedia di `assets/foto/`; jika tidak, slot dibiarkan sebagai bidang
   warna berlabel.
4. Simpan `.figcraft` lewat `save_file`.
5. Ekspor:
   - `kalender-2027-cetak.pdf` — `cmyk: true`, `bleed: "3mm"`, `bleedMarks: true` (untuk percetakan)
   - `kalender-2027-layar.pdf` — RGB tanpa bleed (untuk dibagikan/diperiksa)
   - `lembar-{1,2,3}.png` — `scale` secukupnya untuk pratinjau

Elemen berulang (sel tanggal, baris jadwal sholat, slot foto) dibuat sebagai komponen FigCraft,
bukan layer duplikat, supaya perubahan gaya cukup dilakukan sekali di komponen induk.

## 11. Aset dan lisensi

- Ketiga font (Caveat Brush, Patrick Hand, Plus Jakarta Sans) berlisensi OFL-1.1 dan diambil dari
  Google Fonts. Belum terpasang di mesin ini (`fc-list` tidak menemukannya), jadi dipasang ke
  `~/.fonts` agar FigCraft dapat membacanya saat runtime. Font tidak ikut dimasukkan ke dalam repo.
- Setiap aset dicatat di `ATTRIBUTION.md` milik proyek kalender: berkas, pembuat, sumber, lisensi.
- Foto yayasan adalah milik yayasan; dicatat sebagai "milik Yayasan Islam Baitul Qowwam, izin
  pemilik". Tidak ada foto stok, tidak ada ikon atau ilustrasi dari produk pihak lain.

## 12. Verifikasi

Sebuah lembar dianggap selesai apabila:

1. **Benar secara data.** Uji otomatis membandingkan tanggal Masehi/Hijriah/Jawa dan waktu sholat
   hasil render terhadap `generate_kalender.py`, untuk seluruh 365 hari. Satu hari meleset = gagal.
2. **Aturan rentang terjaga.** Uji memastikan tiap sel rentang berisi waktu maksimum pada
   rentangnya, bukan rata-rata atau waktu hari pertama.
3. **Terlihat benar.** Tiap lembar diekspor PNG dan dilihat; dicek luberan teks, tumpang tindih,
   dan sel yang kosong tidak pada tempatnya.
4. **Siap cetak.** PDF cetak dibuka dan diperiksa: ukuran halaman 426 × 600 mm (termasuk bleed),
   ruang warna CMYK, bleed marks ada.

## 13. Batasan yang diketahui

- **Hijriah bersifat prediksi.** Awal Ramadan, Idulfitri dan Iduladha ditentukan Sidang Isbat
  Kemenag RI dan bisa bergeser satu hari dari tabel mana pun. Keterangan ini dicetak di kaki
  halaman, bukan disembunyikan.
- **Waktu sholat adalah hasil hitungan**, bukan salinan dari jadwal resmi Kemenag. Selisih satu
  menit terhadap jadwal masjid setempat adalah wajar. Ihtiyati +2 menit sudah diperhitungkan.
- **Ringkasan per 5 hari menghilangkan detail harian** hingga sekitar 2 menit. Ini pertukaran yang
  dipilih secara sadar demi keterbacaan.
- **Konversi CMYK oleh FigCraft belum pernah diuji pada proyek ini.** Sebelum cetak massal, minta
  proof cetak ke percetakan. Warna teal pekat adalah yang paling rawan bergeser.

## 14. Di luar ruang lingkup

- Penjadwalan ulang otomatis setelah Sidang Isbat.
- Versi digital interaktif atau ekspor `.ics`.
- Kalender untuk tahun selain 2027.
- Lokasi di luar DIY (hanya koreksi menit yang dicantumkan, bukan perhitungan terpisah).

## 15. Lokasi proyek

Folder ini saat ini berada di dalam repositori FigCraft dan belum ter-commit. Aturan repositori itu
melarang penambahan materi yang tidak berhubungan, jadi proyek kalender ini **diusulkan** dipindah
ke `~/project/artCraft/kalender-baitul-qowwam-2027` sebagai repositori git tersendiri. Pemindahan
menunggu persetujuan pemilik dan belum dilakukan. Direktori kerja companion (`.superpowers/`)
dimasukkan ke `.gitignore`.
