from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from app.models import db, User, get_egypt_time

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if not user.is_active:
                return render_template('auth/login.html', error="تم إيقاف هذا الحساب، راجع الإدارة.")
            session['user_id'] = user.id
            session['username'] = user.username
            session['real_name'] = user.real_name
            session['role'] = user.role
            
            # قراءة الصلاحيات بتنسيق dict
            try:
                session['permissions'] = json.loads(user.permissions) if user.permissions else {}
            except:
                session['permissions'] = {}

            user.last_active = get_egypt_time()
            db.session.commit()

            return redirect(url_for('dashboard.index'))
        else:
            return render_template('auth/login.html', error="اسم المستخدم أو كلمة المرور غير صحيحة")

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/fix_sudo')
def fix_sudo():
    from werkzeug.security import generate_password_hash
    user = User.query.filter_by(username='sudo').first()
    if user:
        # إضافة خوارزمية التشفير المدعومة
        user.password = generate_password_hash('sudo123', method='pbkdf2:sha256')
        db.session.commit()
        return "تم إعادة ضبط وتشفير الباسورد بنجاح! ارجع اعمل لوجين دلوقتي."
    else:
        new_sudo = User(
            real_name='المبرمج (Sudo)',
            username='sudo',
            # إضافة خوارزمية التشفير المدعومة
            password=generate_password_hash('sudo123', method='pbkdf2:sha256'),
            role='sudo'
        )
        db.session.add(new_sudo)
        db.session.commit()
        return "تم إنشاء الحساب من جديد بنجاح! ارجع اعمل لوجين."