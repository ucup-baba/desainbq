# Kalender Dinding 2027 — Yayasan Islam Baitul Qowwam

Tiga lembar A2 (42 × 59,4 cm), empat bulan per lembar, memuat tanggal Masehi,
Hijriah dan Jawa, serta jadwal sholat WIB untuk D.I. Yogyakarta.

## Menyiapkan

```bash
./scripts/pasang_font.sh
```

Sekali saja. Mengunduh Caveat Brush, Patrick Hand dan Plus Jakarta Sans
(ketiganya OFL-1.1) ke `~/.fonts`. Font tidak ikut repo.

## Membangun

Hidupkan app FigCraft lebih dulu:

```bash
FIGCRAFT=~/project/artCraft/FIGCRAFT/target/release/figcraft
setsid nohup "$FIGCRAFT" --control 40695 --automation-read-root "$PWD" --automation-write-root "$PWD/dist" > .figcraft-app.log 2>&1 &
```

Lalu bangun:

```bash
python3 build_kalender.py
```

Satu lembar saja:

```bash
python3 build_kalender.py --lembar 1
```

**Penting:** app harus bermula dari dokumen kosong. Build menambah halaman ke
dokumen yang sedang terbuka, jadi untuk membangun ulang dari nol, matikan dan
hidupkan lagi app-nya.

Keluaran di `dist/`:

| Berkas | Untuk |
|---|---|
| `cetak-lembar-{1,2,3}.pdf` | Percetakan: CMYK, 426 × 600 mm |
| `layar-lembar-{1,2,3}.pdf` | Dibagikan dan diperiksa: RGB |
| `lembar-{1,2,3}.png` | Pratinjau cepat |
| `kalender-baitul-qowwam-2027.figcraft` | Berkas sumber, bisa disunting di FigCraft |

Tiap lembar menjadi berkasnya sendiri karena `export` di FigCraft selalu
mengambil halaman yang sedang aktif; tidak ada ekspor banyak halaman sekaligus.

## Ukuran cetak dan bleed

PDF cetak berukuran **426 × 600 mm**, yaitu A2 (420 × 594 mm) ditambah bleed
3 mm di keempat sisi. **Potong 3 mm dari tiap tepi** untuk mendapat ukuran
jadi. Warna kertas sudah menutupi area bleed, jadi tidak akan ada garis putih
kalau pemotongan sedikit meleset.

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

Uji paritas membandingkan seluruh 365 hari terhadap `generate_kalender.py`,
dan memastikan tiap sel jadwal sholat tidak pernah lebih awal dari hari mana
pun dalam rentangnya.

## Susunan berkas

| Berkas | Isi |
|---|---|
| `generate_kalender.py` | Sumber data: Hijriah, Jawa, pasaran, hari libur, hitungan waktu sholat |
| `kalender_data.py` | Model lembar/bulan/hari + peringkas sholat per 5 hari |
| `tema.py` | Geometri, palet, peran font |
| `blok_bulan.py`, `pita_sholat.py`, `header.py` | Penghasil perintah tata letak (fungsi murni) |
| `figcraft_mcp.py` | Klien MCP attached |
| `build_kalender.py` | Orkestrator: bangun, simpan, ekspor |

Modul tata letak tidak menyentuh jaringan: mereka menghasilkan daftar perintah,
sehingga tata letaknya bisa diuji tanpa menjalankan app.

## Yang perlu diketahui sebelum cetak

- Tanggal Hijriah di sini adalah **hitungan**, bukan ketetapan. Awal Ramadan,
  Idulfitri dan Iduladha ditentukan Sidang Isbat Kemenag RI dan bisa bergeser
  satu hari.
- Waktu sholat dihitung dengan metode Kemenag RI (Subuh 20°, Isya 18°,
  ihtiyati +2 menit) untuk Kota Yogyakarta. Tiap sel memuat waktu **paling
  akhir** dalam rentang 5 harinya, supaya tidak mungkin sholat atau berbuka
  sebelum waktunya masuk. Selisih dalam satu rentang paling besar ~2 menit.
- **Minta proof cetak** sebelum cetak massal. Konversi CMYK sudah diverifikasi
  menghasilkan operator warna CMYK murni, tetapi hasil warna di atas kertas
  belum pernah diuji; teal pekat adalah warna yang paling rawan bergeser.
- Alamat dan nomor telepon di kaki halaman masih berupa teks sementara
  (`[alamat]`, `[telp/WA]`), begitu juga logo yayasan yang belum ada.
