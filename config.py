import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # مفتاح الأمان (تم إعداده ليكون آمناً أو يعتمد على البيئة)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-change-it-later'
    # مسار قاعدة البيانات المحلي
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'factory.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False