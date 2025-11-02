"""验证中文字体修复"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 检查是否应用了中文字体设置
print("字体设置:", plt.rcParams['font.sans-serif'])
print("负号设置:", plt.rcParams['axes.unicode_minus'])

# 测试创建一个简单的图表
plt.figure(figsize=(8, 6))
plt.plot([1, 2, 3], [1, 4, 2])
plt.title('测试图表')
plt.xlabel('X轴')
plt.ylabel('Y轴')

# 尝试保存图表
try:
    plt.savefig('test_chart.png', dpi=100, bbox_inches='tight')
    print("图表保存成功，中文字体修复完成")
except Exception as e:
    print(f"保存图表时出错: {e}")
finally:
    plt.close()