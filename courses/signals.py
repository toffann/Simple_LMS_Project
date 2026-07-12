from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Course
from .tasks import send_enrollment_email

@receiver(m2m_changed, sender=Course.students.through)
def trigger_enrollment_email(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for student_id in pk_set:
            send_enrollment_email.delay(student_id, instance.id)