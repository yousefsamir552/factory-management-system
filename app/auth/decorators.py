from functools import wraps
from flask import session, redirect, url_for, flash

def require_permission(section_name, require_edit=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))

            role = session.get('role')

            # الـ Sudo له كامل الصلاحيات
            if role == 'sudo':
                return f(*args, **kwargs)

            # الـ Owner للمشاهدة فقط في كل الأقسام
            if role == 'owner':
                if require_edit:
                    return "عفواً، حساب المالك مخصص للمشاهدة والتقارير فقط.", 403
                return f(*args, **kwargs)

            # الموظفين Staff
            user_perms = session.get('permissions', {})
            # permissions تكون dictionary مثل: {'warehouse': 'edit', 'design': 'view'}
            
            section_perm = user_perms.get(section_name)

            if not section_perm:
                return "عفواً، لا تملك الصلاحية للوصول لهذا القسم.", 403

            if require_edit and section_perm != 'edit':
                return "عفواً، تملك صلاحية المشاهدة فقط لهذا القسم ولا يمكنك التعديل أو الإضافة.", 403

            return f(*args, **kwargs)
        return decorator
    return decorator