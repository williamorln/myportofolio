# myportofolio

Website portofolio pribadi William Orlando, dibangun sebagai bagian dari mata kuliah **Pemrograman Berbasis Platform (PBP)**, Fakultas Ilmu Komputer, Universitas Indonesia.

Proyek ini dikerjakan bertahap mengikuti rangkaian Tutorial dan Tugas Individu tiap minggu, jadi struktur dan fiturnya akan terus berkembang sepanjang semester.

## Tech Stack

- **Backend:** Django 6.1 (Python)
- **Frontend:** HTML5 + CSS3 murni (belum pakai JavaScript maupun database untuk konten)
- **Static files:** WhiteNoise
- **Deployment:** PWS (Platform-as-a-Service Fasilkom UI)

## Struktur Proyek

```
myportofolio/
├── env/                  # virtual environment (tidak di-commit)
├── portofolio/            # package konfigurasi Django
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── templates/
│   └── index.html         # halaman utama portofolio
├── static/
│   ├── css/style.css
│   └── img/
├── manage.py
└── requirements.txt
```

## Progress Mingguan

Proyek ini dibangun bertahap mengikuti rangkaian Tutorial dan Tugas Individu tiap minggu. Langkah instalasi & menjalankan project di bagian "Menjalankan Proyek Secara Lokal" di bawah berlaku sama untuk setiap minggu — belum ada dependency atau langkah setup tambahan selain yang sudah ada dari Tutorial 0, karena proyek masih di tahap HTML5/CSS3 murni (migrasi database baru untuk fitur dinamis baru akan mulai dari Tutorial 02/MVT).

- **Tutorial 0** (Agustus 2026) &mdash; Setup awal proyek Django, virtual environment, dan koneksi ke PWS Fasilkom UI.
- **Tutorial 1** (31 Agustus 2026) &mdash; Halaman "About Me" pertama: struktur `views`/`urls`/`templates`/`static`, diisi data profil sendiri (nama, NPM, foto, bio).
- **Individual Assignment 1** (7 September 2026) &mdash; Menambahkan section Skills, Experience, dan Projects, lalu redesign visual penuh ke gaya minimalis modern: dark mode toggle, sticky navigation, vertical timeline untuk Experience, dan format showcase Problem/Solution/Tech Stack untuk Projects.

## Menjalankan Proyek Secara Lokal

1. Clone repo ini, lalu masuk ke foldernya.
2. Buat dan aktifkan virtual environment:
   ```
   python -m venv env
   env\Scripts\activate      # Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Buat file `.env` di root project, isi minimal:
   ```
   PRODUCTION=False
   ```
5. Jalankan migrasi database:
   ```
   python manage.py migrate
   ```
6. Jalankan server:
   ```
   python manage.py runserver
   ```
7. Buka `http://127.0.0.1:8000/` di browser.

## Deployment

Proyek ini di-deploy ke PWS Fasilkom UI. Untuk deploy ulang setelah ada perubahan:
```
git push pws master
```

## Pertanyaan Reflektif

### Tugas 1

1. Iya, hampir semua bagian halaman ini pakai elemen semantik HTML5: `<header>` + `<nav>` untuk navigasi situs, `<main>` sebagai pembungkus konten utama, dan satu `<section>` per bagian (Hero, About, Skills, Experience, Projects, Contact) supaya strukturnya jelas kalau dibaca ulang tanpa perlu lihat CSS-nya dulu. Di Projects, tiap project aku bungkus pakai `<article>` karena masing-masing memang berdiri sendiri dan bisa dipahami lepas dari konteks section-nya. Yang paling menarik justru terjadi di Experience: awalnya aku pakai `<details>`/`<summary>` biar collapsible, tapi pas redesign minggu ini aku ganti jadi `<ol>` (ordered list) buat timeline-nya — karena riwayat pengalaman itu memang punya urutan kronologis, jadi `<ol>` lebih jujur secara semantik dibanding `<ul>` atau tumpukan `<div>` biasa, meskipun secara visual dia dirender sebagai garis timeline vertikal, bukan daftar bernomor. `<footer>` juga aku pakai khusus buat info kontak dan NPM, biar jelas terpisah dari konten utama.

2. Tantangan pertama muncul di bagian yang kelihatannya paling sederhana: foto profil di hero section. Aku pakai CSS Grid 2 kolom yang di layar kecil harus collapse jadi 1 kolom, tapi ukuran asli file foto (resolusinya cukup besar) tetap dianggap browser sebagai "lebar minimum" grid item-nya, jadi kolomnya nggak mau menyempit sepenuhnya dan bikin halaman overflow ke samping. Solusinya nambahin `min-width: 0` di grid item-nya. Setelah nambah fitur baru (sticky header, dark mode, redesign minggu ini), muncul dua tantangan lain: pertama, pas header dibikin `position: sticky`, klik nav ke suatu section jadi bikin heading-nya ketutupan header, karena `scroll-margin-top` yang aku set cuma pas buat header versi desktop (satu baris) — di mobile header-nya stack jadi 3 baris yang jauh lebih tinggi, jadi perlu breakpoint terpisah dengan nilai clearance yang lebih besar. Kedua, aku sempat nambahin animasi fade-in di hero pas pertama load, tapi baru sadar itu berisiko bikin konten paling penting di halaman (nama, foto, tombol) kelihatan nyaris invisible kalau di-render sebelum animasinya kelar — akhirnya animasi itu aku hapus dari bagian yang krusial, dan cuma nyisain animasi kecil di bagian yang nggak fatal kalau telat muncul (teks role di bawah nama), sekalian nambahin `prefers-reduced-motion` biar user yang aksesibilitasnya minta kurangi animasi tetap dapet versi statis. Cara aku evaluasi: resize manual dari lebar desktop ke sempit sambil merhatiin elemen mana yang "ngotot" nggak mau nyusut atau ketutupan elemen lain, dicek juga pakai screenshot otomatis di beberapa lebar viewport (1280px dan sekitar 375&ndash;390px) biar nggak cuma ngandelin satu ukuran layar.

3. Batasan paling kerasa itu soal skala konten: halaman ini sekarang punya 7 project dan belasan entri pengalaman yang semuanya ditulis manual langsung di file HTML template. Tiap kali ada pengalaman atau project baru, aku harus buka dan edit template-nya langsung — nggak ada tempat terpusat buat kelola datanya. Section Contact juga masih "palsu" secara fungsional: tombol Email cuma buka link `mailto:`, bukan form yang beneran ngirim dan nyimpen pesan. Untuk iterasi berikutnya, yang paling pengin aku bangun adalah pindahin data Projects dan Experience ke model Django (sesuai topik Tutorial 02 soal MVT) supaya bisa dikelola lewat Django admin tanpa oprek HTML tiap kali update, dan bikin form Contact yang beneran nyimpen pesan pengunjung ke database.

## AI Disclosure

Konten yang ditampilkan di halaman ini (deskripsi project, pengalaman organisasi, skill, dan bio) aku tulis sendiri dari draft yang udah aku siapin duluan, bukan hasil karangan AI. Struktur dasar halaman dari Tutorial 1 juga aku kerjain sendiri. Untuk pengembangan lanjutan tiap minggu (termasuk redesign minggu ini), aku tetap yang mimpin arah desain dan ikut coding langsung di beberapa bagian, dan aku pakai Claude (Claude Code) sebagai asisten buat mempercepat implementasi teknis dan bantu debug beberapa hal spesifik:

- Debug bug CSS Grid di hero section yang bikin halaman overflow ke samping saat dibuka di layar sempit/mobile — AI bantu aku nemuin penyebabnya (ukuran asli foto profil yang jadi "lebar minimum" grid item) dan solusinya (`min-width: 0`).
- Bantu nulis sebagian kode dari arah desain yang udah aku tentuin sendiri (skill tags, timeline Experience, project showcase, dark mode toggle), sekaligus nemuin dan benerin bug animasi fade-in di hero yang berisiko bikin konten utama nyaris invisible pas halaman pertama dibuka.

Semua kode dan konten tetap aku review, sesuaikan, dan pahami sebelum di-commit — posisi AI di sini buat mempercepat proses coding/debugging, bukan gantiin keputusan desain, isi konten, maupun kontribusi coding yang tetap aku pegang.
