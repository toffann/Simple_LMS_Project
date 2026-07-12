# FINAL PROJECT REPORT

## 1. Identitas
* **Nama:** Toffan
* **NIM:** A11.2023.15195
* **Kelas:** Pemrograman Sisi Server (A11.54403)
* **URL Repository:** https://github.com/toffann/Simple_LMS_Project.git

---

## 2. Deskripsi Project
Project ini merupakan pengembangan lanjutan dari platform *Simple Learning Management System (LMS)* berbasis arsitektur REST API menggunakan framework Django Ninja dan PostgreSQL. Pada tahap final project ini, sistem ditingkatkan skalabilitas dan performanya menggunakan pendekatan *Polyglot Persistence* (kombinasi PostgreSQL dan MongoDB), mekanisme caching memory *Cache-Aside* dengan Redis, serta implementasi pemrosesan asinkron dan *scheduled tasks* memanfaatkan Celery dan RabbitMQ.

---

## 3. Fitur Dasar yang Sudah Berjalan
* **Authentication & Authorization:** JWT Authentication dengan pembagian Role-Based Access Control (RBAC) mencakup Admin, Instructor, dan Student.
* **Course Management API:** Endpoint CRUD untuk pengelolaan kelas (Course) dan materi (Lesson).
* **Enrollment & Progress Tracking:** Endpoint untuk pendaftaran kelas oleh mahasiswa serta tracking status penyelesaian materi secara real-time.
* **API Documentation:** Auto-generated interactive documentation melalui Swagger UI (`/api/docs#`).

---

## 4. Fitur Tambahan yang Dipilih
Melalui arsitektur Progress 4, berikut adalah rincian kalkulasi poin fitur tambahan pilihan yang diimplementasikan secara terintegrasi:

| No | Fitur Tambahan | Kategori | Poin | Status |
|---|---|---|---|---|
| 1 | Redis Caching untuk Course | D. Redis & Caching | 12 | Selesai |
| 2 | Cache Invalidation Strategy | D. Redis & Caching | 12 | Selesai |
| 3 | Activity Logging ke MongoDB | E. MongoDB & Analytics | 15 | Selesai |
| 4 | Learning Analytics Collection | E. MongoDB & Analytics | 15 | Selesai |
| 5 | Email Notification Async (Celery) | F. Celery & Async | 12 | Selesai |
| 6 | Generate Certificate/Report Async | F. Celery & Async | 18 | Selesai |
| 7 | Scheduled Task (Celery Beat) | F. Celery & Async | 15 | Selesai |
| 8 | Flower Monitoring | F. Celery & Async | 8 | Selesai |
| **Total** | **Akumulasi Poin Fitur Tambahan** | | **107 Poin** | *(Maks dihitung 50 poin)* |

---

## 5. Penjelasan Implementasi Fitur Tambahan Utama

### A. Mekanisme Caching (Redis)
Sistem menerapkan pola *Cache-Aside (Lazy Loading)* pada endpoint `GET /api/courses/` dan `GET /api/courses/{id}`. Data dibaca dari Redis RAM memory terlebih dahulu untuk memotong response time. Mekanisme *Proactive Cache Invalidation* dikonfigurasi pada method mutasi data (`POST`, `PUT`, `DELETE`) dengan memicu penghapusan cache key lama secara otomatis agar konsistensi data PostgreSQL dan Redis tetap terjaga.

### B. Asynchronous Workers (Celery & RabbitMQ)
Pemrosesan komputasi berat didelegasikan ke background worker menggunakan broker RabbitMQ dan Celery worker:
* **`send_enrollment_email` & `generate_certificate`:** Berjalan secara asinkron sesaat setelah transaksi database PostgreSQL berhasil, mempercepat siklus HTTP response time pada client side.
* **`update_course_statistics`:** Scheduled task menggunakan Celery Beat untuk melakukan agregasi query data secara periodik berkala.

### C. Big Data Analytics & Audit Trail (MongoDB)
Setiap event krusial pengguna (seperti pendaftaran kelas, login, dan penyelesaian modul belajar) dicatat ke dalam NoSQL document database MongoDB pada collection `learning_analytics` secara terpisah. Hal ini menjamin log audit trail aplikasi tidak membebani performa query transaksional pada database utama PostgreSQL.

---

## 6. Cara Menjalankan Project
1. Pastikan Docker dan Docker Desktop sudah aktif di background.
2. Clone repository dan masuk ke root folder proyek:
   ```bash
   git clone [https://github.com/toffann/Simple_LMS_Project.git](https://github.com/toffann/Simple_LMS_Project.git)
   cd Simple_LMS_Project

   1. Jalankan infrastruktur container menggunakan Docker Compose:

        docker-compose down
        docker-compose up -d --build

    2. Akses Swagger UI Dokumentasi API melalui browser pada alamat: http://localhost:8000/api/docs#

## 7. Akun Demo Pengujian
        Admin: admin@lms.com / admin123

        Instructor: instructor@lms.com / instructor123

        Student: student@lms.com / student123

## 8. Endpoint Penting untuk Diuji
POST /api/auth/login - Otentikasi dan perolehan token JWT.

GET /api/courses/ - Pengujian performa caching Redis (Cache-Aside pattern).

POST /api/enrollments/ - Triggering async background task kirim email lewat Celery.

POST /api/enrollments/{id}/progress - Pencatatan progres belajar terintegrasi asinkron log MongoDB.

## 9. Kendala Teknis dan Solusi
Kendala: Terjadi File Lock Concurrency Conflict pada environment sistem operasi Windows host ketika kontainer web (lms-app) dan Celery workers mencoba mengeksekusi instalasi dependensi library python secara bersamaan di startup.

Solusi: Menambahkan konfigurasi execution delay orchestration menggunakan perintah sleep terukur pada baris entrypoint command script di dalam file docker-compose.yml. Hal ini memisahkan waktu inisialisasi awal antar service kontainer backend sehingga seluruh kluster infrastruktur Docker dapat terangkat stabil tanpa bentrokan akses berkas.

## 10. Kesimpulan
Pengembangan Final Project ini memberikan pemahaman mendalam mengenai arsitektur backend moderen yang production-ready. Integrasi Redis, MongoDB, dan Celery terbukti memangkas latensi beban server secara signifikan dan memberikan fleksibilitas pengelolaan basis data berskala besar.