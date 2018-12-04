import os
from flask_uploads import IMAGES
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True 
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Blog]'
    FLASKY_MAIL_SENDER = '1771710969@qq.com'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    FLASKY_POSTS_PER_PAGE = 10
    FLASKY_COMMENTS_PER_PAGE = 5
    FLASKY_FOLLOWERS_PER_PAGE = 50
    DROPZONE_MAX_FILE_SIZE = 5
    DROPZONE_MAX_FILES = 30
    DROPZONE_ALLOWED_FILE_TYPE = 'image'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    AVATARS_SAVE_PATH = os.path.join(FLASKY_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)
    IMAGE_SAVE_PATH = os.path.join(FLASKY_UPLOAD_PATH, 'images') #文章图片保存
    PHOTO_SAVE_PATH = os.path.join(FLASKY_UPLOAD_PATH, 'photos') #flask_dropdown路径
    FLASKY_PHOTO_SIZE = {'small': 200, 'medium': 800}
    FLASKY_PHOTO_SUFFIX = {
        FLASKY_PHOTO_SIZE['small']: '_s',
        FLASKY_PHOTO_SIZE['medium']: '_m',
    }
    UPLOADED_PHOTOS_DEST = os.path.join(FLASKY_UPLOAD_PATH, 'photos') #flask_uploads 保存路径
    UPLOADED_PHOTOS_ALLOW = IMAGES


    
    @staticmethod
    def init_app(app):
        pass
        
class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    
class ProductionConfig(Config):
    SQLCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
        
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    
    'default': DevelopmentConfig
}
