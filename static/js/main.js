// 主要的JavaScript功能

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initializeComponents();
    setupEventListeners();
});

// 初始化组件
function initializeComponents() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log('组件初始化完成');
}

// 设置事件监听器
function setupEventListeners() {
    // 为所有带有data-action属性的按钮添加点击事件
    document.querySelectorAll('[data-action]').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const target = this.getAttribute('data-target');
            
            switch(action) {
                case 'refresh':
                    refreshData(target);
                    break;
                case 'delete':
                    confirmDelete(target);
                    break;
                default:
                    console.warn('未知的操作:', action);
            }
        });
    });
}

// 刷新数据
function refreshData(target) {
    if (target) {
        // 如果指定了目标，刷新特定数据
        console.log('刷新数据:', target);
        // 这里可以添加具体的刷新逻辑
    } else {
        // 否则刷新整个页面
        location.reload();
    }
}

// 确认删除
function confirmDelete(target) {
    if (confirm('确定要删除这个项目吗？此操作不可撤销。')) {
        // 用户确认删除
        performDelete(target);
    }
}

// 执行删除操作
function performDelete(target) {
    if (target) {
        console.log('执行删除操作:', target);
        // 这里可以添加具体的删除逻辑
        // 例如发送AJAX请求到服务器
    }
}

// 显示通知消息
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 将通知添加到页面顶部
    const container = document.querySelector('.container');
    if (container) {
        // 检查是否已存在通知容器
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            container.insertBefore(notificationContainer, container.firstChild);
        }
        notificationContainer.appendChild(notification);
    }
    
    // 5秒后自动隐藏通知
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// 格式化字节大小
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// 格式化百分比
function formatPercentage(value, decimals = 2) {
    return parseFloat(value).toFixed(decimals) + '%';
}

// 更新仪表板指标
function updateDashboardMetrics(metrics) {
    // 更新CPU使用率
    if (metrics.cpu_percent !== undefined) {
        const cpuElement = document.getElementById('cpu-percent');
        if (cpuElement) {
            cpuElement.textContent = formatPercentage(metrics.cpu_percent);
        }
    }
    
    // 更新内存使用率
    if (metrics.memory_percent !== undefined) {
        const memoryElement = document.getElementById('memory-percent');
        if (memoryElement) {
            memoryElement.textContent = formatPercentage(metrics.memory_percent);
        }
    }
    
    // 更新磁盘使用率
    if (metrics.disk_percent !== undefined) {
        const diskElement = document.getElementById('disk-percent');
        if (diskElement) {
            diskElement.textContent = formatPercentage(metrics.disk_percent);
        }
    }
}

// 动态更新图表数据
function updateChart(chart, newData) {
    if (chart && newData) {
        chart.data.datasets[0].data = newData;
        chart.update();
    }
}

// 加载图表数据
function loadChartData(url, chartId, dataKey) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const chart = Chart.getChart(chartId);
            if (chart) {
                chart.data.labels = data.timestamps;
                chart.data.datasets[0].data = data[dataKey];
                chart.update();
            }
        })
        .catch(error => console.error('加载图表数据失败:', error));
}