import csv
from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import Course
from pymongo import MongoClient
from django.conf import settings

def get_mongo_db():
    client = MongoClient(settings.MONGODB_URI)
    return client['lms_analytics']

@shared_task
def send_enrollment_email(student_id, course_id):
    try:
        student = User.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        
        subject = f"Selamat Datang di Kelas {course.name}"
        message = f"Halo {student.username},\n\nKamu berhasil terdaftar pada kelas {course.name}."
        
        send_mail(
            subject,
            message,
            'noreply@lms.com',
            [student.email],
            fail_silently=False,
        )
        return f"Email sent to {student.email}"
    except Exception as e:
        return str(e)

@shared_task
def generate_certificate(student_id, course_id):
    # Logic mock-up pembuatan sertifikat kelulusan
    db = get_mongo_db()
    db.learning_analytics.insert_one({
        "student_id": student_id,
        "course_id": course_id,
        "event": "certificate_generated"
    })
    return f"Certificate generated for student {student_id} in course {course_id}"

@shared_task
def update_course_statistics():
    # Menghitung ulang jumlah enrollment aktif
    courses = Course.objects.all()
    updated_count = 0
    for course in courses:
        # Menghitung relasi student (asumsi nama field/relasi M2M M6 & M7 adalah students)
        count = course.students.count() if hasattr(course, 'students') else 0
        
        db = get_mongo_db()
        db.course_reports.update_one(
            {"course_id": course.id},
            {"$set": {"name": course.name, "total_enrollments": count}},
            upsert=True
        )
        updated_count += 1
    return f"Statistics updated for {updated_count} courses"

@shared_task
def export_course_report():
    courses = Course.objects.all()
    file_path = '/code/media/course_report.csv'
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Nama Kelas', 'Harga'])
        for course in courses:
            writer.writerow([course.id, course.name, course.price])
            
    return f"Report exported successfully to {file_path}"