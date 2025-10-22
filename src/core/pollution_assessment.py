import numpy as np
import matplotlib

matplotlib.use('Agg')  # 设置非交互式后端，解决服务器环境下的渲染问题
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import os
import logging
from typing import Dict, List, Any
from io import BytesIO
import base64
from utils import set_chinese_font

# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pollution_assessment')


# 自定义安全图表转换函数
def safe_plot_to_base64(fig):
    """安全地将matplotlib图表转换为base64字符串"""
    try:
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)  # 释放资源
        return img_str
    except Exception as e:
        logger.error(f"图表转换失败: {str(e)}")
        plt.close(fig)  # 确保释放资源
        return ""


def assess_coal_pollution(data, coal_mask):
    """评估煤污染程度，基于多参数综合分析"""
    try:
        # 深度分段（每10米一段）
        depth_min = data['深度'].min()
        depth_max = data['深度'].max()
        segment_size = 10  # 10米一段

        segments = []
        avg_density_total = float(data['密度'].mean())  # 确保转换为Python原生类型

        for start in np.arange(depth_min, depth_max, segment_size):
            end = min(start + segment_size, depth_max)
            segment_data = data[(data['深度'] >= start) & (data['深度'] < end)]

            if len(segment_data) > 0:
                # 计算该段内煤层占比
                segment_coal = np.sum(coal_mask[segment_data.index])
                coal_percentage = segment_coal / len(segment_data)

                # 计算污染指数 - 基于综合物理特性和煤层状况
                if coal_percentage > 0:
                    # 获取物理参数
                    avg_density = float(segment_data['密度'].mean())
                    avg_gamma = float(segment_data['自然伽玛'].mean())

                    # 尝试获取电阻率，如果存在的话(可能列名有差异)
                    try:
                        resistivity = float(segment_data['双侧向电阻率'].mean())
                    except:
                        try:
                            resistivity = float(segment_data['电阻率'].mean())
                        except:
                            resistivity = 100.0  # 默认值

                    # 尝试获取声波时差，用于评估岩层结构
                    try:
                        sonic_dt = float(segment_data['声波时差'].mean())
                        porosity_factor = min(1.5, sonic_dt / 200)  # 孔隙度因子，声波时差越大，孔隙度越高
                    except:
                        porosity_factor = 1.0  # 默认值

                    # 计算周围岩层阻隔系数 (非煤层部分的密度和电阻率)
                    non_coal_data = segment_data[~coal_mask[segment_data.index]]
                    if len(non_coal_data) > 0:
                        rock_density = float(non_coal_data['密度'].mean())
                        try:
                            rock_resistivity = float(non_coal_data['双侧向电阻率'].mean())
                        except:
                            try:
                                rock_resistivity = float(non_coal_data['电阻率'].mean())
                            except:
                                rock_resistivity = 200.0  # 默认值

                        # 密度越高、电阻率越高，阻隔性越好
                        barrier_factor = min(1.0, (rock_density / 3.0) * (rock_resistivity / 500))
                    else:
                        barrier_factor = 0.5  # 默认中等阻隔

                    # 煤质污染潜力评估
                    coal_pollution_potential = (
                                                       (2.0 - min(2.0, avg_density)) * 2.0 +  # 密度因子
                                                       (avg_gamma / 40) * 3.0 +  # 伽马因子
                                                       (100 / max(10, resistivity)) * 2.5 +  # 电阻率因子
                                                       porosity_factor * 1.5  # 孔隙度因子
                                               ) / 9.0  # 归一化到约0-1范围

                    # 考虑深度因素：浅层污染更容易影响地表和地下水
                    depth_factor = 1.0 - (start - depth_min) / (depth_max - depth_min) * 0.5  # 深度越大，影响越小

                    # 最终污染指数：煤层比例 × 煤炭污染潜力 × 深度因子 ÷ 阻隔因子
                    pollution_level = min(10, (coal_percentage * coal_pollution_potential * depth_factor /
                                               max(0.1, barrier_factor)) * 10)
                else:
                    pollution_level = 0.0
                    avg_density = 0.0
                    avg_gamma = 0.0
                    resistivity = 0.0

                    # 污染物类型评估（基于物理参数特征）
                pollutants = []
                if segment_coal > 0:
                    if 'avg_gamma' in locals() and avg_gamma > 60:
                        pollutants.append({'name': '重金属', 'level': float(min(10, avg_gamma / 10))})
                    if 'avg_density' in locals() and avg_density < 1.3:
                        pollutants.append({'name': '有机污染物', 'level': float(min(10, (1.4 - avg_density) * 20))})
                    if 'pH值' in segment_data.columns and segment_data['pH值'].mean() < 5.5:
                        pollutants.append(
                            {'name': '酸性物质', 'level': float(min(10, (6 - segment_data['pH值'].mean()) * 5))})
                    elif 'resistivity' in locals() and resistivity < 50 and 'avg_gamma' in locals() and avg_gamma > 40:
                        pollutants.append({'name': '酸性物质', 'level': 5.0})  # 中等可能性

                segments.append({
                    'start_depth': float(start),
                    'end_depth': float(end),
                    'coal_percentage': float(coal_percentage),
                    'pollution_level': float(pollution_level),
                    'pollutants': pollutants,
                    'segment_size': float(segment_size),
                    'physical_params': {
                        'density': float(avg_density) if 'avg_density' in locals() else 0.0,
                        'gamma': float(avg_gamma) if 'avg_gamma' in locals() else 0.0,
                        'resistivity': float(resistivity) if 'resistivity' in locals() else 0.0
                    }
                })

                # 加权计算总体污染评分（0-100），考虑深度因素
        if segments:
            weighted_pollution = sum(s['pollution_level'] * (1 - 0.3 * (s['start_depth'] - depth_min) /
                                                             max(1, depth_max - depth_min))
                                     for s in segments)
            max_possible = 10 * len(segments)  # 最高可能分数
            overall_score = min(100, (weighted_pollution / max_possible) * 100)
        else:
            overall_score = 0.0

            # 污染等级分类 (参考国际标准)
        if overall_score < 15:
            pollution_grade = '轻微'
            grade_description = '煤层污染影响极小，无需特殊处理'
        elif overall_score < 35:
            pollution_grade = '轻度'
            grade_description = '存在轻度煤层污染，可采取简单防护措施'
        elif overall_score < 55:
            pollution_grade = '中度'
            grade_description = '中度煤层污染，需要采取防护和治理措施'
        elif overall_score < 75:
            pollution_grade = '严重'
            grade_description = '煤层污染严重，需要专业治理方案'
        else:
            pollution_grade = '极严重'
            grade_description = '煤层污染极为严重，需要紧急治理和区域隔离'

            # 污染影响分析
        impacts = analyze_pollution_impacts(segments, overall_score)

        # 污染扩散风险分析
        diffusion_risk = analyze_diffusion_risk(segments, data, coal_mask)

        # 创建临时目录
        os.makedirs('temp_charts', exist_ok=True)

        # 生成污染深度剖面图
        pollution_profile_chart = generate_pollution_profile(segments, depth_min, depth_max)

        # 生成污染物类型分布图
        pollutant_distribution_chart = generate_pollutant_distribution(segments)

        # 返回结果（确保所有值都是可JSON序列化的）
        return {
            'segments': segments,
            'overall_score': float(overall_score),
            'pollution_grade': pollution_grade,
            'grade_description': grade_description,
            'impacts': impacts,
            'diffusion_risk': diffusion_risk,
            'visualizations': {
                'pollution_profile': pollution_profile_chart,
                'pollutant_distribution': pollutant_distribution_chart
            }
        }
    except Exception as e:
        logger.error(f"煤污染评估失败: {str(e)}")
        # 返回最小可用结果
        return {
            'segments': [],
            'overall_score': 0.0,
            'pollution_grade': '未知',
            'grade_description': '评估过程中发生错误',
            'impacts': {'ecological': [], 'water': [], 'soil': [], 'health': []},
            'diffusion_risk': {'risk_level': {'level': '未知', 'description': '评估失败'}},
            'visualizations': {'pollution_profile': '', 'pollutant_distribution': ''}
        }


def analyze_pollution_impacts(segments, overall_score):
    """分析煤层污染的具体影响"""
    try:
        impacts = {
            'ecological': [],
            'water': [],
            'soil': [],
            'health': []
        }

        # 根据污染程度和类型分析不同方面的影响
        if overall_score > 20:
            impacts['soil'].append('土壤有机质结构可能受到破坏')
        if overall_score > 40:
            impacts['soil'].append('土壤pH值可能发生改变，影响植物生长')
            impacts['ecological'].append('微生物群落结构可能被改变')
        if overall_score > 50:
            impacts['water'].append('浅层地下水可能受到污染')
            impacts['ecological'].append('区域植被生长受抑制')
        if overall_score > 65:
            impacts['water'].append('地下水系统可能遭受长期污染')
            impacts['health'].append('通过食物链富集可能影响健康')
        if overall_score > 80:
            impacts['water'].append('地表水系统可能被连带污染')
            impacts['soil'].append('土壤可能长期无法支持农作物生长')
            impacts['health'].append('可能对居民健康构成直接威胁')
            impacts['ecological'].append('生态系统可能出现不可逆损害')

            # 分析主要污染物类型的特殊影响
        pollutant_types = {}
        for segment in segments:
            for pollutant in segment.get('pollutants', []):
                name = pollutant['name']
                level = pollutant['level']
                if name not in pollutant_types:
                    pollutant_types[name] = 0
                pollutant_types[name] = max(pollutant_types[name], level)

                # 根据污染物类型添加特定影响
        if '重金属' in pollutant_types and pollutant_types['重金属'] > 5:
            impacts['health'].append('重金属可能在生物体内富集，造成慢性中毒')
            impacts['ecological'].append('重金属污染可能导致生物多样性下降')

        if '有机污染物' in pollutant_types and pollutant_types['有机污染物'] > 5:
            impacts['water'].append('有机污染物可能导致水体富营养化')
            impacts['health'].append('某些有机污染物可能具有致癌风险')

        if '酸性物质' in pollutant_types and pollutant_types['酸性物质'] > 5:
            impacts['soil'].append('土壤酸化可能导致养分流失')
            impacts['water'].append('水体酸化可能影响水生生物')

        return impacts
    except Exception as e:
        logger.error(f"污染影响分析失败: {str(e)}")
        return {'ecological': [], 'water': [], 'soil': [], 'health': []}


def analyze_diffusion_risk(segments, data, coal_mask):
    """分析污染物扩散风险"""
    try:
        # 数据验证
        if not segments:
            return {
                'horizontal_risk': 0.0,
                'vertical_risk': 0.0,
                'est_horizontal_speed': 0.1,
                'est_vertical_speed': 0.05,
                'horizontal_range_20y': 2.0,
                'vertical_range_20y': 1.0,
                'risk_level': {'level': '未知', 'description': '无数据分析'}
            }

            # 计算平均物理参数，用于评估扩散风险
        avg_params = {
            'coal_percentage': float(sum(s['coal_percentage'] for s in segments) / len(segments)),
            'density': float(data['密度'].mean())
        }

        # 安全获取电阻率
        try:
            avg_params['resistivity'] = float(data['双侧向电阻率'].mean() if '双侧向电阻率' in data.columns else 100)
        except:
            avg_params['resistivity'] = 100.0

            # 扩散风险因素评估
        horizontal_risk = float(
            min(10, avg_params['coal_percentage'] * 10 * (100 / max(10, avg_params['resistivity']))))
        vertical_risk = float(min(10, avg_params['coal_percentage'] * 10 * (2.0 - min(2.0, avg_params['density']))))

        # 扩散速度估计 (单位: 米/年)
        est_horizontal_speed = float(max(0.1, horizontal_risk * 0.2))  # 0.1-2.0 米/年
        est_vertical_speed = float(max(0.05, vertical_risk * 0.1))  # 0.05-1.0 米/年

        # 扩散范围估计 (单位: 米，20年内)
        horizontal_range = float(est_horizontal_speed * 20)  # 20年内水平扩散范围
        vertical_range = float(est_vertical_speed * 20)  # 20年内垂直扩散范围

        return {
            'horizontal_risk': horizontal_risk,
            'vertical_risk': vertical_risk,
            'est_horizontal_speed': est_horizontal_speed,
            'est_vertical_speed': est_vertical_speed,
            'horizontal_range_20y': horizontal_range,
            'vertical_range_20y': vertical_range,
            'risk_level': get_diffusion_risk_level(horizontal_risk, vertical_risk)
        }
    except Exception as e:
        logger.error(f"扩散风险分析失败: {str(e)}")
        return {
            'horizontal_risk': 0.0,
            'vertical_risk': 0.0,
            'est_horizontal_speed': 0.1,
            'est_vertical_speed': 0.05,
            'horizontal_range_20y': 2.0,
            'vertical_range_20y': 1.0,
            'risk_level': {'level': '未知', 'description': '分析过程中出错'}
        }


def get_diffusion_risk_level(h_risk, v_risk):
    """根据水平和垂直扩散风险确定整体风险等级"""
    try:
        avg_risk = (h_risk + v_risk) / 2

        if avg_risk < 2:
            return {
                'level': '低',
                'description': '污染物扩散风险低，预计将局限在煤层周边小范围内'
            }
        elif avg_risk < 4:
            return {
                'level': '中低',
                'description': '污染物有一定扩散可能，但速度较慢，范围有限'
            }
        elif avg_risk < 6:
            return {
                'level': '中等',
                'description': '污染物将逐步扩散，在数年内可能影响周边区域'
            }
        elif avg_risk < 8:
            return {
                'level': '中高',
                'description': '污染物扩散速度较快，需要采取防护措施防止大范围污染'
            }
        else:
            return {
                'level': '高',
                'description': '污染物扩散风险高，可能迅速影响大范围区域，需要紧急处置'
            }
    except Exception as e:
        logger.error(f"风险等级评估失败: {str(e)}")
        return {'level': '未知', 'description': '无法确定风险等级'}


def generate_pollution_visualization(pollution_assessment):
    """生成污染评估的可视化图表"""
    try:
        set_chinese_font()

        segments = pollution_assessment['segments']
        if not segments:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, '无污染数据可视化', ha='center', va='center', fontsize=14)
            ax.axis('off')
            return safe_plot_to_base64(fig)

        depths = [s['start_depth'] for s in segments]
        pollution_levels = [s['pollution_level'] for s in segments]

        # 创建深度污染柱状图
        fig, ax = plt.subplots(figsize=(10, 8))

        # 根据污染等级使用渐变色
        norm = mcolors.Normalize(vmin=0, vmax=10)
        colors = plt.cm.YlOrRd(norm(pollution_levels))

        bars = ax.barh(depths, pollution_levels, height=8, align='edge', color=colors)

        # 添加污染程度标签
        for i, bar in enumerate(bars):
            if pollution_levels[i] > 1:
                ax.text(bar.get_width() + 0.1, bar.get_y() + 4,
                        f"{pollution_levels[i]:.1f}", va='center')

                # 设置刻度和标签
        ax.set_title('煤层污染深度剖面图', fontsize=15)
        ax.set_xlabel('污染程度 (0-10)', fontsize=12)
        ax.set_ylabel('深度 (米)', fontsize=12)
        ax.set_xlim(0, 10.5)
        ax.invert_yaxis()  # 反转Y轴，使深度从上到下增加
        ax.grid(True, linestyle='--', alpha=0.7)

        # 添加污染等级颜色图例
        sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=norm)
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('污染程度')

        # 添加整体评分
        overall_text = (f"整体污染评分: {pollution_assessment['overall_score']:.1f}/100\n"
                        f"污染等级: {pollution_assessment['pollution_grade']}")
        ax.text(0.5, 0.02, overall_text, transform=ax.transAxes,
                ha='center', va='bottom', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        # 尝试保存为临时文件作为备份
        try:
            filename = f"temp_charts/pollution_viz_{id(fig)}.png"
            fig.savefig(filename, format='png', dpi=100, bbox_inches='tight')
        except Exception as e:
            logger.warning(f"无法保存临时图表文件: {str(e)}")

            # 转换为base64
        return safe_plot_to_base64(fig)
    except Exception as e:
        logger.error(f"生成污染可视化失败: {str(e)}")
        return ""


def generate_pollution_profile(segments, depth_min, depth_max):
    """生成污染深度剖面图"""
    try:
        set_chinese_font()

        if not segments:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, '无污染剖面数据', ha='center', va='center', fontsize=14)
            ax.axis('off')
            return safe_plot_to_base64(fig)

            # 提取数据
        depths = [(s['start_depth'] + s['end_depth']) / 2 for s in segments]
        pollution_levels = [s['pollution_level'] for s in segments]
        coal_percentages = [s['coal_percentage'] * 10 for s in segments]  # 放大10倍用于绘图

        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8))

        # 绘制污染程度曲线和煤层占比
        ax.plot(pollution_levels, depths, 'ro-', linewidth=2, label='污染程度')
        ax.plot(coal_percentages, depths, 'b--', linewidth=1.5, label='煤层占比×10')

        # 添加背景色带
        for level, color, label in [
            (2, '#e6ffcc', '轻微'),
            (4, '#ffffcc', '轻度'),
            (6, '#ffd699', '中度'),
            (8, '#ffb399', '严重'),
            (10, '#ff8080', '极严重')
        ]:
            ax.axvspan(level - 2, level, alpha=0.3, color=color)

            # 添加辅助线
        ax.grid(True, linestyle='--', alpha=0.6)

        # 设置坐标轴
        ax.set_title('煤层污染深度剖面图', fontsize=15)
        ax.set_xlabel('污染程度/煤层占比', fontsize=12)
        ax.set_ylabel('深度 (米)', fontsize=12)
        ax.set_xlim(0, 10)
        ax.set_ylim(depth_max, depth_min)  # 反转Y轴
        ax.legend(loc='upper right')

        # 添加污染分区图例
        handles = [Patch(color=c, alpha=0.3, label=l) for c, l in [
            ('#e6ffcc', '轻微污染'),
            ('#ffffcc', '轻度污染'),
            ('#ffd699', '中度污染'),
            ('#ffb399', '严重污染'),
            ('#ff8080', '极严重污染')
        ]]
        ax2 = ax.twinx()
        ax2.set_yticks([])
        ax2.legend(handles=handles, loc='upper left', title='污染分区')

        # 尝试保存为临时文件作为备份
        try:
            filename = f"temp_charts/pollution_profile_{id(fig)}.png"
            fig.savefig(filename, format='png', dpi=100, bbox_inches='tight')
        except Exception as e:
            logger.warning(f"无法保存临时图表文件: {str(e)}")

        return safe_plot_to_base64(fig)
    except Exception as e:
        logger.error(f"生成污染剖面图失败: {str(e)}")
        return ""


def generate_pollutant_distribution(segments):
    """生成污染物类型分布图"""
    try:
        set_chinese_font()

        # 统计各类污染物的分布
        pollutant_count = {}
        pollutant_levels = {}

        for segment in segments:
            for pollutant in segment.get('pollutants', []):
                name = pollutant['name']
                level = pollutant['level']

                if name not in pollutant_count:
                    pollutant_count[name] = 0
                    pollutant_levels[name] = []

                pollutant_count[name] += 1
                pollutant_levels[name].append(level)

                # 如果没有污染物数据，返回空图
        if not pollutant_count:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, '无明确污染物分布数据', ha='center', va='center', fontsize=14)
            ax.axis('off')
            return safe_plot_to_base64(fig)

            # 计算平均污染程度
        avg_levels = {name: sum(levels) / len(levels) for name, levels in pollutant_levels.items()}

        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        # 绘制污染物出现频率饼图
        labels = list(pollutant_count.keys())
        sizes = list(pollutant_count.values())
        colors = plt.cm.Paired(np.linspace(0, 1, len(labels)))

        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.axis('equal')
        ax1.set_title('污染物类型分布')

        # 绘制污染物平均污染程度条形图
        names = list(avg_levels.keys())
        avgs = list(avg_levels.values())

        bars = ax2.barh(names, avgs, color=colors[:len(names)])
        ax2.set_xlim(0, 10)
        ax2.set_title('污染物平均污染程度')
        ax2.set_xlabel('污染程度 (0-10)')

        # 添加数值标签
        for i, bar in enumerate(bars):
            ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                     f"{avgs[i]:.1f}", va='center')

        fig.tight_layout()

        # 尝试保存为临时文件作为备份
        try:
            filename = f"temp_charts/pollutant_dist_{id(fig)}.png"
            fig.savefig(filename, format='png', dpi=100, bbox_inches='tight')
        except Exception as e:
            logger.warning(f"无法保存临时图表文件: {str(e)}")

        return safe_plot_to_base64(fig)
    except Exception as e:
        logger.error(f"生成污染物分布图失败: {str(e)}")
        return ""