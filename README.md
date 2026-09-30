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
│   ├── forms.py           # ModelForm untuk Project dan Experience
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── portofolio/            # package konfigurasi Django
│   ├── settings.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html          # skeleton bersama: head, navigasi, pesan, footer
│   ├── experience_form.html
│   ├── experience_confirm_delete.html
│   ├── experience.html    # daftar experience dari database
│   ├── projects.html      # daftar project dari database
│   └── index.html         # halaman utama portofolio
├── static/
│   ├── css/style.css
│   ├── js/toast.js
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
- **Tutorial 3 dan Individual Assignment 3** (September 2026) &mdash; Menambahkan form, CRUD, filter, dan endpoint JSON untuk Projects dan Experience.
- **Tutorial 4** (27 September 2026) &mdash; Menambahkan register, login, logout, cookie `last_login`, pembatasan pengelolaan Projects, dan fitur star pada Projects.
- **Individual Assignment 4** (27 September 2026) &mdash; Menerapkan empat tingkat akses pada Experience, peran Editor, star Experience, serta perlindungan data pengguna pada API JSON.
- **Tutorial 5** (30 September 2026) &mdash; Mengubah halaman Projects menjadi interaktif dengan Fetch API, pencarian debounce, modal dan form AJAX, toast, serta perlindungan XSS di browser dan server.

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

## Form dan Data Delivery — Minggu 3

Tutorial 03 menyediakan skeleton `base.html`, form tambah project, penghapusan project, pencarian, dan JSON project. Tugas 3 melanjutkannya pada bagian **Experience**. Semua template halaman mewarisi `base.html`; template di `components/` merupakan fragmen yang disertakan melalui `include`.

`ExperienceForm` menyediakan seluruh field yang dapat diedit: `title` (CharField), `description` (TextField), `category` (CharField dengan pilihan), `thumbnail` (CharField opsional), dan `ended_at` (DateTimeField opsional). `id` dan timestamp otomatis `started_at` tidak dimasukkan ke form. `ended_at` adalah data waktu selesai yang diisi pengguna, bukan timestamp pencatatan otomatis; kosong berarti masih berlangsung. Waktu pada form menggunakan UTC, sesuai konfigurasi proyek.

| URL | Fungsi |
| --- | --- |
| `/experience/` | Daftar experience setelah JSON dideserialisasi, pencarian judul, dan filter status |
| `/experience/add/` | Form tambah experience |
| `/experience/<uuid>/edit/` | Form edit dengan data awal dari objek yang dipilih |
| `/experience/<uuid>/delete/` | GET untuk konfirmasi, POST untuk menghapus |
| `/api/experience/` | Data experience dalam JSON |
| `/api/projects/` | Data project dalam JSON dari Tutorial 03 |

Filter experience berlaku pada halaman dan API, misalnya `/api/experience/?title=staff&status=ongoing`. Pilihan status adalah `ongoing` atau `completed`; tanpa filter menampilkan semua data. Tombol **Lihat JSON** mempertahankan filter yang sedang dipakai. Fitur tambahan meliputi jumlah hasil, pesan sukses, keadaan hasil kosong, dan konfirmasi hapus yang tetap bekerja tanpa JavaScript.

Setup minggu ini menggunakan langkah instalasi lokal di atas; tidak ada dependensi atau perubahan skema baru. Verifikasi:

```sh
python manage.py migrate
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py runserver
```

Uji alur lewat `/experience/`: tambah pengalaman, edit deskripsi/status selesai, cari judulnya, buka JSON, kemudian hapus melalui konfirmasi. Tes otomatis memakai database sementara dan mencakup form invalid, edit tanpa membuat baris baru, CSRF, UUID tidak ditemukan, filter, deserialisasi, dan escaping HTML. Data portofolio lokal tidak dihapus oleh tes.

Pada Tugas 3, alur CRUD ini belum memiliki pembatasan akun. Pembatasan autentikasi dan otorisasi kemudian ditambahkan pada Tugas 4.

Pengumpulan Tugas 3 menggunakan **tautan commit GitHub yang telah di-push**, pada repositori publik, paling lambat **21 September 2026 pukul 23.59 WIB**. Tutorial 03 harus sudah selesai paling lambat 16 September 2026. Push atau pengumpulan tidak dilakukan oleh perintah pengujian di atas.

## Authentication dan Authorization — Minggu 4

Tugas 4 menerapkan autentikasi dan otorisasi pada bagian **Experience** yang dikembangkan di Tugas 3. Halaman daftar dan endpoint JSON tetap terbuka untuk umum. Perubahan data diperiksa di sisi server, sehingga menyembunyikan tombol di template bukan satu-satunya perlindungan.

| Peran | Lihat | Star / Unstar | Tambah | Edit | Hapus |
| --- | --- | --- | --- | --- | --- |
| Pengunjung | Ya | Harus login | Tidak | Tidak | Tidak |
| Pengguna biasa | Ya | Ya | Tidak | Tidak | Tidak |
| Editor | Ya | Ya | Tidak | Ya | Tidak |
| Superuser | Ya | Ya | Ya | Ya | Ya |

Peran Editor menggunakan Django Group bernama `Editor`. Penetapan role hanya dilakukan oleh superuser melalui Django Admin:

1. Buat superuser dengan `python manage.py createsuperuser` dan login ke `/admin/`.
2. Buka **Authentication and Authorization → Groups**, lalu buat group bernama `Editor`.
3. Buka akun pada menu **Users** dan masukkan akun yang dipilih ke group `Editor`.

Endpoint baru `/experience/<uuid>/star/` hanya menerima `POST` dan dilindungi `{% csrf_token %}`. Relasi `ManyToManyField` memastikan satu pengguna hanya tercatat sekali pada satu experience. Tombol menampilkan status Star/Unstar dan jumlah total star. Endpoint `/api/experience/` tetap mendukung filter dari Tugas 3 dan menampilkan username pemberi star melalui natural key, bukan ID database internal.

Verifikasi Tugas 4:

```sh
python manage.py migrate
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py runserver
```

Tes otomatis memeriksa akses pengunjung, pengguna biasa, Editor, dan superuser; toggle star; penolakan metode selain POST; visibilitas tombol; CSRF; serta bentuk data pada API.

## JavaScript dan AJAX — Minggu 5

Halaman `/projects/` memuat kerangka HTML terlebih dahulu, kemudian mengambil data dari `/api/projects/` melalui Fetch API. Respons API dirakit manual agar setiap kartu memperoleh jumlah star, nama pemberi star, serta status star milik pengguna yang sedang login. Pencarian berjalan 300 milidetik setelah pengguna berhenti mengetik dan request lama dibatalkan dengan `AbortController`.

Superuser dapat membuka modal tambah proyek tanpa berpindah halaman. Form dikirim ke `/projects/add-ajax/` menggunakan `FormData` dan header `X-CSRFToken`. Respons berhasil menutup modal, menampilkan toast, dan memuat ulang daftar proyek tanpa reload halaman. Endpoint tetap memeriksa `is_superuser` di server dan mengembalikan JSON 403 bagi pengunjung atau pengguna biasa.

Data dari JSON di-escape sebelum dipasang melalui `innerHTML`. `ProjectForm` juga menghapus tag HTML dari judul, problem, solution, dan tech stack, serta menolak judul yang hanya berisi tag. Kedua lapisan dipakai bersama karena sanitasi input tidak menggantikan escaping ketika data ditampilkan.

Verifikasi Tutorial 5:

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py runserver
```

Tes mencakup struktur API AJAX, pencarian, status star per pengguna, hak akses endpoint tambah, validasi form, sanitasi HTML, metode HTTP, dan perlindungan CSRF.

## Pertanyaan Reflektif

### Tugas 1

1. Iya, hampir semua bagian halaman ini pakai elemen semantik HTML5: `<header>` + `<nav>` untuk navigasi situs, `<main>` sebagai pembungkus konten utama, dan satu `<section>` per bagian (Hero, About, Skills, Experience, Projects, Contact) supaya strukturnya jelas kalau dibaca ulang tanpa perlu lihat CSS-nya dulu. Di Projects, tiap project aku bungkus pakai `<article>` karena masing-masing memang berdiri sendiri dan bisa dipahami lepas dari konteks section-nya. Yang paling menarik justru terjadi di Experience: awalnya aku pakai `<details>`/`<summary>` biar collapsible, tapi pas redesign minggu ini aku ganti jadi `<ol>` (ordered list) buat timeline-nya — karena riwayat pengalaman itu memang punya urutan kronologis, jadi `<ol>` lebih jujur secara semantik dibanding `<ul>` atau tumpukan `<div>` biasa, meskipun secara visual dia dirender sebagai garis timeline vertikal, bukan daftar bernomor. `<footer>` juga aku pakai khusus buat info kontak dan NPM, biar jelas terpisah dari konten utama.

2. Tantangan pertama muncul di bagian yang kelihatannya paling sederhana: foto profil di hero section. Aku pakai CSS Grid 2 kolom yang di layar kecil harus collapse jadi 1 kolom, tapi ukuran asli file foto (resolusinya cukup besar) tetap dianggap browser sebagai "lebar minimum" grid item-nya, jadi kolomnya nggak mau menyempit sepenuhnya dan bikin halaman overflow ke samping. Solusinya nambahin `min-width: 0` di grid item-nya. Setelah nambah fitur baru (sticky header, dark mode, redesign minggu ini), muncul dua tantangan lain: pertama, pas header dibikin `position: sticky`, klik nav ke suatu section jadi bikin heading-nya ketutupan header, karena `scroll-margin-top` yang aku set cuma pas buat header versi desktop (satu baris) — di mobile header-nya stack jadi 3 baris yang jauh lebih tinggi, jadi perlu breakpoint terpisah dengan nilai clearance yang lebih besar. Kedua, aku sempat nambahin animasi fade-in di hero pas pertama load, tapi baru sadar itu berisiko bikin konten paling penting di halaman (nama, foto, tombol) kelihatan nyaris invisible kalau di-render sebelum animasinya kelar — akhirnya animasi itu aku hapus dari bagian yang krusial, dan cuma nyisain animasi kecil di bagian yang nggak fatal kalau telat muncul (teks role di bawah nama), sekalian nambahin `prefers-reduced-motion` biar user yang aksesibilitasnya minta kurangi animasi tetap dapet versi statis. Cara aku evaluasi: resize manual dari lebar desktop ke sempit sambil merhatiin elemen mana yang "ngotot" nggak mau nyusut atau ketutupan elemen lain, dicek juga pakai screenshot otomatis di beberapa lebar viewport (1280px dan sekitar 375&ndash;390px) biar nggak cuma ngandelin satu ukuran layar.

3. Batasan paling kerasa itu soal skala konten: halaman ini sekarang punya 7 project dan belasan entri pengalaman yang semuanya ditulis manual langsung di file HTML template. Tiap kali ada pengalaman atau project baru, aku harus buka dan edit template-nya langsung — nggak ada tempat terpusat buat kelola datanya. Section Contact juga masih "palsu" secara fungsional: tombol Email cuma buka link `mailto:`, bukan form yang beneran ngirim dan nyimpen pesan. Untuk iterasi berikutnya, yang paling pengin aku bangun adalah pindahin data Projects dan Experience ke model Django (sesuai topik Tutorial 02 soal MVT) supaya bisa dikelola lewat Django admin tanpa oprek HTML tiap kali update, dan bikin form Contact yang beneran nyimpen pesan pengunjung ke database.

### Tugas 2

1. Alurnya dimulai dari browser mengirim request ke `/projects/`. Django pertama-tama cek `portofolio/urls.py` (urls.py tingkat proyek) — di situ cuma ada `path('', include('main.urls'))`, jadi Django melempar semua routing ke `main/urls.py` (urls.py tingkat aplikasi). Di `main/urls.py`, path `projects/` dicocokkan ke fungsi `show_projects`, dan berkat `app_name = 'main'`, URL ini bisa dipanggil di template pakai nama `main:show_projects` tanpa hardcode path. Django lalu memanggil `show_projects` di `main/views.py` — di situ view mengambil data dari **model** `Project` lewat `Project.objects.all()`, memasukkannya ke dictionary `context` (bersama data profil seperti nama dan NPM), lalu memanggil `render(request, 'projects.html', context)`. Perintah ini menyuruh Django Template Engine membaca **template** `projects.html`, mengganti setiap placeholder (`{% for project in project_list %}`, `{{ project.title }}`, dst.) dengan data asli dari context, dan hasil akhirnya berupa HTML murni dikirim balik sebagai response ke browser. Singkatnya: browser &rarr; urls.py proyek &rarr; urls.py aplikasi &rarr; view &rarr; model (ambil data) &rarr; view (susun context) &rarr; template (render HTML) &rarr; browser.

2. Karena kalau data ditulis langsung di template, "data" dan "tampilan" jadi tercampur dalam satu file yang sama — tiap ada project baru atau ada yang perlu diedit, aku harus buka dan edit file HTML-nya langsung, padahal HTML seharusnya cuma soal tampilan, bukan tempat menyimpan data. Dengan data disimpan di model, dua hal itu jadi terpisah: kalau mau menambah/mengedit/menghapus project, aku (atau siapa pun yang mengelola situs ini nanti) tinggal mengubah data lewat Django admin, tanpa perlu menyentuh HTML atau memahami cara kerja Django sama sekali. Data yang terstruktur di database juga bisa dipakai ulang di tempat lain (misalnya ringkasan project di homepage, atau di-expose lewat API), yang nggak mungkin dilakukan kalau datanya "terkunci" di dalam satu file HTML. Dampaknya ke pemeliharaan: bug atau typo cukup diperbaiki di satu sumber data, bukan dicari di banyak file HTML. Dampaknya ke pengembangan: fitur seperti pencarian, filter, atau pengurutan project jadi mungkin dibangun, karena datanya sudah terstruktur, bukan teks bebas di HTML.

3. `makemigrations` hanya membuat **rencana perubahan** &mdash; Django membandingkan `models.py` saat ini dengan migration terakhir, lalu menulis file migration baru berisi instruksi perubahan (belum diterapkan ke database). `migrate` adalah yang benar-benar **menerapkan** instruksi itu ke database &mdash; membuat, mengubah, atau menghapus tabel dan kolom sesuai file migration yang ada. Contoh konkret dari tugas ini: begitu aku menambahkan model `Project` baru di `models.py`, aku menjalankan `makemigrations` dan Django membuat file `0002_project.py`, tapi database itu sendiri belum berubah sama sekali di titik ini. Baru setelah aku menjalankan `migrate`, tabel `main_project` benar-benar terbentuk di `db.sqlite3`. Kalau cuma menjalankan `makemigrations` tanpa `migrate`, aku hanya akan punya "rencana" di atas kertas, sementara kondisi database masih yang lama.

### Tugas 3

1. `ModelForm` menghubungkan form dengan model, sehingga tipe input, batas panjang, pilihan kategori, dan aturan wajib isi mengikuti definisi model. Ini mengurangi duplikasi dibanding menulis input HTML, validasi, dan penyimpanan secara manual. Pada proyek ini, `ExperienceForm` memakai `is_valid()` sebelum `save()`. Saat edit, `instance=experience` memastikan yang diperbarui adalah baris yang dipilih, bukan membuat baris baru. Form HTML manual tetap dapat digunakan, tetapi validasi server harus ditulis dengan benar. `{% csrf_token %}` menghasilkan input token yang diperiksa middleware Django untuk permintaan POST. Tujuannya mencegah situs lain mengirim tindakan perubahan data dengan memanfaatkan sesi pengguna tanpa persetujuannya. Token bukan pengganti autentikasi atau otorisasi.

2. JSON umumnya lebih ringkas karena tidak memerlukan pasangan tag pembuka dan penutup seperti XML. Struktur objek, array, string, angka, boolean, dan null juga sesuai dengan data yang biasa dipakai aplikasi web. JavaScript dapat membaca JSON langsung dengan `JSON.parse()` atau `response.json()`, sehingga pertukaran data antara backend dan frontend sederhana. XML tetap berguna ketika memerlukan namespace, atribut, atau struktur dokumen yang kompleks; JSON lebih sesuai untuk kebutuhan daftar experience dalam proyek ini, bukan selalu lebih baik untuk semua kasus.

3. Request `/api/experience/` dicocokkan oleh URL router ke `get_experience_json`. View mengambil QuerySet `Experience`, menerapkan pencarian/filter, lalu memanggil `serializers.serialize('json', experiences)`. Hasil berupa teks JSON dikembalikan sebagai `HttpResponse` dengan `Content-Type: application/json`. Objek model dan QuerySet tidak dapat dikirim langsung sebagai JSON karena merupakan objek Python dengan tipe seperti UUID dan datetime; serialization mengubahnya menjadi representasi yang dapat dipertukarkan, termasuk `model`, `pk`, dan `fields`. Untuk halaman `/experience/`, `show_experience` mengambil respons JSON dari fungsi tersebut, memanggil `serializers.deserialize`, mengambil `.object` setiap hasil, dan mengirim daftar objek ke template. Pemanggilan ini berlangsung di server tanpa HTTP tambahan. Deserialisasi tidak menyimpan ulang objek ke database; tujuannya memulihkan struktur data agar field dan properti seperti `is_ongoing` bisa dipakai saat rendering.

## AI Disclosure

Saya menggunakan **GPT** untuk memberi ide pendekatan dan referensi implementasi, memeriksa checklist, serta membantu debugging pada alur permission, role Editor, fitur star, migrasi, dan tes otomatis. Pada Tutorial 5, GPT juga membantu menyesuaikan contoh AJAX dengan field `problem` dan `solution`, meninjau perlindungan CSRF/XSS, serta memeriksa test endpoint. Pada tahap sebelumnya, saya juga menggunakan **Claude** untuk saran pendekatan dan debugging CSS serta model.

Saya tetap menentukan bagian portfolio yang dikembangkan, pembagian hak akses, desain antarmuka, isi konten, dan keputusan akhir implementasi. Seluruh perubahan saya tinjau dan sesuaikan dengan struktur project sebelum diuji dan di-commit.
