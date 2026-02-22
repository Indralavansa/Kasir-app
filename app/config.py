# config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rahasia-sangat-rahasia-123456'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'instance' / 'kasir.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Backup settings
    BACKUP_DIR = BASE_DIR / 'backups'
    MAX_BACKUPS = 10
    
    # Security
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_DIGIT = True
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or ''
    # Telegram Chat IDs admin yang bisa akses bot (pisahkan dengan koma)
    TELEGRAM_ADMIN_CHAT_IDS = os.environ.get('TELEGRAM_ADMIN_CHAT_IDS') or ''
    TELEGRAM_NOTIFY_NEW_TRANSACTION = os.environ.get('TELEGRAM_NOTIFY_NEW_TRANSACTION', 'false').lower() == 'true'
    TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD = int(os.environ.get('TELEGRAM_NOTIFY_LOW_STOCK_THRESHOLD', '10'))