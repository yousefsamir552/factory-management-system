import json
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash
from app.models import db, Supplier, SizeDef, PrintShop, User, AuditLog
from datetime import datetime
from app.models import log_action

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
def index():
    if session.get('role') != 'sudo':
        return "غير مصرح لك بالوصول للإعدادات", 403

    suppliers = Supplier.query.all()
    sizes = SizeDef.query.all()
    printshops = PrintShop.query.all()
    
    # تحويل الصلاحيات من النص المخزن في الداتابيز لـ JSON لسهولة العرض
    users = User.query.filter_by(is_deleted=False).all()
    for u in users:
        try:
            u.parsed_perms = json.loads(u.permissions) if u.permissions else {}
        except:
            u.parsed_perms = {}

    return render_template('settings/index.html', suppliers=suppliers, sizes=sizes, printshops=printshops, users=users)

@settings_bp.route('/add_user', methods=['POST'])
def add_user():
    if session.get('role') != 'sudo':
        return "غير مصرح", 403

    real_name = request.form.get('real_name')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    # تجميع الصلاحيات بصيغة JSON { "warehouse": "edit", "design": "view" }
    perms_dict = {}
    sections = ['warehouse', 'design', 'cutting', 'qc']
    
    if role == 'staff':
        for sec in sections:
            perm_type = request.form.get(f'perm_{sec}') # view, edit, or None
            if perm_type:
                perms_dict[sec] = perm_type

    new_user = User(
        real_name=real_name,
        username=username,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        role=role,
        permissions=json.dumps(perms_dict)
    )
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('settings.index'))

@settings_bp.route('/edit_user_permissions/<int:user_id>', methods=['POST'])
def edit_user_permissions(user_id):
    if session.get('role') != 'sudo':
        return "غير مصرح", 403

    user = User.query.get_or_404(user_id)
    sections = ['warehouse', 'design', 'cutting', 'qc']
    perms_dict = {}

    for sec in sections:
        perm_type = request.form.get(f'perm_{sec}')
        if perm_type:
            perms_dict[sec] = perm_type

    user.permissions = json.dumps(perms_dict)
    db.session.commit()

    return redirect(url_for('settings.index'))

@settings_bp.route('/logs')
def view_logs():
    if session.get('role') not in ['sudo', 'owner']:
        return "غير مصرح لك بالدخول لسجلات المراقبة.", 403

    query = AuditLog.query

    user_id = request.args.get('user_id', type=int)
    if user_id:
        query = query.filter_by(user_id=user_id)

    action = request.args.get('action')
    if action:
        query = query.filter(AuditLog.action.contains(action))

    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if date_from:
        query = query.filter(AuditLog.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(AuditLog.timestamp <= datetime.strptime(date_to + " 23:59:59", '%Y-%m-%d %H:%M:%S'))

    logs = query.order_by(AuditLog.timestamp.desc()).limit(300).all()
    users = User.query.all()

    return render_template('settings/logs.html', logs=logs, users=users)

@settings_bp.route('/add_supplier', methods=['POST'])
def add_supplier():
    name = request.form.get('name')
    phone = request.form.get('phone')
    if name and not Supplier.query.filter_by(name=name).first():
        db.session.add(Supplier(name=name, phone=phone))
        db.session.commit()
    return redirect(url_for('settings.index'))

@settings_bp.route('/add_size', methods=['POST'])
def add_size():
    name = request.form.get('name')
    if name and not SizeDef.query.filter_by(name=name).first():
        db.session.add(SizeDef(name=name))
        db.session.commit()
    return redirect(url_for('settings.index'))

@settings_bp.route('/add_printshop', methods=['POST'])
def add_printshop():
    name = request.form.get('name')
    if name and not PrintShop.query.filter_by(name=name).first():
        db.session.add(PrintShop(name=name))
        db.session.commit()
    return redirect(url_for('settings.index'))

@settings_bp.route('/toggle_active/<int:user_id>')
def toggle_active(user_id):
    if session.get('role') != 'sudo':
        return "غير مصرح", 403
        
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'تفعيل' if user.is_active else 'إيقاف'
    log_action("تعديل حساب", f"تم {status} حساب الموظف {user.username}")
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/change_pass/<int:user_id>', methods=['POST'])
def change_pass(user_id):
    if session.get('role') != 'sudo':
        return "غير مصرح", 403
        
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    
    user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    
    log_action("تعديل حساب", f"تم تغيير باسورد حساب الموظف {user.username}")
    
    return redirect(url_for('settings.index'))