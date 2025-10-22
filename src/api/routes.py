# src/api/routes.py - API路由定义

from flask import Blueprint, request, jsonify, send_from_directory
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.coal_analysis import process_data_file, classify_coal_layer, get_coal_depth_ranges
from src.core.pollution_assessment import assess_coal_pollution, generate_pollution_visualization
from src.core.resource_assessment import calculate_coal_resources, optimize_mining_plan, predict_resource_trend
from src.core.agriculture import assess_soil_quality, generate_reclamation_plan, recommend_agriculture
from src.core.utils import allowed_file, set_chinese_font
from config.settings import config

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# 获取配置
current_config = config['default']()

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不允许的文件类型'}), 400
    
    try:
        # 保存文件
        filename = file.filename
        filepath = os.path.join(current_config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 处理数据
        data, coal_mask, coal_data, chart_data = process_data_file(filepath)
        
        return jsonify({
            'status': 'success',
            'data': chart_data,
            'filename': filename
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'处理文件时出错: {str(e)}'}), 500

@api_bp.route('/analysis/coal', methods=['POST'])
def analyze_coal():
    """煤层分析接口"""
    # 实现煤层分析逻辑
    pass

@api_bp.route('/analysis/pollution', methods=['POST'])
def analyze_pollution():
    """污染分析接口"""
    # 实现污染分析逻辑
    pass

@api_bp.route('/analysis/resource', methods=['POST'])
def analyze_resource():
    """资源分析接口"""
    # 实现资源分析逻辑
    pass

@api_bp.route('/analysis/agriculture', methods=['POST'])
def analyze_agriculture():
    """农业分析接口"""
    # 实现农业分析逻辑
    pass

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': '2024-01-01T00:00:00Z'
    }), 200
