from functools import wraps
from flask import session, redirect, url_for

def require_permission(perm_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))

            role = session.get('role')

            if role == 'sudo':
                return f(*args, **kwargs)

            if role == 'owner':
                if 'edit' in perm_name or 'add' in perm_name or 'delete' in perm_name:
                    return "عفواً، حساب المالك مخصص للمشاهدة والتقارير فقط.", 403
                return f(*args, **kwargs)

            user_perms = session.get('permissions', [])
            if perm_name not in user_perms:
                return "عفواً، لا تملك الصلاحية الكافية للوصول لهذه الصفحة.", 403

            return f(*args, **kwargs)
        return decorator
    return decorator