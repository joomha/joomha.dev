# Jomha.dev — Documentation & Guide

Selamat datang di repositori portofolio **Ahmad Jumhadi (@joomha)**. Website ini dibangun menggunakan **Astro v5** dengan **Tailwind CSS v4** dan mengusung desain **Bento Grid Layout**.

---

## Cara Menambah Artikel Baru

Semua konten blog/artikel berada di folder `src/content/blog/`. 

1. **Buat file baru**: Gunakan ekstensi `.md` atau `.mdx`. Rekomendasi: `src/content/blog/2026/judul-artikel.mdx`.
2. **Atur Frontmatter**: Pastikan di bagian atas file terdapat metadata seperti ini:
```markdown
---
title: "Judul Artikel Anda"
pubDatetime: 2026-03-25T23:00:00+07:00
description: "Deskripsi singkat artikel."
tags:
  - webdev
  - ai
---
Konten artikel Anda di sini...
```

---

## Penempatan Gambar

Untuk gambar di dalam artikel, Anda punya dua pilihan:
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

Konten halaman utama (Headline, Hero section, dan susunan Bento Grid) dapat Anda edit langsung di file:
`src/pages/index.astro`

Di sana Anda bisa mengubah teks "I'm Jomha", deskripsi diri, serta tautan-tautan di dalam kotak bento.

---

## Portfolio / Proyek

Saat ini, portofolio diarahkan untuk menggunakan format blog post atau bisa ditambahkan section khusus di `src/pages/index.astro`. 

**Saran saya:** Masukkan portofolio sebagai artikel blog dengan tag `portfolio`. Dengan begitu, proyek Anda akan muncul otomatis di daftar tulisan terbaru.

---

## menjalankan Secara Lokal

Jika Anda ingin mengedit dan melihat hasilnya langsung:
1. Buka terminal di folder ini.
2. Jalankan `npm install` (hanya sekali).
3. Jalankan `npm run dev`.
4. Buka `http://localhost:4321`.

---
