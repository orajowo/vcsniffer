#!/bin/bash

# Vercel sudah menjalankan `pip install` secara otomatis sebelum skrip ini,
# jadi kita tidak perlu melakukannya lagi.

# Langsung jalankan instalasi browser Playwright menggunakan modul Python.
# Ini cara yang lebih andal untuk menghindari masalah "command not found".
echo "Installing Playwright browsers..."
python -m playwright install --with-deps chromium

echo "Build script finished."
