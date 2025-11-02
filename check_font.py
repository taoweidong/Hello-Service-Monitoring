"""检查中文字体设置"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("当前字体设置:", plt.rcParams['font.sans-serif'])
print("负号显示设置:", plt.rcParams['axes.unicode_minus'])

# 列出系统中可用的中文字体
fonts = [f.name for f in fm.fontManager.ttflist if 'Sim' in f.name or 'hei' in f.name.lower() or 'song' in f.name.lower()]
print("可用的中文字体:", fonts)