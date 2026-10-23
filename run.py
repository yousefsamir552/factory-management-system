from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # تغيير المنفذ إلى 5001 لتجنب تعارض نظام الماك
    app.run(debug=True, port=5001)