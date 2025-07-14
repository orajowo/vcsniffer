#!/bin/bash

# 1. Instal semua dependensi Python dari requirements.txt
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 2. Jalankan perintah instalasi Playwright secara manual
#    Perintah ini akan men-download browser Chromium beserta dependensi sistem yang diperlukan.
echo "Installing Playwright browsers..."
playwright install --with-deps chromium

echo "Build script finished successfully."
