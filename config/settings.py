# config/settings.py - 系统配置文件

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# Flask配置
class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # 文件上传配置
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    # 数据存储路径
    HISTORY_FOLDER = BASE_DIR / 'data' / 'history'
    RESOURCE_FOLDER = BASE_DIR / 'data' / 'resource'
    CHARTS_FOLDER = BASE_DIR / 'data' / 'charts'
    LOGS_FOLDER = BASE_DIR / 'logs'
    
    # 图表配置
    CHART_DPI = 100
    CHART_FORMAT = 'png'
    
    # 煤层识别参数
    COAL_DETECTION_PARAMS = {
        'resistivity_min': 50,
        'resistivity_max': 2000,
        'sonic_min': 300,
        'sonic_max': 600,
        'gamma_min': 20,
        'gamma_max': 80,
        'density_min': 1.0,
        'density_max': 1.8
    }
    
    # 污染评估参数
    POLLUTION_SEGMENT_SIZE = 10  # 米
    POLLUTION_THRESHOLDS = {
        'light': 15,
        'moderate': 35,
        'severe': 55,
        'critical': 75
    }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
