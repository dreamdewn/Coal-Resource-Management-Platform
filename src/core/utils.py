# utils.py - 通用工具函数
import matplotlib
import os
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.font_manager import FontProperties
import numpy as np

# 设置matplotlib使用非交互式后端，避免多线程问题
matplotlib.use('Agg')  # 必须在其他matplotlib导入之前设置


# 检查文件类型是否合法
def allowed_file(filename, allowed_extensions={'xlsx', 'xls', 'csv'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# 设置中文字体
def set_chinese_font():
    try:
        # 尝试使用系统中的中文字体
        font_paths = ['C:/Windows/Fonts/simhei.ttf',  # Windows简黑
                      'C:/Windows/Fonts/msyh.ttf',  # 微软雅黑
                      '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc']  # Linux文泉驿

        for font_path in font_paths:
            if os.path.exists(font_path):
                plt.rcParams['font.family'] = ['simhei']  # 使用简黑字体
                plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                return

                # 如果找不到指定字体，使用matplotlib内置支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        print(f"设置中文字体时出错: {e}")

    # 将Matplotlib图表转换为base64编码的图像


def plot_to_base64(fig, dpi=100):
    """
    将Matplotlib图表转换为base64编码字符串

    参数:
        fig: matplotlib图表对象
        dpi: 图像分辨率，默认为100

    返回:
        base64编码的PNG图像字符串
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=dpi)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    return image_base64