"""
Views untuk Simple LMS - Lab 05: Optimasi Database

File ini dibagi menjadi 3 bagian:

  BAGIAN 1 - Views dengan N+1 Problem
    Gunakan Django Silk (http://localhost:8000/silk/) untuk mengamati
    jumlah query yang dihasilkan oleh setiap endpoint.

  BAGIAN 2 - Views Teroptimasi (Referensi Solusi)
    Bandingkan jumlah query di Silk setelah mengakses endpoint ini.

  BAGIAN 3 - Statistik
    Contoh penggunaan aggregate() untuk kalkulasi di level database.

Petunjuk Lab:
  1. Jalankan python manage.py seed_data untuk mengisi data
  2. Akses endpoint BAGIAN 1, amati jumlah query di Silk
  3. Coba optimalkan sendiri sebelum melihat BAGIAN 2
  4. Bandingkan hasilnya
"""

from django.db.models import Avg, Count, Max, Min, Prefetch
from django.http import JsonResponse

from .models import Comment, Course, CourseContent, CourseMember


# --- 1. CASE: Course + Teacher (ForeignKey) ---
def course_list_baseline(request):
    courses = Course.objects.all()
    data = []
    for c in courses:
        data.append({
            'course': c.name,
            'teacher': c.teacher.username, # Memicu N+1
        })
    return JsonResponse({'data': data})

def course_list_optimized(request):
    courses = Course.objects.select_related('teacher').all()
    data = []
    for c in courses:
        data.append({
            'course': c.name,
            'teacher': c.teacher.username,
        })
    return JsonResponse({'data': data})

# --- 2. CASE: Course + Member Count (Reverse ForeignKey) ---
def course_members_baseline(request):
    courses = Course.objects.all()
    data = []
    for c in courses:
        data.append({
            'course': c.name,
            'member_count': c.coursemember_set.count(), # Memicu N+1
        })
    return JsonResponse({'data': data})

def course_members_optimized(request):
    courses = Course.objects.prefetch_related('coursemember_set').all()
    data = []
    for c in courses:
        data.append({
            'course': c.name,
            'member_count': c.coursemember_set.count(),
        })
    return JsonResponse({'data': data})

# --- 3. CASE: Dashboard Statistics (Aggregate/Annotate) ---
def course_dashboard_baseline(request):
    courses = Course.objects.all()
    # Menghitung manual dalam loop (sangat tidak efisien)
    data = []
    for c in courses:
        data.append({'id': c.id, 'price': c.price})
    
    total_course = courses.count()
    avg_price = sum(c.price for c in courses) / total_course if total_course > 0 else 0
    
    return JsonResponse({
        'total': total_course,
        'avg_price': avg_price,
        'detail': data[:5] # Ambil 5 saja buat sampel
    })

def course_dashboard_optimized(request):
    stats = Course.objects.aggregate(
        total=Count('id'),
        avg_price=Avg('price')
    )
    return JsonResponse(stats)