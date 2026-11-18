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
unduh "caveatbrush/CaveatBrush-Regular.ttf"           "CaveatBrush-Regular.ttf"
unduh "patrickhand/PatrickHand-Regular.ttf"           "PatrickHand-Regular.ttf"
unduh "plusjakartasans/PlusJakartaSans%5Bwght%5D.ttf" "PlusJakartaSans-Variable.ttf"
unduh "caveatbrush/OFL.txt"                           "OFL-CaveatBrush.txt"
unduh "patrickhand/OFL.txt"                           "OFL-PatrickHand.txt"
unduh "plusjakartasans/OFL.txt"                       "OFL-PlusJakartaSans.txt"

fc-cache -f "$TUJUAN" >/dev/null
echo "Selesai. Font terdaftar:"
fc-list : family | grep -iE "caveat brush|patrick hand|plus jakarta" | sort -u
