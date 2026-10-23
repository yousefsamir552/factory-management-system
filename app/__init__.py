from flask import Flask
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        from app.auth.routes import auth_bp
        app.register_blueprint(auth_bp)

        from app.dashboard.routes import dashboard_bp
        app.register_blueprint(dashboard_bp)
        
        from app.warehouse.routes import warehouse_bp
        app.register_blueprint(warehouse_bp)

        from app.design.routes import design_bp
        app.register_blueprint(design_bp)

        # تسجيل القص والفرز والإعدادات
        from app.cutting.routes import cutting_bp
        app.register_blueprint(cutting_bp)

        from app.qc.routes import qc_bp
        app.register_blueprint(qc_bp)

        from app.settings.routes import settings_bp
        app.register_blueprint(settings_bp)

        @app.route('/')
        def home():
            from flask import redirect, url_for
            return redirect(url_for('dashboard.index'))

    return app