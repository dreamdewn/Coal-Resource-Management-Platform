# coal_analysis.py - 煤层分析相关功能
import numpy as np
import pandas as pd


def classify_coal_layer(data):
    """根据物理参数识别煤层"""
    coal_conditions = (
            (data['双侧向电阻率'] >= 50) & (data['双侧向电阻率'] <= 2000) &
            (data['声波时差'] >= 300) & (data['声波时差'] <= 600) &
            (data['自然伽玛'] >= 20) & (data['自然伽玛'] <= 80) &
            (data['密度'] >= 1.0) & (data['密度'] <= 1.8))
    return coal_conditions


def get_coal_depth_ranges(data, coal_mask):
    """计算煤层的深度范围"""
    coal_depths = data.loc[coal_mask, '深度']
    depth_ranges = []
    if not coal_depths.empty:
        current_start = coal_depths.iloc[0]
        current_end = coal_depths.iloc[0]
        for depth in coal_depths.iloc[1:]:
            if depth - current_end > 1:
                depth_ranges.append((current_start, current_end))
                current_start = depth
            current_end = depth
        depth_ranges.append((current_start, current_end))
    return depth_ranges


def process_data_file(filepath):
    """处理上传的数据文件，返回处理后的数据和煤层信息"""
    # 根据文件类型读取数据
    if filepath.endswith(('xlsx', 'xls')):
        data = pd.read_excel(filepath)
    else:  # 假设是CSV
        data = pd.read_csv(filepath)

        # 检查必要的列
    required_columns = ['深度', '深侧向', '浅侧向', '声波时差', '自然伽玛', '密度']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f'文件中缺少必要的列。请确保文件包含以下列：{", ".join(required_columns)}')

        # 计算双侧向电阻率
    data['双侧向电阻率'] = 0.7 * data['深侧向'] + 0.3 * data['浅侧向']

    # 识别煤层
    coal_mask = classify_coal_layer(data)
    coal_data = data.loc[coal_mask, ['深度', '声波时差', '自然伽玛', '双侧向电阻率', '密度']]

    # 获取煤层深度范围
    depth_ranges = get_coal_depth_ranges(data, coal_mask)
    formatted_ranges = [{'start': float(start), 'end': float(end),
                         'thickness': float(end - start)} for start, end in depth_ranges]

    # 计算总厚度
    total_thickness = sum(end - start for start, end in depth_ranges)

    # 准备返回数据
    indicators = ['深侧向', '浅侧向', '声波时差', '自然伽玛', '密度', '双侧向电阻率']
    chart_data = {
        'depth': data['深度'].tolist(),
        'indicators': {indicator: data[indicator].tolist() for indicator in indicators},
        'coal_layers': formatted_ranges,
        'total_thickness': float(total_thickness),
        'min_depth': float(data['深度'].min()),
        'max_depth': float(data['深度'].max())
    }

    return data, coal_mask, coal_data, chart_data