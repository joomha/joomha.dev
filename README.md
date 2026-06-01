# Jomha.dev — Documentation & Guide

Selamat datang di repositori portofolio **Ahmad Jumhadi (@joomha)**. Website ini dibangun menggunakan **Astro v5** dengan **Tailwind CSS v4** dan mengusung desain **Bento Grid Layout**.

---

## Cara Menambah Artikel Baru

Semua konten blog/artikel berada di folder `src/content/blog/`. 

1. **Buat file baru**: Gunakan ekstensi `.md` atau `.mdx`. Rekomendasi: `src/content/blog/2026/judul-artikel.mdx`.
2. **Atur Frontmatter**: Pastikan di bagian atas file terdapat metadata seperti ini:
```markdown
---
title: "Judul Artikel kamu"
pubDatetime: 2026-03-25T23:00:00+07:00
description: "Deskripsi singkat artikel."
tags:
  - webdev
  - ai
---
Konten artikel kamu di sini...
```

---

## Penempatan Gambar

Untuk gambar di dalam artikel, kamu punya dua pilihan:
1. **Lokal**: Masukkan gambar ke folder `public/assets/` dan panggil di MDX:
   `![Deskripsi](/assets/nama-gambar.jpg)`
2. **External**: Gunakan URL langsung dari layanan hosting gambar.

---

## Mengubah Warna & Tema

Warna utama diatur di file `src/styles/global.css`.
- Cari bagian `:root` untuk **Light Mode**.
- Cari bagian `html[data-theme="dark"]` untuk **Dark Mode**.
- Website ini menggunakan **True Dark** (latar belakang `#050505`).

---

## Mengedit Halaman Awal (Landing Page)

Konten halaman utama (Headline, Hero section, dan susunan Bento Grid) dapat kamu edit langsung di file:
`src/pages/index.astro`

Di sana kamu bisa mengubah teks "I'm Jomha", deskripsi diri, serta tautan-tautan di dalam kotak bento.

---

## Portfolio / Proyek

Saat ini, portofolio diarahkan untuk menggunakan format blog post atau bisa ditambahkan section khusus di `src/pages/index.astro`. 

**Saran saya:** Masukkan portofolio sebagai artikel blog dengan tag `portfolio`. Dengan begitu, proyek kamu akan muncul otomatis di daftar tulisan terbaru.

---

## Menjalankan Secara Lokal

Jika kamu ingin mengedit dan melihat hasilnya langsung:
1. Buka terminal di folder ini.
2. Jalankan `npm install` (hanya sekali).
3. Jalankan `npm run dev`.
4. Buka `http://localhost:4321`.

---

## Auto Article Agent

Repo ini dilengkapi sistem **Auto Article Agent v2** — pipeline otomatis yang menghasilkan dan mempublikasikan artikel blog secara rutin (setiap 3 hari) tanpa intervensi manual.

### Cara Kerja

```
RSS Research → Topic Ranking → Duplicate Check → AI Generate Article
→ Validate MDX → Quality Score → Generate Thumbnail → Publish → Deploy
```

| Komponen | Teknologi |
|----------|-----------|
| Automation | GitHub Actions (cron setiap 3 hari pukul 10:00 WIB) |
| AI Engine | OpenRouter API (GPT-OSS 120b → Llama 4 → Gemini Flash) |
| Scripting | Python 3.11 |
| Thumbnail | Pillow (dark theme, 1200×630) |
| Validation | YAML frontmatter + MDX body check |
| Deploy | Otomatis via Vercel (trigger on push) |

### Struktur File Agent

```
scripts/agent/
├── main.py              # Pipeline orchestrator
├── researcher.py        # RSS feed scraper (6 sumber)
├── topic_ranker.py      # Scoring & ranking topik
├── duplicate_checker.py # Cek duplikasi via history
├── generator.py         # LLM article generator
├── validator.py         # MDX & frontmatter validator
├── quality_scorer.py    # Quality scoring (threshold: 7/10)
├── image_generator.py   # Thumbnail generator
├── publisher.py         # File saver & history updater
├── utils.py             # Logging & helpers
└── requirements.txt     # Python dependencies

data/
└── article_history.json # Riwayat artikel (anti-duplikat)
```

### Setup

Tambahkan 2 secret di **GitHub → Settings → Secrets → Actions**:

| Secret | Keterangan |
|--------|------------|
| `OPENROUTER_API_KEY` | API key dari [openrouter.ai](https://openrouter.ai) |
| `GH_TOKEN` | GitHub Personal Access Token (scope: `repo`) |

### Menjalankan Manual

1. Buka tab **Actions** di GitHub
2. Pilih workflow **"Auto Article Agent"**
3. Klik **"Run workflow"**

### Menjalankan Lokal

```bash
# Buat file .env di root project
echo "OPENROUTER_API_KEY=sk-or-v1-xxx" > .env

# Install dependencies
pip install -r scripts/agent/requirements.txt

# Jalankan pipeline
python scripts/agent/main.py
```

---

