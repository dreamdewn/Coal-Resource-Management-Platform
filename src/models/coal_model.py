# src/models/coal_model.py - 煤层数据模型

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd

@dataclass
class CoalLayer:
    """煤层数据模型"""
    layer_number: int
    start_depth: float
    end_depth: float
    thickness: float
    volume: float
    density: float
    mass_tons: float
    quality_score: float
    quality_grade: str
    mining_difficulty: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'layer_number': self.layer_number,
            'start_depth': self.start_depth,
            'end_depth': self.end_depth,
            'thickness': self.thickness,
            'volume': self.volume,
            'density': self.density,
            'mass_tons': self.mass_tons,
            'quality_score': self.quality_score,
            'quality_grade': self.quality_grade,
            'mining_difficulty': self.mining_difficulty
        }

@dataclass
class CoalAnalysisResult:
    """煤层分析结果模型"""
    filename: str
    location: str
    notes: str
    timestamp: str
    total_thickness: float
    layers: List[CoalLayer]
    chart_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'filename': self.filename,
            'location': self.location,
            'notes': self.notes,
            'timestamp': self.timestamp,
            'total_thickness': self.total_thickness,
            'layers': [layer.to_dict() for layer in self.layers],
            'chart_data': self.chart_data
        }

@dataclass
class DrillingData:
    """钻井数据模型"""
    depth: List[float]
    deep_resistivity: List[float]
    shallow_resistivity: List[float]
    sonic_interval: List[float]
    natural_gamma: List[float]
    density: List[float]
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> 'DrillingData':
        """从DataFrame创建实例"""
        return cls(
            depth=df['深度'].tolist(),
            deep_resistivity=df['深侧向'].tolist(),
            shallow_resistivity=df['浅侧向'].tolist(),
            sonic_interval=df['声波时差'].tolist(),
            natural_gamma=df['自然伽玛'].tolist(),
            density=df['密度'].tolist()
        )
    
    def to_dataframe(self) -> pd.DataFrame:
        """转换为DataFrame"""
        return pd.DataFrame({
            '深度': self.depth,
            '深侧向': self.deep_resistivity,
            '浅侧向': self.shallow_resistivity,
            '声波时差': self.sonic_interval,
            '自然伽玛': self.natural_gamma,
            '密度': self.density
        })
