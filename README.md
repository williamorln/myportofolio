# myportofolio

Website portofolio pribadi William Orlando, dibangun sebagai bagian dari mata kuliah **Pemrograman Berbasis Platform (PBP)**, Fakultas Ilmu Komputer, Universitas Indonesia.

Proyek ini dikerjakan bertahap mengikuti rangkaian Tutorial dan Tugas Individu tiap minggu, jadi struktur dan fiturnya akan terus berkembang sepanjang semester.

## Tech Stack

- **Backend:** Django 5.2 (Python) dengan pola Model-View-Template
- **Frontend:** Django Template Language, HTML5, dan CSS3
- **Database:** SQLite untuk lokal dan PostgreSQL untuk deployment
- **Static files:** WhiteNoise
- **Deployment:** PWS (Platform-as-a-Service Fasilkom UI)

## Struktur Proyek

```
myportofolio/
├── env/                  # virtual environment (tidak di-commit)
├── main/                 # app profil, experience, dan projects
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── portofolio/            # package konfigurasi Django
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── experience.html    # daftar experience dari database
│   ├── projects.html      # daftar project dari database
│   └── index.html         # halaman utama portofolio
├── static/
│   ├── css/style.css
│   └── img/
├── manage.py
└── requirements.txt
```

## Progress Mingguan

Proyek ini dibangun bertahap mengikuti rangkaian Tutorial dan Tugas Individu tiap minggu. Langkah instalasi dan menjalankan project tersedia pada bagian "Menjalankan Proyek Secara Lokal".

- **Tutorial 0** (Agustus 2026) &mdash; Setup awal proyek Django, virtual environment, dan koneksi ke PWS Fasilkom UI.
- **Tutorial 1** (31 Agustus 2026) &mdash; Halaman "About Me" pertama: struktur `views`/`urls`/`templates`/`static`, diisi data profil sendiri (nama, NPM, foto, bio).
- **Individual Assignment 1** (7 September 2026) &mdash; Menambahkan section Skills, Experience, dan Projects, lalu redesign visual penuh ke gaya minimalis modern: dark mode toggle, sticky navigation, vertical timeline untuk Experience, dan format showcase Problem/Solution/Tech Stack untuk Projects.
- **Tutorial 2** (9 September 2026) &mdash; Menerapkan pola MVT melalui app `main`, model `Experience`, context profil, halaman experience dinamis, routing aplikasi, migrasi database, dan unit test Django.
- **Individual Assignment 2** (12&ndash;13 September 2026) &mdash; Menerapkan pola MVT yang sama untuk bagian Projects: model `Project`, migrasi skema sekaligus migrasi data (memindahkan project dari HTML statis ke database, lalu menghapus satu project yang sudah tidak relevan), halaman `/projects/` dinamis, registrasi model ke Django admin, serta unit test baru. Sekalian melengkapi data `Experience` dengan riwayat pengalaman asli beserta foto tiap event, menggantikan data uji coba yang sebelumnya ada di database.

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

### Tugas 2

1. Alurnya dimulai dari browser mengirim request ke `/projects/`. Django pertama-tama cek `portofolio/urls.py` (urls.py tingkat proyek) — di situ cuma ada `path('', include('main.urls'))`, jadi Django melempar semua routing ke `main/urls.py` (urls.py tingkat aplikasi). Di `main/urls.py`, path `projects/` dicocokkan ke fungsi `show_projects`, dan berkat `app_name = 'main'`, URL ini bisa dipanggil di template pakai nama `main:show_projects` tanpa hardcode path. Django lalu memanggil `show_projects` di `main/views.py` — di situ view mengambil data dari **model** `Project` lewat `Project.objects.all()`, memasukkannya ke dictionary `context` (bersama data profil seperti nama dan NPM), lalu memanggil `render(request, 'projects.html', context)`. Perintah ini menyuruh Django Template Engine membaca **template** `projects.html`, mengganti setiap placeholder (`{% for project in project_list %}`, `{{ project.title }}`, dst.) dengan data asli dari context, dan hasil akhirnya berupa HTML murni dikirim balik sebagai response ke browser. Singkatnya: browser &rarr; urls.py proyek &rarr; urls.py aplikasi &rarr; view &rarr; model (ambil data) &rarr; view (susun context) &rarr; template (render HTML) &rarr; browser.

2. Karena kalau data ditulis langsung di template, "data" dan "tampilan" jadi tercampur dalam satu file yang sama — tiap ada project baru atau ada yang perlu diedit, aku harus buka dan edit file HTML-nya langsung, padahal HTML seharusnya cuma soal tampilan, bukan tempat menyimpan data. Dengan data disimpan di model, dua hal itu jadi terpisah: kalau mau menambah/mengedit/menghapus project, aku (atau siapa pun yang mengelola situs ini nanti) tinggal mengubah data lewat Django admin, tanpa perlu menyentuh HTML atau memahami cara kerja Django sama sekali. Data yang terstruktur di database juga bisa dipakai ulang di tempat lain (misalnya ringkasan project di homepage, atau di-expose lewat API), yang nggak mungkin dilakukan kalau datanya "terkunci" di dalam satu file HTML. Dampaknya ke pemeliharaan: bug atau typo cukup diperbaiki di satu sumber data, bukan dicari di banyak file HTML. Dampaknya ke pengembangan: fitur seperti pencarian, filter, atau pengurutan project jadi mungkin dibangun, karena datanya sudah terstruktur, bukan teks bebas di HTML.

3. `makemigrations` hanya membuat **rencana perubahan** &mdash; Django membandingkan `models.py` saat ini dengan migration terakhir, lalu menulis file migration baru berisi instruksi perubahan (belum diterapkan ke database). `migrate` adalah yang benar-benar **menerapkan** instruksi itu ke database &mdash; membuat, mengubah, atau menghapus tabel dan kolom sesuai file migration yang ada. Contoh konkret dari tugas ini: begitu aku menambahkan model `Project` baru di `models.py`, aku menjalankan `makemigrations` dan Django membuat file `0002_project.py`, tapi database itu sendiri belum berubah sama sekali di titik ini. Baru setelah aku menjalankan `migrate`, tabel `main_project` benar-benar terbentuk di `db.sqlite3`. Kalau cuma menjalankan `makemigrations` tanpa `migrate`, aku hanya akan punya "rencana" di atas kertas, sementara kondisi database masih yang lama.

## AI Disclosure

Konten yang ditampilkan di halaman ini (deskripsi project, pengalaman organisasi, skill, dan bio) aku tulis sendiri dari draft yang udah aku siapin duluan, bukan hasil karangan AI. Struktur dasar halaman dari Tutorial 1 aku kerjain sendiri, dan **Tutorial 2 (model, view, template, migrasi, serta unit test pertama untuk Experience) aku kerjain 100% sendiri tanpa bantuan AI sama sekali**. Untuk pengembangan lanjutan tiap minggu, aku tetap yang memimpin arah desain/pendekatan dan ikut coding langsung di berbagai bagian, dan aku pakai Claude (Claude Code) sebagai asisten buat mempercepat implementasi teknis dan bantu debug beberapa hal spesifik:

- Debug bug CSS Grid di hero section yang bikin halaman overflow ke samping saat dibuka di layar sempit/mobile — AI bantu aku nemuin penyebabnya (ukuran asli foto profil yang jadi "lebar minimum" grid item) dan solusinya (`min-width: 0`).
- Bantu nulis sebagian kode dari arah desain yang udah aku tentuin sendiri (skill tags, timeline Experience, project showcase, dark mode toggle), sekaligus nemuin dan benerin bug animasi fade-in di hero yang berisiko bikin konten utama nyaris invisible pas halaman pertama dibuka.
- Untuk Tugas 2: karena pola MVT-nya udah aku bangun sendiri di Tutorial 2 (lewat Experience), pendekatan untuk model `Project` ini tinggal aku terapin ulang dengan pola yang sama. AI di sini fungsinya lebih sebagai stimulus/sparring partner buat mastiin desain field model-nya udah sesuai kebutuhan, dan bantu debug satu error di unit test yang disebabkan oleh HTML auto-escaping pada tanda petik.
- Untuk pelengkapan data Experience (foto tiap event, isi ulang riwayat pengalaman asli) dan penghapusan satu project yang sudah tidak dipakai: aku yang nentuin data & foto mana yang dipakai, AI bantu implementasi migration-nya sekaligus nemuin kalau tipe field `thumbnail` (`URLField`) bakal bermasalah dipakai buat path foto lokal lewat Django admin.

Semua kode dan konten tetap aku review, sesuaikan, dan pahami sebelum di-commit — posisi AI di sini buat mempercepat proses coding/debugging, bukan gantiin keputusan desain, isi konten, maupun kontribusi coding yang tetap aku pegang.
