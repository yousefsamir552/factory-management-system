from flask import Blueprint, render_template, redirect, url_for, session
from app.models import User, DesignModel, FabricColor, get_egypt_time
from datetime import timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    total_models = DesignModel.query.count()
    total_fabrics = FabricColor.query.count()

    time_threshold = get_egypt_time() - timedelta(minutes=60)
    online_users = User.query.filter(User.last_active >= time_threshold).all()

    return render_template('dashboard/index.html',
                           total_models=total_models,
                           total_fabrics=total_fabrics,
                           online_users=online_users)