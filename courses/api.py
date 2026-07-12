from ninja import Router
from ninja.errors import HttpError
from typing import List
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Course
from .schemas import CourseIn, CourseOut
from core.auth import JWTAuth
from core.permissions import is_instructor, is_admin

router = Router(tags=["Courses"])

# ==================== 1. PUBLIC ENDPOINTS (Modul 6) ====================

@router.get("/", response=List[CourseOut])
def list_courses(request, search: str = None, min_price: int = None, max_price: int = None):
    """Mengambil daftar course dengan filter opsional (Optimasi Modul 5)"""
    qs = Course.objects.select_related('teacher').all()
    if search:
        qs = qs.filter(name__icontains=search)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    return qs

@router.get("/{int:id}", response=CourseOut)
def get_course_detail(request, id: int):
    """Mengambil detail satu course spesifik"""
    return get_object_or_404(Course.objects.select_related('teacher'), pk=id)


# ==================== 2. PROTECTED ENDPOINTS (Modul 7 / Progress 3) ====================

@router.post("/", auth=JWTAuth(), response={201: CourseOut})
@is_instructor
def create_course(request, data: CourseIn):
    """Membuat course baru (Hanya untuk Instructor)"""
    course = Course.objects.create(
        name=data.name,
        description=data.description,
        price=data.price,
        teacher=request.auth # Mengambil user dari token JWT
    )
    return 201, course

@router.patch("/{int:id}", auth=JWTAuth(), response=CourseOut)
def update_course(request, id: int, data: CourseIn):
    """Mengubah data course (Hanya untuk Pemilik/Instructor terkait)"""
    course = get_object_or_404(Course, pk=id)
    
    # Validasi kepemilikan (Ownership Validation)
    if course.teacher_id != request.auth.id:
        raise HttpError(403, "Anda bukan pemilik dari course ini!")
        
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    return course

@router.delete("/{int:id}", auth=JWTAuth(), response={204: None})
@is_admin
def delete_course(request, id: int):
    """Menghapus course dari sistem (Hanya untuk Admin)"""
    course = get_object_or_404(Course, pk=id)
    course.delete()
    return 204, None