from ninja import Router
from ninja.errors import HttpError
from typing import List
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from pymongo import MongoClient
from ratelimit.decorators import ratelimit
from ratelimit.exceptions import Ratelimited

from .models import Course
from .schemas import CourseIn, CourseOut
from core.auth import JWTAuth
from core.permissions import is_instructor, is_admin

router = Router(tags=["Courses"])

def log_to_mongo(user_id, action, details):
    client = MongoClient(settings.MONGODB_URI)
    db = client['lms_analytics']
    db.activity_logs.insert_one({
        "user_id": user_id,
        "action": action,
        "details": details
    })

# ==================== 1. PUBLIC ENDPOINTS ====================

@router.get("/", response=List[CourseOut])
def list_courses(request, search: str = None, min_price: int = None, max_price: int = None):
    # Rate Limiting: 60 request per menit berdasarkan IP
    # Karena django-ninja menggunakan class-based routing di bawah kap, manual check bisa dipakai:
    was_limited = ratelimit(key='ip', rate='60/m', block=False)(lambda r: None)(request)
    if getattr(request, 'limited', False):
        raise HttpError(429, "Rate limit exceeded. Maksimal 60 request per menit.")

    # Redis Cache Pattern untuk Course List
    cache_key = f"course_list_{search}_{min_price}_{max_price}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data

    qs = Course.objects.select_related('teacher').all()
    if search:
        qs = qs.filter(name__icontains=search)
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    
    # Simpan ke cache selama 15 menit (900 detik)
    cache.set(cache_key, list(qs), 900)
    return qs

@router.get("/{int:id}", response=CourseOut)
def get_course_detail(request, id: int):
    was_limited = ratelimit(key='ip', rate='60/m', block=False)(lambda r: None)(request)
    if getattr(request, 'limited', False):
        raise HttpError(429, "Rate limit exceeded.")

    # Redis Cache Pattern untuk Course Detail
    cache_key = f"course_detail_{id}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data

    course = get_object_or_404(Course.objects.select_related('teacher'), pk=id)
    cache.set(cache_key, course, 900)
    return course

# ==================== 2. PROTECTED ENDPOINTS ====================

@router.post("/", auth=JWTAuth(), response={201: CourseOut})
@is_instructor
def create_course(request, data: CourseIn):
    course = Course.objects.create(
        name=data.name,
        description=data.description,
        price=data.price,
        teacher=request.auth
    )
    
    # Invalidation Strategy: Hapus semua cache list saat ada data baru
    cache.clear()
    
    log_to_mongo(request.auth.id, "CREATE_COURSE", {"course_id": course.id, "name": course.name})
    return 201, course

@router.patch("/{int:id}", auth=JWTAuth(), response=CourseOut)
def update_course(request, id: int, data: CourseIn):
    course = get_object_or_404(Course, pk=id)
    
    if course.teacher_id != request.auth.id:
        raise HttpError(403, "Anda bukan pemilik dari course ini!")
        
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    
    # Invalidation Strategy: Hapus cache spesifik dan list data
    cache.delete(f"course_detail_{id}")
    cache.clear()
    
    log_to_mongo(request.auth.id, "UPDATE_COURSE", {"course_id": id})
    return course

@router.delete("/{int:id}", auth=JWTAuth(), response={204: None})
@is_admin
def delete_course(request, id: int):
    course = get_object_or_404(Course, pk=id)
    course.delete()
    
    # Invalidation Strategy
    cache.delete(f"course_detail_{id}")
    cache.clear()
    
    log_to_mongo(request.auth.id, "DELETE_COURSE", {"course_id": id})
    return 204, None