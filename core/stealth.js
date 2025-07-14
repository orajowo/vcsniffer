// core/stealth.js (Versi Lengkap)

// Skrip ini dirancang untuk menyamarkan berbagai tanda dan fingerprint
// yang digunakan oleh sistem deteksi bot untuk mengidentifikasi Playwright.

(() => {
    // 1. Menghilangkan properti "navigator.webdriver"
    if (navigator.webdriver) {
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
    }

    // 2. Memalsukan izin notifikasi
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters)
    );

    // 3. Memalsukan plugin browser
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format', length: 1, MimeTypes: [{ type: 'application/pdf', suffixes: 'pdf', description: '' }] },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '', length: 1, MimeTypes: [{ type: 'application/pdf', suffixes: 'pdf', description: '' }] },
            { name: 'Native Client', filename: 'internal-native-client', description: '', length: 2, MimeTypes: [{ type: 'application/x-nacl', suffixes: '', description: '' }, { type: 'application/x-pnacl', suffixes: '', description: '' }] },
        ],
    });

    // 4. Memalsukan properti bahasa
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en', 'id-ID', 'id'],
    });

    // 5. Menambahkan properti yang hilang di browser non-Chrome
    if (!window.chrome) {
        window.chrome = { runtime: {} };
    }

    // 6. Memalsukan properti WebGL
    try {
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                return 'NVIDIA GeForce GTX 1080 Ti OpenGL Engine'; // Kartu grafis umum
            }
            if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                return 'NVIDIA Corporation';
            }
            return getParameter.apply(this, arguments);
        };
    } catch (e) {
        // Abaikan
    }

    // 7. [BARU] Melawan Canvas Fingerprinting
    // Teknik ini menambahkan "noise" acak yang sangat kecil pada gambar canvas
    // sehingga hash fingerprint yang dihasilkan akan selalu berbeda.
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {
        try {
            const context = this.getContext('2d');
            if (context) {
                // Tambahkan noise random ke pixel data
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    const noise = Math.floor(Math.random() * 3) - 1; // -1, 0, or 1
                    imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + noise));
                    imageData.data[i + 1] = Math.max(0, Math.min(255, imageData.data[i + 1] + noise));
                }
                context.putImageData(imageData, 0, 0);
            }
        } catch(e) {
            // Abaikan jika ada error
        }
        return originalToDataURL.apply(this, arguments);
    };

    // 8. [BARU] Melawan Audio Fingerprinting
    // Sama seperti canvas, kita menambahkan noise pada data audio yang dihasilkan.
    const audioContext = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (audioContext) {
        const originalStartRendering = audioContext.prototype.startRendering;
        audioContext.prototype.startRendering = function() {
            return originalStartRendering.apply(this, arguments).then(buffer => {
                try {
                    for (let i = 0; i < buffer.numberOfChannels; i++) {
                        const channelData = buffer.getChannelData(i);
                        for (let j = 0; j < channelData.length; j++) {
                            // Tambahkan noise yang sangat kecil
                            channelData[j] += (Math.random() - 0.5) * 0.0000001;
                        }
                    }
                } catch(e) {
                    // Abaikan
                }
                return buffer;
            });
        };
    }

    // 9. [BARU] Menyamarkan Properti Perangkat Keras
    // Memberikan nilai yang umum untuk jumlah core CPU dan memori.
    if ('hardwareConcurrency' in navigator && navigator.hardwareConcurrency > 0) {
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8, // Nilai umum untuk desktop
        });
    }
    if ('deviceMemory' in navigator && navigator.deviceMemory > 0) {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8, // Nilai umum untuk desktop
        });
    }

    // --- [LOGIKA BARU & LEBIH KUAT] ---
    // 10. Secara Proaktif Menghapus Atribut 'sandbox' pada Iframe

    // Fungsi untuk menghapus sandbox dari sebuah iframe
    const removeSandbox = (iframe) => {
        if (iframe && iframe.hasAttribute('sandbox')) {
            iframe.removeAttribute('sandbox');
        }
    };

    // Buat "mata-mata" (MutationObserver)
    const observer = new MutationObserver((mutations) => {
        // Loop setiap mutasi/perubahan yang terdeteksi
        for (const mutation of mutations) {
            // Loop setiap elemen baru yang ditambahkan ke halaman
            for (const node of mutation.addedNodes) {
                // Jika elemen baru itu sendiri adalah iframe
                if (node.tagName === 'IFRAME') {
                    removeSandbox(node);
                }
                // Jika elemen baru mengandung iframe di dalamnya
                else if (node.querySelectorAll) {
                    const iframes = node.querySelectorAll('iframe[sandbox]');
                    iframes.forEach(removeSandbox);
                }
            }
        }
    });

    // Jalankan observer saat dokumen sudah siap
    // Ini akan mengawasi seluruh halaman untuk setiap elemen baru yang ditambahkan
    if (document.documentElement) {
         observer.observe(document.documentElement, {
            childList: true,
            subtree: true,
        });
    } else {
         // Fallback jika dokumen belum siap, jalankan saat sudah siap
         document.addEventListener('DOMContentLoaded', () => {
             observer.observe(document.documentElement, {
                childList: true,
                subtree: true,
            });
         });
    }
    
    // Sebagai tambahan, jalankan satu kali untuk membersihkan iframe yang mungkin sudah ada
    // saat skrip ini pertama kali dieksekusi.
    const initialIframes = document.querySelectorAll('iframe[sandbox]');
    initialIframes.forEach(removeSandbox);
})();