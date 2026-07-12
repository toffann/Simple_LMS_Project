from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from courses.schemas import LoginSchema, RegisterSchema, TokenSchema, UserOutSchema
from core.auth import generate_tokens, JWTAuth

auth_router = Router(tags=["Authentication"])

@auth_router.post("/register", response=UserOutSchema)
def register(request, data: RegisterSchema):
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username sudah digunakan")
    user = User.objects.create_user(username=data.username, email=data.email, password=data.password)
    # Set default role ke profile user (sesuaikan dengan model relasi profil kampusmu jika ada)
    user.role = data.role 
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}

@auth_router.post("/login", response=TokenSchema)
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if not user:
        raise HttpError(401, "Username atau password salah")
    access_token, refresh_token = generate_tokens(user)
    return {"access_token": access_token, "refresh_token": refresh_token}

@auth_router.get("/me", auth=JWTAuth(), response=UserOutSchema)
def get_me(request):
    user = request.auth
    return {"id": user.id, "username": user.username, "email": user.email, "role": getattr(user, 'role', 'student')}