from ninja import Router
from ninja.errors import HttpError
from typing import List
from django.shortcuts import get_object_or_404
from .models import Course  # Sesuaikan jika ada model Enrollment tersendiri di project-mu
from core.auth import JWTAuth
from core.permissions import is_student

enrollment_router = Router(tags=["Enrollments"])

@enrollment_router.post("/", auth=JWTAuth())
@is_student
def enroll_course(request, course_id: int):
    """Enroll ke kelas baru (Hanya untuk Student)"""
    course = get_object_or_404(Course, id=course_id)
    # Tulis logic menyimpan relasi student ke course di sini (misal: course.students.add(request.auth))
    return {"success": True, "message": f"Berhasil mendaftar di kelas {course.name}"}

@enrollment_router.get("/my-courses", auth=JWTAuth())
@is_student
def my_courses(request):
    """Melihat daftar kelas yang diikuti oleh student aktif"""
    # Contoh logic penarikan data kelas student
    return {"student": request.auth.username, "enrolled_courses": []}

@enrollment_router.post("/{int:id}/progress", auth=JWTAuth())
@is_student
def mark_lesson_complete(request, id: int):
    """Menandai materi/konten tertentu selesai"""
    return {"success": True, "message": f"Materi dengan ID {id} selesai dibaca"}