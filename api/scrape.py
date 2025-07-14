# /api/scrape.py
import asyncio
import json
import sys
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import importlib
import inspect

# Tambahkan root proyek ke path agar bisa impor 'core' dan 'service'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.base import BaseScraperService
from core.browser_manager import init_browser, close_browser

# Muat semua service saat fungsi pertama kali di-load
SERVICES = {}
def load_services():
    if SERVICES: return
    service_folder = os.path.join(project_root, "service")
    for filename in os.listdir(service_folder):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"service.{module_name}")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseScraperService) and obj is not BaseScraperService:
                        SERVICES[module_name.lower()] = obj()
                        break
            except ImportError:
                pass
load_services()


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function Handler"""

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        service_name = query_components.get('service', [None])[0]
        target_url = query_components.get('url', [None])[0]

        if not service_name or not target_url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Parameter 'service' dan 'url' wajib diisi."}).encode('utf-8'))
            return

        service_instance = SERVICES.get(service_name.lower())
        if not service_instance:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Service '{service_name}' tidak ditemukan."}).encode('utf-8'))
            return

        # Jalankan proses scraping secara sinkron di dalam loop asyncio baru
        try:
            result = asyncio.run(self.run_scrape(service_instance, target_url))
            status_code = 200 if result.get("success") else 404
            
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal Server Error", "details": str(e)}).encode('utf-8'))

    async def run_scrape(self, service_instance, target_url):
        """Wrapper async untuk menjalankan scraping"""
        try:
            await init_browser()
            result = await service_instance.get_stream(target_url)
        finally:
            await close_browser()
        return result
