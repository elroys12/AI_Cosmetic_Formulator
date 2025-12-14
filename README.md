# novel-chemicals-discovery-agent
# AI Cosmetic Formulator

**Sistem Cerdas untuk Analisis Keamanan dan Formulasi Skincare**

---

## 1. Deskripsi Singkat Proyek

AI Cosmetic Formulator merupakan sistem cerdas yang dirancang untuk membantu proses **analisis keamanan bahan kosmetik** serta **formulasi produk skincare** menggunakan pendekatan Artificial Intelligence. Proyek ini memanfaatkan teknologi **Large Language Model (LLM)** yang diorkestrasi dalam sebuah workflow berbasis agent.

Melalui pipeline ini, sistem dapat membantu pengguna dalam:

* Menganalisis keamanan dan kelayakan bahan skincare
* Memberikan rekomendasi formulasi secara terstruktur
* Menjalankan proses analisis secara otomatis dan berurutan

Proyek ini dikembangkan sebagai bagian dari **capstone project**, dengan fokus pada penerapan AI modern dalam domain kosmetik dan perawatan kulit.

---

## 2. Petunjuk Setup Environment

### A. Prasyarat

Pastikan environment telah memenuhi kebutuhan berikut:

* **Python 3.9 atau lebih baru**
* Jupyter Notebook
* Koneksi internet
* API Key Google Generative AI

### B. Instalasi Library

Instal dependensi yang digunakan dalam proyek dengan perintah berikut:

```bash
pip install crewai litellm google-generativeai python-dotenv
```

### C. Konfigurasi Environment Variable

Proyek ini menggunakan model AI berbasis API. Silakan siapkan API Key dan simpan sebagai environment variable.

Menggunakan terminal:

```bash
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

Atau menggunakan file `.env`:

```env
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
```

API Key ini digunakan untuk mengakses layanan **Google Generative AI (Gemini)** melalui LiteLLM.

---

## Catatan

* Proyek ini tidak menggunakan model Machine Learning lokal.
* Seluruh proses inferensi dilakukan melalui **API LLM**.
* Struktur pipeline bersifat modular dan dapat dikembangkan lebih lanjut.

---


