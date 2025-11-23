# app/utils/chart_utils.py
"""图表生成工具类"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Dict, Any
from loguru import logger

from ..config.config import Config


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def _setup_figure(self, figsize: Tuple[int, int] = (12, 6)) -> Tuple[plt.Figure, plt.Axes]:
        """
        设置图表基础配置
        
        Args:
            figsize: 图表大小
            
        Returns:
            Tuple[plt.Figure, plt.Axes]: 图表对象和坐标轴对象
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.grid(True, alpha=0.3)
        return fig, ax
    
    def _save_chart(self, fig: plt.Figure, filename: str) -> str:
        """
        保存图表到文件
        
        Args:
            fig: 图表对象
            filename: 文件名
            
        Returns:
            str: 图片文件路径
        """
        # 确保临时目录存在
        chart_dir = os.path.join(Config.BASE_DIR, 'temp')
        if not os.path.exists(chart_dir):
            os.makedirs(chart_dir)
            
        chart_path = os.path.join(chart_dir, filename)
        plt.tight_layout()
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        logger.info(f"图表已保存: {chart_path}")
        return chart_path
    
    def create_line_chart(
        self,
        x_data: List[Any],
        y_data: List[List[float]],
        labels: List[str],
        title: str = "趋势图",
        x_label: str = "X轴",
        y_label: str = "Y轴",
        colors: Optional[List[str]] = None,
        filename: str = "line_chart.png"
    ) -> str:
        """
        创建折线图
        
        Args:
            x_data: X轴数据
            y_data: Y轴数据列表（支持多条线）
            labels: 每条线的标签
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            colors: 线条颜色列表
            filename: 保存的文件名
            
        Returns:
            str: 图片文件路径
        """
        try:
            fig, ax = self._setup_figure()
            
            # 默认颜色
            if colors is None:
                colors = ['#4361ee', '#f72585', '#4cc9f0', '#7209b7', '#3a0ca3']
            
            # 绘制多条折线
            for i, (y_series, label) in enumerate(zip(y_data, labels)):
                color = colors[i % len(colors)]
                ax.plot(x_data, y_series, label=label, linewidth=2, color=color)
            
            # 设置图表样式
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel(x_label, fontsize=12)
            ax.set_ylabel(y_label, fontsize=12)
            ax.legend()
            
            # 格式化x轴日期（如果是日期类型）
            fig.autofmt_xdate()
            
            return self._save_chart(fig, filename)
            
        except Exception as e:
            logger.error(f"创建折线图时出错: {e}")
            # 创建错误提示图表
            fig, ax = self._setup_figure()
            ax.text(0.5, 0.5, f'图表生成失败: {str(e)}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('图表生成错误')
            return self._save_chart(fig, f"error_{filename}")
    
    def create_bar_chart(
        self,
        x_data: List[Any],
        y_data: List[float],
        title: str = "柱状图",
        x_label: str = "X轴",
        y_label: str = "Y轴",
        color: str = '#4361ee',
        filename: str = "bar_chart.png"
    ) -> str:
        """
        创建柱状图
        
        Args:
            x_data: X轴数据
            y_data: Y轴数据
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            color: 柱子颜色
            filename: 保存的文件名
            
        Returns:
            str: 图片文件路径
        """
        try:
            fig, ax = self._setup_figure()
            
            # 绘制柱状图
            bars = ax.bar(x_data, y_data, color=color)
            
            # 在柱子上显示数值
            for bar, value in zip(bars, y_data):
                height = bar.get_height()
                ax.annotate(f'{value:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)
            
            # 设置图表样式
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlabel(x_label, fontsize=12)
            ax.set_ylabel(y_label, fontsize=12)
            
            # 格式化x轴标签（防止重叠）
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            return self._save_chart(fig, filename)
            
        except Exception as e:
            logger.error(f"创建柱状图时出错: {e}")
            # 创建错误提示图表
            fig, ax = self._setup_figure()
            ax.text(0.5, 0.5, f'图表生成失败: {str(e)}', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('图表生成错误')
            return self._save_chart(fig, f"error_{filename}")
    
    def create_empty_chart(self, message: str = "暂无数据", title: str = "资源使用趋势", filename: str = "empty_chart.png") -> str:
        """
        创建空图表（用于无数据情况）
        
        Args:
            message: 显示的消息
            title: 图表标题
            filename: 保存的文件名
            
        Returns:
            str: 图片文件路径
        """
        fig, ax = self._setup_figure()
        ax.text(0.5, 0.5, message, ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return self._save_chart(fig, filename)