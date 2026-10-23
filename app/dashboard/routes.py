from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash
from app.models import db, User, DesignModel, FabricColor, AuditLog, get_egypt_time
from datetime import timedelta, datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    total_models = DesignModel.query.count()
    total_fabrics = FabricColor.query.count()

    time_threshold = get_egypt_time() - timedelta(minutes=60)
    online_users = User.query.filter(User.last_active >= time_threshold).all()
    all_users = User.query.all() if session.get('role') == 'sudo' else []

    return render_template('dashboard/index.html',
                           total_models=total_models,
                           total_fabrics=total_fabrics,
                           online_users=online_users,
                           all_users=all_users)

@dashboard_bp.route('/add_user', methods=['POST'])
def add_user():
    if session.get('role') != 'sudo':
        return "غير مصرح", 403

    real_name = request.form.get('real_name')
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    perms = request.form.getlist('permissions')
    permissions_str = ','.join(perms) if role == 'staff' else ''

    new_user = User(
        real_name=real_name,
        username=username,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        role=role,
        permissions=permissions_str
    )
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/logs')
def view_logs():
    if session.get('role') not in ['sudo', 'owner']:
        return "غير مصرح لك بالدخول لسجلات المراقبة.", 403

    query = AuditLog.query

    # الفلترة حسب المستخدم
    user_id = request.args.get('user_id', type=int)
    if user_id:
        query = query.filter_by(user_id=user_id)

    # الفلترة حسب قسم الإجراء
    action = request.args.get('action')
    if action:
        query = query.filter(AuditLog.action.contains(action))

    # الفلترة بالتاريخ
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if date_from:
        query = query.filter(AuditLog.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
    if date_to:
        query = query.filter(AuditLog.timestamp <= datetime.strptime(date_to + " 23:59:59", '%Y-%m-%d %H:%M:%S'))

    logs = query.order_by(AuditLog.timestamp.desc()).limit(300).all()
    users = User.query.all()

    return render_template('dashboard/logs.html', logs=logs, users=users)