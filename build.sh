#!/bin/bash
echo "Installing Playwright OS dependencies..."
# [FIX] Jalankan perintah yang direkomendasikan oleh Playwright untuk menginstal dependensi OS
python3 -m playwright install-deps
echo "Installing Playwright browsers using specific python version..."

# [FIX] Gunakan python3.11 secara eksplisit untuk menjalankan modul playwright.
# Pastikan versi ini (3.11) sama dengan yang Anda atur di dasbor Vercel.
python3 -m playwright install chromium

echo "Build script finished."
