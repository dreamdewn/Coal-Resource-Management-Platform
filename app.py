# app.py - 主应用程序和路由
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import json
import sys
from pathlib import Path
from werkzeug.utils import secure_filename
import numpy as np
from datetime import datetime
import matplotlib

matplotlib.use('Agg')  # 设置非交互式后端，避免服务器环境渲染问题

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入配置
from config.settings import config

# 导入自定义模块
from src.core.utils import allowed_file, set_chinese_font
from src.core.coal_analysis import process_data_file, classify_coal_layer, get_coal_depth_ranges
from src.core.pollution_assessment import assess_coal_pollution, generate_pollution_visualization
from src.core.resource_assessment import calculate_coal_resources, optimize_mining_plan, predict_resource_trend
from src.core.agriculture import assess_soil_quality, generate_reclamation_plan, recommend_agriculture

# 创建Flask应用实例
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取配置
current_config = config['default']()

# 应用配置
app.config['UPLOAD_FOLDER'] = str(current_config.UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = current_config.MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = current_config.SECRET_KEY

# 创建必要的目录
for folder in [current_config.UPLOAD_FOLDER, current_config.HISTORY_FOLDER, 
               current_config.RESOURCE_FOLDER, current_config.CHARTS_FOLDER, 
               current_config.LOGS_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

    # 缓存数据存储
data_cache = {}
pollution_history = {}
resource_data_cache = {}
extraction_history = {}
agriculture_history = {}


# 通用文件处理函数
def process_uploaded_file(file, location='未知位置', notes='', area=10000):
    """处理上传的文件并返回处理结果"""
    if not file or file.filename == '':
        return None, '没有选择文件', 400

    if not allowed_file(file.filename):
        return None, '不允许的文件类型', 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        data, coal_mask, coal_data, chart_data = process_data_file(filepath)
        return {
            'data': data,
            'coal_mask': coal_mask,
            'coal_data': coal_data,
            'chart_data': chart_data,
            'filename': filename,
            'location': location,
            'notes': notes,
            'area': float(area),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, None, 200
    except Exception as e:
        return None, f'处理文件时出错: {str(e)}', 500

    # 保存历史记录函数


def save_history(data, folder, prefix=''):
    """保存历史记录并返回键值"""
    history_key = f"{data['location']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    history_file = os.path.join(folder, f"{prefix}{history_key}.json")

    with open(history_file, 'w') as f:
        json.dump(data, f)

    return history_key


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400

    result, error, status = process_uploaded_file(request.files['file'])
    if error:
        return jsonify({'error': error}), status

        # 缓存数据，用于后续请求
    data_cache[result['filename']] = result['chart_data']
    return jsonify(result['chart_data']), 200


@app.route('/data/<filename>', methods=['GET'])
def get_data_range(filename):
    if filename not in data_cache:
        return jsonify({'error': '未找到数据，请先上传文件'}), 404

    start_depth = request.args.get('start', type=float)
    end_depth = request.args.get('end', type=float)
    chart_data = data_cache[filename]

    if start_depth is not None and end_depth is not None:
        # 根据深度范围过滤数据
        depth_arr = np.array(chart_data['depth'])
        mask = (depth_arr >= start_depth) & (depth_arr <= end_depth)

        filtered_data = {
            'depth': [float(d) for d in depth_arr[mask]],
            'indicators': {}
        }

        for indicator, values in chart_data['indicators'].items():
            values_arr = np.array(values)
            filtered_data['indicators'][indicator] = [float(v) for v in values_arr[mask]]

            # 保留必要的非过滤数据
        filtered_data['coal_layers'] = chart_data['coal_layers']
        filtered_data['total_thickness'] = chart_data['total_thickness']

        for key in ['pollution_assessment', 'ecological_assessment']:
            if key in chart_data:
                filtered_data[key] = chart_data[key]

        return jsonify(filtered_data), 200

    return jsonify(chart_data), 200


@app.route('/pollution-assessment', methods=['POST'])
def assess_pollution():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400

    location = request.form.get('location', '未知位置')
    notes = request.form.get('notes', '')

    result, error, status = process_uploaded_file(
        request.files['file'], location=location, notes=notes
    )
    if error:
        return jsonify({'error': error}), status

        # 评估煤污染
    pollution_assessment = assess_coal_pollution(result['data'], result['coal_mask'])
    visualization = generate_pollution_visualization(pollution_assessment)

    # 生成结果数据
    assessment_data = {
        'timestamp': result['timestamp'],
        'location': location,
        'notes': notes,
        'filename': result['filename'],
        'assessment': pollution_assessment,
        'visualization': visualization
    }

    # 保存历史记录
    history_key = save_history(assessment_data, str(current_config.HISTORY_FOLDER))

    # 更新历史记录缓存
    if location not in pollution_history:
        pollution_history[location] = []
    pollution_history[location].append({
        'key': history_key,
        'timestamp': result['timestamp'],
        'overall_score': pollution_assessment['overall_score'],
        'pollution_grade': pollution_assessment['pollution_grade']
    })

    return jsonify(assessment_data), 200


@app.route('/resource-assessment', methods=['POST'])
def assess_resources():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400

    location = request.form.get('location', '未知位置')
    area = float(request.form.get('area', 10000))
    notes = request.form.get('notes', '')

    result, error, status = process_uploaded_file(
        request.files['file'], location=location, notes=notes, area=area
    )
    if error:
        return jsonify({'error': error}), status

        # 计算资源储量
    resource_data = calculate_coal_resources(result['data'], result['coal_mask'], area)
    mining_plan = optimize_mining_plan(resource_data["layers"])

    # 生成结果数据
    assessment_data = {
        'timestamp': result['timestamp'],
        'location': location,
        'area': float(area),
        'notes': notes,
        'filename': result['filename'],
        'total_resources': resource_data["total_resources"],
        'total_volume': resource_data["total_volume"],
        'layers_count': len(resource_data["layers"]),
        'layers': resource_data["layers"],
        'mining_plan': mining_plan["mining_plan"],
        'priority_chart': mining_plan["priority_chart"]
    }

    # 保存历史记录
    resource_key = save_history(assessment_data, str(current_config.RESOURCE_FOLDER))

    # 更新历史记录缓存
    if location not in extraction_history:
        extraction_history[location] = []

    extraction_history[location].append({
        'key': resource_key,
        'timestamp': result['timestamp'],
        'total_resources': resource_data["total_resources"],
        'layers_count': len(resource_data["layers"])
    })

    # 预测资源趋势（如果有历史数据）
    if len(extraction_history[location]) >= 2:
        trend_data = predict_resource_trend(extraction_history[location])
        assessment_data['trend_data'] = trend_data

    return jsonify(assessment_data), 200


@app.route('/agriculture-assessment', methods=['POST'])
def agriculture_assessment():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分'}), 400

    location = request.form.get('location', '未知位置')
    area = float(request.form.get('area', 10000))
    notes = request.form.get('notes', '')
    assessment_type = request.form.get('type', 'both')  # 'reclamation', 'agriculture', 'both'

    result, error, status = process_uploaded_file(
        request.files['file'], location=location, notes=notes, area=area
    )
    if error:
        return jsonify({'error': error}), status

        # 评估土壤质量
    soil_quality = assess_soil_quality(result['data'], result['coal_mask'])

    # 生成结果
    assessment_data = {
        'timestamp': result['timestamp'],
        'location': location,
        'area': float(area),
        'notes': notes,
        'filename': result['filename'],
        'soil_quality': soil_quality
    }

    # 根据评估类型生成建议
    if assessment_type in ['reclamation', 'both']:
        assessment_data['reclamation_plan'] = generate_reclamation_plan(soil_quality)

    if assessment_type in ['agriculture', 'both']:
        assessment_data['agriculture_recommendation'] = recommend_agriculture(soil_quality)

        # 保存历史记录
    agriculture_key = save_history(assessment_data, str(current_config.RESOURCE_FOLDER), prefix='agri_')

    # 更新历史记录缓存
    if location not in agriculture_history:
        agriculture_history[location] = []

    agriculture_history[location].append({
        'key': agriculture_key,
        'timestamp': result['timestamp'],
        'location': location,
        'soil_type': soil_quality['soil_type'],
        'fertility_score': soil_quality['fertility_score'],
        'pollution_level': soil_quality['pollution_level']['level']
    })

    return jsonify(assessment_data), 200


# 历史记录处理函数
def get_history(history_dict, location=None):
    """获取历史记录"""
    if location and location in history_dict:
        return jsonify(history_dict[location]), 200

        # 返回所有位置的最新记录
    latest_records = {}
    for loc, records in history_dict.items():
        if records:
            latest_records[loc] = sorted(records, key=lambda x: x['timestamp'], reverse=True)[0]

    return jsonify(latest_records), 200


# 历史记录获取路由
@app.route('/pollution-history', methods=['GET'])
def get_pollution_history():
    return get_history(pollution_history, request.args.get('location'))


@app.route('/resource-history', methods=['GET'])
def get_resource_history():
    return get_history(extraction_history, request.args.get('location'))


@app.route('/agriculture-history', methods=['GET'])
def get_agriculture_history():
    return get_history(agriculture_history, request.args.get('location'))


# 历史记录详情获取函数
def get_history_detail(folder, key, prefix=''):
    """获取历史记录详情"""
    history_file = os.path.join(folder, f"{prefix}{key}.json")

    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            return jsonify(json.load(f)), 200

    return jsonify({'error': '未找到历史记录'}), 404


# 历史记录详情路由
@app.route('/pollution-history/<history_key>', methods=['GET'])
def get_pollution_detail(history_key):
    return get_history_detail(str(current_config.HISTORY_FOLDER), history_key)


@app.route('/resource-history/<resource_key>', methods=['GET'])
def get_resource_detail(resource_key):
    return get_history_detail(str(current_config.RESOURCE_FOLDER), resource_key)


@app.route('/agriculture-history/<agriculture_key>', methods=['GET'])
def get_agriculture_detail(agriculture_key):
    return get_history_detail(str(current_config.RESOURCE_FOLDER), agriculture_key, prefix='agri_')


# 页面路由
@app.route('/')
def serve_frontend():
    return send_from_directory('src/templates/pages', 'index.html')


@app.route('/<page>')
def serve_page(page):
    if page in ['pollution', 'resource', 'agriculture']:
        return send_from_directory('src/templates/pages', f'{page}.html')
    return send_from_directory('src/templates/pages', page)


# 运行应用
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)