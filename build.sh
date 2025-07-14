#!/bin/bash

echo "Installing Playwright browsers using specific python version..."

# [FIX] Gunakan python3.11 secara eksplisit untuk menjalankan modul playwright.
# Pastikan versi ini (3.11) sama dengan yang Anda atur di dasbor Vercel.
python3.11 -m playwright install --with-deps chromium

echo "Build script finished."
