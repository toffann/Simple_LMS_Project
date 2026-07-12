"""
URL configuration untuk Simple LMS - Lab 05

Routes:
  /admin/       → Django Admin panel
  /silk/        → Django Silk profiling dashboard
  /             → Semua URL dari app courses (lihat courses/urls.py)
"""

from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from courses.api import router as courses_router
from core.auth_api import auth_router as auth_router
from courses.enrollment_api import enrollment_router

api = NinjaAPI(
    title="Simple LMS REST API",
    version="1.0.0",
    description="REST API dengan JWT Authentication dan RBAC"
)

api.add_router("/courses", courses_router)

api.add_router("/auth", auth_router)

api.add_router("/enrollments", enrollment_router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    path('api/', api.urls),
    path('', include('courses.urls')),
]