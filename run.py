#!/usr/bin/env python3
# run.py - 应用启动脚本

"""
矿能云析系统启动脚本

支持不同环境的启动：
- 开发环境: python run.py
- 生产环境: python run.py --env production
- 测试环境: python run.py --env testing
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app
from config.settings import config

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='矿能云析系统启动脚本')
    parser.add_argument('--env', 
                       choices=['development', 'production', 'testing'],
                       default='development',
                       help='运行环境 (默认: development)')
    parser.add_argument('--host', 
                       default='0.0.0.0',
                       help='绑定主机 (默认: 0.0.0.0)')
    parser.add_argument('--port', 
                       type=int,
                       default=5000,
                       help='绑定端口 (默认: 5000)')
    parser.add_argument('--debug', 
                       action='store_true',
                       help='启用调试模式')
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = args.env
    
    # 获取配置
    current_config = config[args.env]()
    
    # 设置Flask配置
    app.config.update({
        'DEBUG': args.debug or current_config.DEBUG,
        'TESTING': current_config.TESTING
    })
    
    print(f"🚀 启动矿能云析系统...")
    print(f"📋 环境: {args.env}")
    print(f"🌐 地址: http://{args.host}:{args.port}")
    print(f"🔧 调试模式: {'开启' if app.config['DEBUG'] else '关闭'}")
    print(f"📁 数据目录: {current_config.UPLOAD_FOLDER}")
    print("-" * 50)
    
    try:
        app.run(host=args.host, port=args.port, debug=app.config['DEBUG'])
    except KeyboardInterrupt:
        print("\n👋 系统已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
