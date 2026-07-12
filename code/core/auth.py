import jwt
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from ninja.security import HttpBearer

SECRET_KEY = settings.SECRET_KEY

def generate_tokens(user):
    """Membuat token berpasangan: access dan refresh"""
    # Mengambil role dari extend profile user (jika ada), default ke student
    role = getattr(user, 'profile').role if hasattr(user, 'profile') else 'student'
    
    access_payload = {
        'user_id': user.id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }
    refresh_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm='HS256')
    
    return access_token, refresh_token

class JWTAuth(HttpBearer):
    """Middleware otomatis dari Django Ninja untuk memproteksi API"""
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            # Menyuntikkan attribute role ke objek user agar bisa dibaca decorator RBAC
            user.role = payload.get('role', 'student')
            return user
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            return None