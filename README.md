# Prediksi Penumpang Pesawat dengan Holt-Winters dan Moving Average

Aplikasi berbasis web ini dibuat menggunakan kerangka kerja (framework) **Flask Python** untuk memprediksi jumlah penumpang domestik maupun internasional pada beberapa bandara utama di Indonesia. Pemodelan prediksi menggunakan dua metode perbandingan, yaitu **Holt-Winters Exponential Smoothing** dan **Moving Average (MA)**.

Repositori ini merupakan kelengkapan dari program skripsi, yang mencakup kode sumber (source code), manual pemakaian, serta instruksi instalasi agar program siap digunakan.

---

## 📂 Struktur Repositori

- `app.py`: *Source code* utama (listing program) yang menjalankan server Flask dan menampung seluruh logika prediksi.
- `requirements.txt`: Daftar dependensi atau *library* Python yang dibutuhkan untuk menjalankan program.
- `Jalankan_Aplikasi.bat`: *Script* siap pakai untuk menjalankan program di Windows dengan satu kali klik.
- `Manual_Book.pdf`: Manual pemakaian program lengkap beserta panduan antarmuka (UI).
- `templates/` & `static/`: Folder yang berisi rancangan antarmuka web (HTML, CSS, JS).
- `Dataset/`: Folder berisi dataset riwayat jumlah penumpang (format Excel).
- `Notebook_Eksperimen/`: Folder berisi file Jupyter Notebook eksperimen pencarian parameter terbaik.

---

## 🛠️ Cara Instalasi Program

Pastikan Anda sudah menginstal **Python** versi terbaru (disarankan versi 3.9 - 3.11) di komputer/laptop Anda sebelum memulai instalasi.

1. **Clone atau Unduh Repositori**
   Unduh *source code* ini melalui GitHub (klik tombol `Code` -> `Download ZIP`) dan ekstrak folder tersebut di komputer Anda.

2. **Buka Terminal/Command Prompt**
   Buka Command Prompt (CMD) atau Terminal dan arahkan direktori aktif ke dalam folder program yang baru saja diunduh.

3. **Buat Virtual Environment (Opsional tapi disarankan)**
   ```bash
   python -m venv env
   env\Scripts\activate
   ```
   *(Catatan: Jika perintah `python` tidak dikenali di komputer Anda, silakan ganti kata `python` dengan `py`)*

4. **Instal Library yang Dibutuhkan**
   Jalankan perintah berikut untuk menginstal semua *library* pendukung:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## 🚀 Cara Membuka / Menjalankan Program (Siap Digunakan)

Setelah instalasi berhasil dilakukan, Anda dapat menjalankan program dengan 2 cara:

### Cara 1: Menggunakan Script Cepat (Khusus Windows)
Cukup klik ganda (*double click*) pada file **`Jalankan_Aplikasi.bat`**. 
Script tersebut akan otomatis mendeteksi konfigurasi Python di komputer Anda, membuka *server* Flask, dan meluncurkan aplikasi di browser.

### Cara 2: Menjalankan Manual via Terminal
1. Buka CMD / Terminal di dalam folder program.
2. Jalankan perintah berikut:
   ```bash
   python app.py
   ```
3. Akan muncul alamat IP lokal (biasanya `http://127.0.0.1:5000`). Buka alamat tersebut di *browser* (Google Chrome / Mozilla Firefox).

---

## 📖 Manual Pemakaian Program

Untuk panduan penggunaan program secara menyeluruh—mulai dari cara mengunggah data, memasukkan parameter, hingga membaca grafik evaluasi—silakan merujuk (baca) ke dalam dokumen **`Manual_Book.pdf`** yang sudah dilampirkan di repositori ini.
