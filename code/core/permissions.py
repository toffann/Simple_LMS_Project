from functools import wraps
from ninja.errors import HttpError

def has_role(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # request.auth otomatis berisi objek User berkat middleware HttpBearer
            if not request.auth:
                raise HttpError(401, "Kredensial tidak valid / Belum login")
            
            if request.auth.role not in allowed_roles:
                raise HttpError(403, "Anda tidak memiliki izin (Forbidden)")
                
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

# Shortcut untuk mempermudah pemanggilan kode di views/api
is_student = has_role(['student'])
is_instructor = has_role(['instructor'])
is_admin = has_role(['admin'])