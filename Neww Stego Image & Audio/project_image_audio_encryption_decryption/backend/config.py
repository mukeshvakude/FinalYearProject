"""
Application Configuration Module

Contains all configuration settings for the Flask application including
security, file handling, and encryption parameters.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with default settings."""
    
    # Flask Settings
    DEBUG = False
    TESTING = False
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload Settings
    UPLOAD_FOLDER = 'uploads'
    UPLOAD_AUDIO_FOLDER = 'upload_audio'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
    ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3'}
    
    # Encryption Settings
    ENCRYPTION_ALGORITHM = 'AES-256-CTR'
    KEY_DERIVATION = 'PBKDF2'
    
    # Fixed IV and Salt (for demo - should be random in production)
    # IV: 99114684525942506313644461257805955214848508590114620791139267598143401799819
    # Salt: b'$\xfb\x89\x1d\xb2\x08\x8f\x1b\xfa\xe49A`\xf9Z\xdc'
    
    # Security Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', '1234')  # Use strong key in production
    
    # Logging Settings
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/steganography.log'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Data Storage
    DATABASE_USERS = 'users.csv'
    DATABASE_SECRETS = 'secrets.csv'
    DATABASE_AUDIO_LOG = 'audio_log.csv'
    DATABASE_FACES = 'faces.csv'
    
    # Face Recognition Settings
    # ⚠ Note: face_recognition library requires dlib (complex to install on Windows)
    # If face_recognition is not available, set FACE_RECOGNITION_ENABLED = False
    FACE_RECOGNITION_ENABLED = True  # Temporarily disabled - install face_recognition library to enable
    FACE_RECOGNITION_MODEL = 'large'  # 'small' or 'large' (more accurate)
    FACE_RECOGNITION_TOLERANCE = 0.6  # Lower = stricter matching (0.0-1.0)
    FACE_RECOGNITION_K = 1  # Number of faces to recognize (1 = just match)
    FACE_UPLOAD_FOLDER = 'face_data'
    ALLOWED_FACE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
    MAX_FACE_FILE_SIZE = 5 * 1024 * 1024  # 5MB max face image size
    FACE_ENCODING_VERSION = '1.0'


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Requires HTTPS


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    TESTING = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=5)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration object based on environment.
    
    Args:
        env (str, optional): Environment name (development, production, testing)
    
    Returns:
        Config: Configuration class instance
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
