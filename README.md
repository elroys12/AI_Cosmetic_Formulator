# 🚀 Novel Chemicals Discovery Agent

Repositori untuk proyek Capstone AC-04 yang mengintegrasikan Front-End (React), Back-End (FastAPI), dan AI/ML (Agentic AI) untuk merekomendasikan formulasi kimia novel berdasarkan kebutuhan pengguna.

---

## 1. Deskripsi Singkat Proyek

Novel Chemicals Discovery Agent adalah sistem berbasis kecerdasan buatan yang dirancang untuk membantu pengguna menemukan dan memformulasikan senyawa kimia yang tepat untuk kebutuhan kosmetik atau farmasi spesifik. Sistem ini menggunakan Agentic AI untuk menganalisis input, melakukan pencarian kontekstual terhadap bahan aktif, dan memverifikasi keamanan (toksisitas, kompatibilitas) sebelum menghasilkan rekomendasi formulasi.

## 2. Petunjuk Setup Environment (Untuk Developer)

Pastikan Anda memiliki **Node.js (v18+)** dan **Python (v3.10+)** terinstal di sistem Anda.

### A. Setup Backend (Python/FastAPI/ML)

1.  **Kloning Repositori:**
    ```bash
    git clone [https://repostuff.com/products/repo-lot-security](https://repostuff.com/products/repo-lot-security)
    cd novel-chemicals-discovery-agent/backend # Asumsi folder backend
    ```

2.  **Buat dan Aktifkan Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Untuk Linux/macOS
    # atau .\venv\Scripts\activate.ps1 (Untuk Windows PowerShell)
    ```

3.  **Instal Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi Environment:**
    * Buat berkas `.env` dari `.env.example`.
    * Isi variabel **`DATABASE_URL`** dan **`SECRET_KEY`**.

### B. Setup Frontend (React/Vite)

1.  **Pindah ke Direktori Frontend:**
    ```bash
    cd ../frontend # Asumsi folder frontend
    ```

2.  **Instal Dependensi:**
    ```bash
    npm install
    ```

3.  **Konfigurasi Environment:**
    * Buat berkas `.env` dari `.env.example`.
    * Pastikan **`VITE_API_URL`** diatur ke URL *backend* lokal Anda (`http://127.0.0.1:8000` atau sesuai port yang digunakan).

---

## 3. Tautan Model ML

Tautan untuk mengunduh (download) dan memuat (load) model Machine Learning yang digunakan:

* **Tautan Model/Dataset:** 

---

## 4. Cara Menjalankan Aplikasi (Instruksi Teknis & Alur Penggunaan)

### A. Menjalankan Server Lokal (Wajib untuk Pengembangan)

1.  **Jalankan Backend (Terminal 1):**
    ```bash
    # Pastikan venv aktif dan berada di folder backend
    uvicorn main:app --reload
    ```
    *Server backend akan berjalan di http://127.0.0.1:8000.*

2.  **Jalankan Frontend (Terminal 2):**
    ```bash
    # Berada di folder frontend
    npm run dev
    ```
    *Aplikasi frontend akan berjalan di http://localhost:5173 (atau port default Vite).*

### B. Alur Penggunaan Sistem (Sudut Pandang Pengguna)

Berikut adalah alur penggunaan sistem dari sudut pandang pengguna:

1.  Pengguna membuka aplikasi melalui *browser* yang menampilkan *frontend* lokal.
2.  Pengguna mengisi *form* input, seperti masalah kulit, tujuan penggunaan produk, dan kebutuhan formulasi.
3.  Sistem menerima input dan memprosesnya menggunakan Agentic AI.
4.  Sistem melakukan pencarian bahan aktif yang relevan berdasarkan konteks input pengguna.
5.  Sistem menganalisis keamanan, kompatibilitas antar bahan, serta batas konsentrasi aman.
6.  Sistem menghasilkan rekomendasi formulasi atau kandidat kandungan baru.
7.  Hasil ditampilkan kepada pengguna berupa formulasi, manfaat, serta rekomendasi pemakaian.
8.  Hasil rekomendasi dapat dilihat kembali melalui fitur *history log*.
9.  Pengguna juga dapat menghapus riwayat hasil rekomendasi sesuai kebutuhan.

---
