# resource_assessment.py - 煤炭资源评估和开采规划相关功能
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 设置非交互式后端，解决服务器环境下的渲染问题
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from functools import lru_cache
from typing import Dict, List, Tuple, Optional, Any, Union
from utils import set_chinese_font, plot_to_base64
from coal_analysis import get_coal_depth_ranges

# 常量定义
# 煤炭品质评估常量
QUALITY_THRESHOLDS = {
    "特优": 90,
    "优质": 75,
    "良好": 60,
    "中等": 45,
    "低质": 0
}

# 开采难度评估常量
DIFFICULTY_THRESHOLDS = {
    "容易": 3,
    "中等": 5,
    "困难": 7,
    "极困难": 10
}

# 开采方法回收率因子
METHOD_FACTORS = {
    "露天开采": 1.2,
    "长壁开采": 1.1,
    "分层开采": 1.0,
    "窄煤柱开采": 0.9,
    "水力开采": 0.8,
    "房柱式开采": 0.85
}


def calculate_coal_resources(data: pd.DataFrame, coal_mask: pd.Series, area_square_meters: float = 10000) -> Dict:
    """
    计算煤炭资源储量

    Args:
        data: 包含钻孔测量数据的DataFrame
        coal_mask: 标识煤层位置的布尔掩码
        area_square_meters: 煤层面积(平方米)

    Returns:
        包含资源量计算结果的字典
    """
    coal_data = data[coal_mask]

    if coal_data.empty:
        return {"total_resources": 0, "layers": [], "total_volume": 0, "area_square_meters": area_square_meters}

        # 计算每个煤层的资源情况
    depth_ranges = get_coal_depth_ranges(data, coal_mask)
    coal_layers = []
    total_volume = 0

    for i, (start, end) in enumerate(depth_ranges):
        thickness = end - start
        # 获取该煤层内的煤炭数据
        layer_data = data[(data['深度'] >= start) & (data['深度'] <= end)]

        # 计算煤层体积和质量
        layer_volume = thickness * area_square_meters
        avg_density = layer_data['密度'].mean()
        layer_mass = layer_volume * avg_density * 1000  # 转换为吨

        # 煤层品质评估
        quality_score = assess_coal_quality(layer_data)

        # 计算开采难度
        mining_difficulty = assess_mining_difficulty(start, end, thickness)

        coal_layers.append({
            "layer_number": i + 1,
            "start_depth": float(start),
            "end_depth": float(end),
            "thickness": float(thickness),
            "volume": float(layer_volume),
            "density": float(avg_density),
            "mass_tons": float(layer_mass),
            "quality": quality_score,
            "mining_difficulty": mining_difficulty
        })

        total_volume += layer_volume

        # 计算总储量
    avg_density = coal_data['密度'].mean()
    total_resources = total_volume * avg_density * 1000  # 转换为吨

    return {
        "total_resources": float(total_resources),
        "layers": coal_layers,
        "total_volume": float(total_volume),
        "area_square_meters": float(area_square_meters)
    }


def assess_coal_quality(layer_data: pd.DataFrame) -> Dict:
    """
    评估煤炭品质

    Args:
        layer_data: 煤层数据

    Returns:
        包含品质评估结果的字典
    """
    avg_density = layer_data['密度'].mean()
    avg_gamma = layer_data['自然伽玛'].mean()

    # 密度评分：1.1-1.8范围内，密度越低分数越高
    density_score = max(0, min(100, (1.8 - avg_density) / 0.7 * 100))

    # 伽马评分：20-80范围内，伽马值越低分数越高
    gamma_score = max(0, min(100, (80 - avg_gamma) / 60 * 100))

    # 总体品质评分（0-100）
    quality_score = 0.6 * density_score + 0.4 * gamma_score

    # 确定品质等级
    quality_grade = "低质"  # 默认值
    for grade, threshold in QUALITY_THRESHOLDS.items():
        if quality_score >= threshold:
            quality_grade = grade
            break

    return {
        "score": float(quality_score),
        "grade": quality_grade,
        "density": float(avg_density),
        "gamma": float(avg_gamma)
    }


def assess_mining_difficulty(start_depth: float, end_depth: float, thickness: float) -> Dict:
    """
    评估开采难度

    Args:
        start_depth: 煤层起始深度
        end_depth: 煤层结束深度
        thickness: 煤层厚度

    Returns:
        包含开采难度评估结果的字典
    """
    avg_depth = (start_depth + end_depth) / 2

    # 深度因子：深度越大，开采难度越大
    depth_factor = min(10, avg_depth / 100)

    # 厚度因子：煤层过薄或过厚都会增加开采难度
    thickness_factor_map = {
        (0, 1): 8,  # <1m: 很难
        (1, 2): 5,  # 1-2m: 较难
        (2, 5): 2,  # 2-5m: 理想
        (5, 8): 4,  # 5-8m: 较难
        (8, float('inf')): 6  # >8m: 难
    }

    thickness_factor = next(factor for (lower, upper), factor in thickness_factor_map.items()
                            if lower <= thickness < upper)

    # 计算总难度（1-10分）
    difficulty_score = (depth_factor * 0.7 + thickness_factor * 0.3)

    # 确定难度等级
    difficulty_grade = "极困难"  # 默认值
    for grade, threshold in DIFFICULTY_THRESHOLDS.items():
        if difficulty_score < threshold:
            difficulty_grade = grade
            break

    return {
        "score": float(difficulty_score),
        "grade": difficulty_grade,
        "depth_factor": float(depth_factor),
        "thickness_factor": float(thickness_factor)
    }


def determine_mining_method(layer: Dict) -> Dict:
    """
    基于煤层特性确定开采方法

    Args:
        layer: 煤层数据字典

    Returns:
        推荐的开采方法
    """
    depth = layer["start_depth"]
    thickness = layer["thickness"]

    # 决策逻辑
    if depth < 50 and thickness > 2:
        method = "露天开采"
        description = "适用于浅层且较厚的煤层，成本低，回收率高。"
    elif 50 <= depth < 300 and 1.5 <= thickness <= 8:
        method = "长壁开采"
        description = "适用于中等深度、厚度适中的煤层，产量高，安全性好。"
    elif 100 <= depth < 600 and thickness > 6:
        method = "分层开采"
        description = "适用于中深度、较厚的煤层，可分批次开采，提高安全性。"
    elif thickness < 1.5:
        method = "窄煤柱开采"
        description = "适用于薄煤层，可提高回收率，但成本较高。"
    elif depth >= 600:
        method = "水力开采"
        description = "适用于深层煤层，通过高压水冲击煤层，安全性较高但成本高。"
    else:
        method = "房柱式开采"
        description = "通用性强的开采方法，适应性好，但回收率较低。"

    return {
        "name": method,
        "description": description
    }


def calculate_recovery_rate(layer: Dict, method: Dict, base_rate: float = 0.85) -> float:
    """
    计算预期回收率

    Args:
        layer: 煤层数据
        method: 开采方法
        base_rate: 基础回收率

    Returns:
        预期回收率(0-1之间的小数)
    """
    difficulty = layer["mining_difficulty"]["score"]

    # 基于开采方法调整回收率
    method_factor = METHOD_FACTORS.get(method["name"], 1.0)

    # 基于难度调整回收率
    difficulty_factor = max(0.7, 1 - difficulty * 0.03)

    # 计算最终回收率，但不超过95%
    recovery_rate = min(0.95, base_rate * method_factor * difficulty_factor)

    return recovery_rate


def _create_priority_chart(layer_numbers: List[str], qualities: List[float],
                           difficulties: List[float], priorities: List[float]) -> str:
    """创建优先级分析图表"""
    set_chinese_font()

    x = np.arange(len(layer_numbers))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(x - width, qualities, width, label='品质得分', color='#4CAF50')
    ax.bar(x, difficulties, width, label='开采难度', color='#F44336')
    ax.bar(x + width, priorities, width, label='优先级指数', color='#2196F3')

    ax.set_title('煤层开采优先级分析')
    ax.set_ylabel('得分')
    ax.set_xticks(x)
    ax.set_xticklabels(layer_numbers)
    ax.legend()

    plt.tight_layout()
    return plot_to_base64(fig)


def optimize_mining_plan(coal_layers: List[Dict], extraction_rate: float = 0.85) -> Dict:
    """
    优化开采顺序和方法

    Args:
        coal_layers: 煤层数据列表
        extraction_rate: 提取率

    Returns:
        优化的开采规划
    """
    # 准备数据
    layers = sorted(coal_layers, key=lambda x: x["start_depth"])
    layer_numbers = [f"煤层{l['layer_number']}" for l in layers]
    qualities = [l["quality"]["score"] for l in layers]
    difficulties = [l["mining_difficulty"]["score"] * 10 for l in layers]  # 缩放为0-100
    resources = [l["mass_tons"] / 1000 for l in layers]  # 转换为千吨

    # 计算优先级得分 = 品质 * 0.5 + (100-难度) * 0.3 + 储量占比 * 0.2
    max_resource = max(resources) if resources else 1
    priorities = []
    for i in range(len(layers)):
        resource_factor = resources[i] / max_resource * 100
        priority = qualities[i] * 0.5 + (100 - difficulties[i]) * 0.3 + resource_factor * 0.2
        priorities.append(priority)

        # 排序并生成开采顺序建议
    combined_data = list(zip(layer_numbers, qualities, difficulties, resources, priorities, layers))
    ordered_layers = sorted(combined_data, key=lambda x: x[4], reverse=True)

    mining_plan = []
    for i, (name, quality, difficulty, resource, priority, layer) in enumerate(ordered_layers):
        # 计算最佳开采方法
        method = determine_mining_method(layer)

        # 计算预期回收率
        recovery_rate = calculate_recovery_rate(layer, method, extraction_rate)

        # 预期产量
        expected_output = layer["mass_tons"] * recovery_rate

        mining_plan.append({
            "order": i + 1,
            "layer": layer["layer_number"],
            "depth_range": f"{layer['start_depth']:.1f}m - {layer['end_depth']:.1f}m",
            "quality_score": float(quality),
            "difficulty_score": float(difficulty / 10),  # 转回1-10分
            "resource_ktons": float(resource),
            "priority_score": float(priority),
            "recommended_method": method["name"],
            "method_details": method["description"],
            "expected_recovery_rate": float(recovery_rate * 100),  # 百分比
            "expected_output_tons": float(expected_output)
        })

        # 绘制优先级分析图表
    plot_data = _create_priority_chart(layer_numbers, qualities, difficulties, priorities)

    return {
        "mining_plan": mining_plan,
        "priority_chart": plot_data
    }


def predict_resource_trend(resource_history: List[Dict]) -> Optional[Dict]:
    """
    基于历史数据预测未来储量变化趋势

    Args:
        resource_history: 资源历史记录列表

    Returns:
        趋势预测结果，如果数据不足则返回None
    """
    if len(resource_history) < 2:
        return None

        # 设置中文字体
    set_chinese_font()

    # 创建数据框处理时间序列
    df = pd.DataFrame([
        {"date": datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S"),
         "resources": record["total_resources"]}
        for record in resource_history
    ])

    # 计算起始日期以来的天数
    df['days'] = (df['date'] - df['date'].min()).dt.days

    # 准备建模数据
    X = df['days'].values.reshape(-1, 1)
    y = df['resources'].values

    # 线性回归预测
    model = LinearRegression()
    model.fit(X, y)

    # 预测未来180天的资源趋势
    future_days = np.array(list(range(0, 180, 30))).reshape(-1, 1)
    predicted_resources = model.predict(future_days)

    # 计算枯竭日期（如果有消耗趋势）
    depletion_date = None
    if model.coef_[0] < 0:  # 如果斜率为负（储量在减少）
        days_to_depletion = -y[-1] / model.coef_[0]
        last_date = df['date'].iloc[-1]
        depletion_date = (last_date + timedelta(days=float(days_to_depletion))).strftime("%Y-%m-%d")

        # 生成趋势图
    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, color='blue', label='历史数据')
    plt.plot(future_days, predicted_resources, color='red', linestyle='--', label='预测趋势')
    plt.title('煤炭资源储量变化趋势')
    plt.xlabel('时间（天）')
    plt.ylabel('储量（吨）')
    plt.legend()
    plt.grid(True)

    # 将图表转换为base64编码
    fig = plt.gcf()
    trend_chart = plot_to_base64(fig)

    return {
        "model_slope": float(model.coef_[0]),
        "model_intercept": float(model.intercept_),
        "predicted_values": [float(x) for x in predicted_resources.tolist()],
        "prediction_days": [int(x[0]) for x in future_days.tolist()],
        "trend_chart": trend_chart,
        "depletion_date": depletion_date
    }