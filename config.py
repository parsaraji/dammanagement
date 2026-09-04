import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    env = os.environ.get('FLASK_ENV', 'development')
    secret = os.environ.get('SECRET_KEY')
    if env == 'production' and not secret:
        raise RuntimeError('SECRET_KEY environment variable must be set in production environment!')

    SECRET_KEY = secret or 'dev-secret-key-persian-livestock'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'farm.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads', 'animals')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit
