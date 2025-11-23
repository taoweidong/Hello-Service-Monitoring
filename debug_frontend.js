// 调试前端JavaScript代码

// 重写loadDiskTrend方法以添加更多调试信息
async function debugLoadDiskTrend() {
    console.log("开始加载磁盘趋势数据...");
    try {
        const response = await fetch('/api/trend/disk');
        console.log("API响应状态:", response.status);
        const data = await response.json();
        console.log("API返回数据:", data);
        
        if (data.history && Object.keys(data.history).length > 0) {
            console.log("调用drawDiskChart方法绘制图表...");
            drawDiskChart(data.history);
        } else {
            console.log("没有磁盘趋势数据可显示");
        }
    } catch (error) {
        console.error('获取磁盘趋势数据失败:', error);
    }
}

// 重写drawDiskChart方法以添加更多调试信息
function debugDrawDiskChart(historyData) {
    console.log("开始绘制磁盘趋势图表...", historyData);
    if (!historyData || Object.keys(historyData).length === 0) {
        console.log("没有数据可绘制");
        return;
    }
    
    // 创建图表数据
    const chartData = [];
    
    // 为每个磁盘设备创建一条线
    for (const device in historyData) {
        console.log("处理设备:", device);
        const deviceData = historyData[device];
        console.log("设备数据:", deviceData);
        const timestamps = deviceData.map(item => new Date(item.timestamp));
        const percents = deviceData.map(item => item.percent);
        
        chartData.push({
            x: timestamps,
            y: percents,
            type: 'scatter',
            mode: 'lines+markers',
            name: device,
            line: {shape: 'spline', color: '#4cc9f0'},
            marker: {size: 6}
        });
    }
    
    console.log("图表数据:", chartData);
    
    // 图表布局
    const layout = {
        title: '磁盘使用趋势',
        xaxis: {title: '时间'},
        yaxis: {title: '使用率(%)', range: [0, 100]},
        margin: {t: 30, l: 50, r: 30, b: 50}
    };
    
    // 绘制图表
    const chartElement = document.getElementById('disk-chart');
    console.log("图表元素:", chartElement);
    if (chartElement) {
        // 确保Plotly已经加载
        console.log("Plotly是否已加载:", typeof Plotly !== 'undefined');
        if (typeof Plotly !== 'undefined') {
            console.log("调用Plotly.newPlot绘制图表");
            Plotly.newPlot('disk-chart', chartData, layout);
        } else {
            console.log("Plotly未加载，无法绘制图表");
        }
    } else {
        console.log("未找到图表元素");
    }
}

// 页面加载完成后测试
document.addEventListener('DOMContentLoaded', () => {
    console.log("页面加载完成，开始测试磁盘趋势图表...");
    // 替换原有的方法
    // 注意：在实际应用中，我们需要修改MonitoringDataLoader类
    debugLoadDiskTrend();
});