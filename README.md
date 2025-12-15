# 🚀 Novel Chemicals Discovery Agent

Repositori untuk proyek Capstone AC-04 yang mengintegrasikan Front-End (React/Vite), Back-End (FastAPI), dan AI/ML (Agentic AI) untuk merekomendasikan formulasi kimia novel berdasarkan kebutuhan pengguna.

---

## 1. Deskripsi Singkat Proyek

**Sistem Cerdas untuk Analisis Keamanan dan Formulasi Skincare**

Novel Chemicals Discovery Agent adalah sistem berbasis kecerdasan buatan yang dirancang untuk membantu pengguna menemukan dan memformulasikan senyawa kimia yang tepat untuk kebutuhan kosmetik atau farmasi spesifik. Sistem ini menggunakan **Agentic AI** (diorkestrasi melalui CrewAI dan Google Gemini) untuk menganalisis input, melakukan pencarian kontekstual terhadap bahan aktif, dan memverifikasi keamanan (toksisitas, kompatibilitas) sebelum menghasilkan rekomendasi formulasi.

Melalui *pipeline* ini, sistem dapat membantu pengguna dalam:

* Menganalisis keamanan dan kelayakan bahan *skincare*.
* Memberikan rekomendasi formulasi secara terstruktur.
* Menjalankan proses analisis secara otomatis dan berurutan.

Proyek ini dikembangkan sebagai bagian dari **capstone project**, dengan fokus pada penerapan AI modern dalam domain kosmetik dan perawatan kulit.

---

## 2. Petunjuk Setup Environment (Untuk Developer)

Pastikan Anda memiliki **Node.js (v18+)** dan **Python (v3.10+)** terinstal di sistem Anda.

### A. Prasyarat Kritis (Wajib)

Proyek ini membutuhkan layanan eksternal berikut yang harus dikonfigurasi di berkas `.env`:

* **API Key Google Generative AI (Gemini)** untuk inferensi Agentic AI.
* Akses ke **Supabase** untuk konfigurasi Database URL (Auth & History Log).

### B. Setup Backend (Python/FastAPI/ML)

1.  **Kloning Repositori:**
    ```bash
    git clone [LINK REPO GITHUB LO]
    cd novel-chemicals-discovery-agent/backend # Pindah ke folder backend
    ```

2.  **Buat dan Aktifkan Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Untuk Linux/macOS
    # atau .\venv\Scripts\activate.ps1 (Untuk Windows PowerShell)
    ```

3.  **Instal Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi Environment Backend:**
    * Buat berkas `.env` dari `.env.example`.
    * Isi variabel krusial:
        ```env
        # Kunci Rahasia
        SECRET_KEY="YOUR_SECRET_KEY"
        # Database Supabase (Wajib untuk Auth dan History Log)
        DATABASE_URL="postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]" 
        # API LLM (Wajib untuk Agentic AI)
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY" 
        ```

### C. Setup Frontend (React/Vite)

1.  **Pindah ke Direktori Frontend:**
    ```bash
    cd ../frontend # Pindah ke folder frontend
    ```

2.  **Instal Dependensi:**
    ```bash
    npm install
    ```

3.  **Konfigurasi Environment Frontend:**
    * Buat berkas `.env.development` (atau `.env.local`).
    * Pastikan **`VITE_API_URL`** diatur ke URL *backend* lokal Anda.
        ```env
        # URL menuju backend FastAPI lokal
        VITE_API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000) 
        ```

---

## 3. Tautan Model ML & Agentic AI

Proyek ini menggunakan kombinasi *pre-trained models* dan *LLM Agent* yang diorkestrasi.

* **Tautan Model:** [https://colab.research.google.com/drive/1E1GejUDfO0JPaoGP4viRDwNLnuvLqhVL?usp=sharing](https://colab.research.google.com/drive/1E1GejUDfO0JPaoGP4viRDwNLnuvLqhVL?usp=sharing)
* **Tautan Dataset :**https://drive.google.com/drive/folders/11nlvniiA3a1iYx7IecS7OGa4KZpH3ibm?usp=sharing*
*    *(Dokumen ini mencakup model *similarity* atau dataset yang digunakan untuk melatih atau memvalidasi Agent.)*
* **Catatan LLM Agent:** Proyek ini tidak menggunakan model *Machine Learning lokal* yang di-*serve*. Seluruh proses inferensi untuk rekomendasi dan analisis keamanan dilakukan secara *real-time* melalui **API LLM (Google Generative AI/Gemini)** yang diatur oleh *workflow* CrewAI.

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

Berikut adalah alur penggunaan sistem dari sudut pandang pengguna (yang akan dipresentasikan saat *live demo*):

1.  Pengguna **Register/Login** melalui *frontend* aplikasi.
2.  Pengguna mengisi *form* input, seperti masalah kulit, tujuan penggunaan produk, dan kebutuhan formulasi (di halaman *Analyze*).
3.  Sistem menerima input dan memprosesnya menggunakan **Agentic AI** melalui *backend* FastAPI.
4.  Sistem melakukan pencarian bahan aktif yang relevan berdasarkan konteks input pengguna.
5.  Sistem menganalisis keamanan, kompatibilitas antar bahan, serta batas konsentrasi aman (menggunakan LLM *agent*).
6.  Sistem menghasilkan rekomendasi formulasi atau kandidat kandungan baru.
7.  Hasil ditampilkan kepada pengguna berupa formulasi, manfaat, serta rekomendasi pemakaian.
8.  Hasil rekomendasi dapat dilihat kembali melalui fitur **History Log**.
9.  Pengguna juga dapat menghapus riwayat hasil rekomendasi sesuai kebutuhan.
