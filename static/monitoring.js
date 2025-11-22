/**
 * 监控系统数据加载模块
 * 负责从后端API获取数据并更新前端页面
 */

class MonitoringDataLoader {
    constructor() {
        // 存储历史数据用于图表显示
        this.memoryHistory = [];
        this.diskHistory = [];
        this.timeHistory = [];
        
        // 绑定事件
        this.init();
    }
    
    /**
     * 初始化页面
     */
    init() {
        // 页面加载完成后获取数据
        document.addEventListener('DOMContentLoaded', () => {
            this.loadAllData();
            
            // 根据项目规范，仅在页面刷新时获取最新数据
            // 不使用定时更新机制
        });
    }
    
    /**
     * 加载所有数据
     */
    async loadAllData() {
        try {
            // 显示刷新指示器
            this.showRefreshIndicator();
            
            // 并行加载所有数据
            await Promise.all([
                this.loadSystemOverview(),
                this.loadServerDetails(),
                this.loadMemoryTrend(),
                this.loadDiskTrend(),
                this.loadDiskDetails(),
                this.loadProcessList()
            ]);
        } catch (error) {
            console.error('加载数据失败:', error);
        } finally {
            // 隐藏刷新指示器
            setTimeout(() => {
                this.hideRefreshIndicator();
            }, 1000);
        }
    }
    
    /**
     * 显示刷新指示器
     */
    showRefreshIndicator() {
        const indicator = document.getElementById('refresh-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }
    
    /**
     * 隐藏刷新指示器
     */
    hideRefreshIndicator() {
        const indicator = document.getElementById('refresh-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    /**
     * 获取服务器IP地址
     */
    async getServerIP() {
        try {
            const response = await fetch('/api/server-ip');
            const data = await response.json();
            
            const ipElement = document.getElementById('server-ip');
            if (ipElement && data.ip) {
                ipElement.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-server me-2" viewBox="0 0 16 16">
                        <path d="M1.333 2.667C1.333 1.194 4.318 0 8 0s6.667 1.194 6.667 2.667V4c0 1.473-2.985 2.667-6.667 2.667S1.333 5.473 1.333 4V2.667z"/>
                        <path d="M1.333 6.334v3C1.333 10.805 4.318 12 8 12s6.667-1.194 6.667-2.667V6.334a6.51 6.51 0 0 1-1.458.79C11.81 7.684 9.967 8 8 8c-1.966 0-3.809-.317-5.208-.876a6.509 6.509 0 0 1-1.458-.79z"/>
                        <path d="M14.667 11.668a6.51 6.51 0 0 1-1.458.789c-1.4.56-3.242.876-5.21.876-1.966 0-3.809-.316-5.208-.876a6.51 6.51 0 0 1-1.458-.79v1.666C1.333 14.806 4.318 16 8 16s6.667-1.194 6.667-2.667v-1.665z"/>
                    </svg>
                    服务器IP: ${data.ip}
                `;
            } else if (ipElement) {
                ipElement.textContent = '无法获取服务器IP地址';
            }
        } catch (error) {
            console.error('获取服务器IP失败:', error);
            const ipElement = document.getElementById('server-ip');
            if (ipElement) {
                ipElement.textContent = '无法获取服务器IP地址';
            }
        }
    }
    
    /**
     * 加载系统概览数据
     */
    async loadSystemOverview() {
        try {
            // 并行获取CPU、内存和磁盘数据
            const [cpuResponse, memoryResponse, diskResponse] = await Promise.all([
                fetch('/api/system/cpu'),
                fetch('/api/system/memory'),
                fetch('/api/system/disk')
            ]);
            
            const cpuData = await cpuResponse.json();
            const memoryData = await memoryResponse.json();
            const diskData = await diskResponse.json();
            
            // 更新CPU使用率
            const cpuPercent = cpuData.cpu_percent;
            const cpuPercentElement = document.getElementById('cpu-percent');
            if (cpuPercentElement) {
                cpuPercentElement.textContent = cpuPercent.toFixed(2) + '%';
            }
            
            const cpuProgressElement = document.getElementById('cpu-progress');
            if (cpuProgressElement) {
                cpuProgressElement.style.width = cpuPercent + '%';
            }
            
            // 更新内存使用率
            const memoryPercent = memoryData.memory_percent;
            const memoryPercentElement = document.getElementById('memory-percent');
            if (memoryPercentElement) {
                memoryPercentElement.textContent = memoryPercent.toFixed(2) + '%';
            }
            
            const memoryProgressElement = document.getElementById('memory-progress');
            if (memoryProgressElement) {
                memoryProgressElement.style.width = memoryPercent + '%';
            }
            
            const memoryCard = document.getElementById('memory-card');
            if (memoryCard) {
                memoryCard.className = 'metric-card ' + 
                    (memoryPercent > 80 ? 'critical' : memoryPercent > 60 ? 'warning' : 'normal');
            }
            
            // 更新磁盘使用率
            const maxDiskPercent = diskData.max_disk_percent;
            const diskPercentElement = document.getElementById('disk-percent');
            if (diskPercentElement) {
                diskPercentElement.textContent = maxDiskPercent.toFixed(2) + '%';
            }
            
            const diskProgressElement = document.getElementById('disk-progress');
            if (diskProgressElement) {
                diskProgressElement.style.width = maxDiskPercent + '%';
            }
            
            const diskCard = document.getElementById('disk-card');
            if (diskCard) {
                diskCard.className = 'metric-card ' + 
                    (maxDiskPercent > 80 ? 'critical' : maxDiskPercent > 60 ? 'warning' : 'normal');
            }
            
            // 更新应用程序版本
            const pythonVersionElement = document.getElementById('python-version');
            if (pythonVersionElement) {
                pythonVersionElement.textContent = diskData.applications.python || '未安装';
            }
            
            const javaVersionElement = document.getElementById('java-version');
            if (javaVersionElement) {
                javaVersionElement.textContent = diskData.applications.java || '未安装';
            }
            
            const dockerVersionElement = document.getElementById('docker-version');
            if (dockerVersionElement) {
                dockerVersionElement.textContent = diskData.applications.docker || '未安装';
            }
        } catch (error) {
            console.error('获取系统概览数据失败:', error);
        }
    }
    
    /**
     * 加载服务器详细信息
     */
    async loadServerDetails() {
        try {
            const response = await fetch('/api/system/details');
            const data = await response.json();
            
            // 更新操作系统信息
            const osInfoElement = document.getElementById('os-info');
            if (osInfoElement) {
                osInfoElement.textContent = `${data.system} ${data.release}`;
            }
            
            const osVersionElement = document.getElementById('os-version');
            if (osVersionElement) {
                osVersionElement.textContent = data.version;
            }
            
            const hostnameElement = document.getElementById('hostname');
            if (hostnameElement) {
                hostnameElement.textContent = data.node;
            }
            
            const architectureElement = document.getElementById('architecture');
            if (architectureElement) {
                architectureElement.textContent = data.machine;
            }
            
            const processorElement = document.getElementById('processor');
            if (processorElement) {
                processorElement.textContent = data.processor || '未知';
            }
            
            const pythonVersionDetailElement = document.getElementById('python-version-detail');
            if (pythonVersionDetailElement) {
                pythonVersionDetailElement.textContent = data.python_version;
            }
            
            const cpuCoresElement = document.getElementById('cpu-cores');
            if (cpuCoresElement) {
                cpuCoresElement.textContent = `${data.cpu_count_physical || '未知'} 物理核心, ${data.cpu_count_logical || '未知'} 逻辑核心`;
            }
            
            const totalMemoryElement = document.getElementById('total-memory');
            if (totalMemoryElement) {
                totalMemoryElement.textContent = this.formatBytes(data.memory.total);
            }
            
            // 使用本地时区显示启动时间
            const bootTimeElement = document.getElementById('boot-time');
            if (bootTimeElement && data.boot_time) {
                const bootTime = new Date(data.boot_time * 1000);
                bootTimeElement.textContent = bootTime.toLocaleString('zh-CN', {
                    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
                });
            }
            
            const kernelVersionElement = document.getElementById('kernel-version');
            if (kernelVersionElement) {
                kernelVersionElement.textContent = data.version;
            }
        } catch (error) {
            console.error('获取服务器详细信息失败:', error);
            // 设置默认值
            const elementsToUpdate = [
                'os-info', 'os-version', 'hostname', 'architecture',
                'processor', 'python-version-detail', 'cpu-cores',
                'total-memory', 'boot-time', 'kernel-version'
            ];
            
            elementsToUpdate.forEach(elementId => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.textContent = '无法获取';
                }
            });
        }
    }
    
    /**
     * 加载内存使用趋势数据
     */
    async loadMemoryTrend() {
        try {
            const response = await fetch('/api/trend/memory');
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                this.drawMemoryChart(data.history);
            }
        } catch (error) {
            console.error('获取内存趋势数据失败:', error);
        }
    }
    
    /**
     * 加载磁盘使用趋势数据
     */
    async loadDiskTrend() {
        try {
            const response = await fetch('/api/trend/disk');
            const data = await response.json();
            
            if (data.history && Object.keys(data.history).length > 0) {
                this.drawDiskChart(data.history);
            }
        } catch (error) {
            console.error('获取磁盘趋势数据失败:', error);
        }
    }
    
    /**
     * 绘制内存使用趋势图表
     */
    drawMemoryChart(historyData) {
        if (!historyData || historyData.length === 0) return;
        
        // 提取时间和内存使用率数据
        const timestamps = historyData.map(item => new Date(item.timestamp));
        const memoryPercents = historyData.map(item => item.memory_percent);
        
        // 创建图表数据
        const chartData = [{
            x: timestamps,
            y: memoryPercents,
            type: 'scatter',
            mode: 'lines+markers',
            name: '内存使用率',
            line: {shape: 'spline', color: '#4361ee'},
            marker: {size: 6}
        }];
        
        // 图表布局
        const layout = {
            title: '内存使用趋势',
            xaxis: {title: '时间'},
            yaxis: {title: '使用率(%)', range: [0, 100]},
            margin: {t: 30, l: 50, r: 30, b: 50}
        };
        
        // 绘制图表
        const chartElement = document.getElementById('memory-chart');
        if (chartElement) {
            Plotly.newPlot('memory-chart', chartData, layout);
        }
    }
    
    /**
     * 绘制磁盘使用趋势图表
     */
    drawDiskChart(historyData) {
        if (!historyData || Object.keys(historyData).length === 0) return;
        
        // 创建图表数据
        const chartData = [];
        
        // 为每个磁盘设备创建一条线
        for (const device in historyData) {
            const deviceData = historyData[device];
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
        
        // 图表布局
        const layout = {
            title: '磁盘使用趋势',
            xaxis: {title: '时间'},
            yaxis: {title: '使用率(%)', range: [0, 100]},
            margin: {t: 30, l: 50, r: 30, b: 50}
        };
        
        // 绘制图表
        const chartElement = document.getElementById('disk-chart');
        if (chartElement) {
            Plotly.newPlot('disk-chart', chartData, layout);
        }
    }
    
    /**
     * 加载磁盘详情数据
     */
    async loadDiskDetails() {
        try {
            const response = await fetch('/api/system/disk');
            const data = await response.json();
            
            const diskTableBody = document.getElementById('disk-table-body');
            const diskCollectionTime = document.getElementById('disk-collection-time');
            
            if (diskTableBody) {
                diskTableBody.innerHTML = '';
                
                // 获取采集时间并显示
                if (diskCollectionTime && data.collection_time) {
                    const collectionTime = new Date(data.collection_time);
                    diskCollectionTime.textContent = collectionTime.toLocaleString('zh-CN', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
                    });
                } else if (diskCollectionTime) {
                    // 获取当前时间作为采集时间
                    const currentTime = new Date().toLocaleString('zh-CN', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
                    });
                    diskCollectionTime.textContent = currentTime;
                }
                
                // 填充磁盘详情表格
                if (data.disks && Array.isArray(data.disks)) {
                    data.disks.forEach(disk => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${disk.device}</td>
                            <td>${disk.mountpoint}</td>
                            <td>${this.formatBytes(disk.total)}</td>
                            <td>${this.formatBytes(disk.used)}</td>
                            <td>${this.formatBytes(disk.free)}</td>
                            <td>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar ${disk.percent > 80 ? 'bg-danger' : disk.percent > 60 ? 'bg-warning' : 'bg-success'}" 
                                         role="progressbar" style="width: ${disk.percent}%" aria-valuenow="${disk.percent}" 
                                         aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <small class="text-muted">${disk.percent.toFixed(2)}%</small>
                            </td>
                        `;
                        diskTableBody.appendChild(row);
                    });
                }
            }
        } catch (error) {
            console.error('获取磁盘详情数据失败:', error);
        }
    }
    
    /**
     * 加载进程列表数据
     */
    async loadProcessList() {
        try {
            const response = await fetch('/api/system/processes');
            const data = await response.json();
            
            const processTableBody = document.getElementById('process-table-body');
            const processCollectionTime = document.getElementById('process-collection-time');
            
            if (processTableBody) {
                processTableBody.innerHTML = '';
                
                // 显示采集时间
                if (processCollectionTime && data.collection_time) {
                    const collectionTime = new Date(data.collection_time);
                    processCollectionTime.textContent = collectionTime.toLocaleString('zh-CN', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
                    });
                } else if (processCollectionTime) {
                    // 获取当前时间作为采集时间
                    const currentTime = new Date().toLocaleString('zh-CN', {
                        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
                    });
                    processCollectionTime.textContent = currentTime;
                }
                
                // 填充进程列表表格
                if (data.processes && Array.isArray(data.processes)) {
                    data.processes.forEach(proc => {
                        // 确定状态样式
                        let statusClass = 'status-running';
                        if (proc.status === 'sleeping') {
                            statusClass = 'status-sleeping';
                        } else if (proc.status === 'stopped') {
                            statusClass = 'status-stopped';
                        }
                        
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${proc.pid}</td>
                            <td>${proc.name}</td>
                            <td><span class="status-badge ${statusClass}">${proc.status}</span></td>
                            <td>${proc.cpu_percent.toFixed(2)}</td>
                            <td>${proc.memory_percent.toFixed(2)}</td>
                        `;
                        processTableBody.appendChild(row);
                    });
                }
            }
        } catch (error) {
            console.error('获取进程列表数据失败:', error);
            // 即使获取失败，也更新采集时间
            const processCollectionTime = document.getElementById('process-collection-time');
            if (processCollectionTime) {
                const currentTime = new Date().toLocaleString('zh-CN', {
                    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
                });
                processCollectionTime.textContent = currentTime;
            }
        }
    }
    
    /**
     * 格式化字节数
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// 初始化数据加载器
const dataLoader = new MonitoringDataLoader();

// 页面加载时获取服务器IP
document.addEventListener('DOMContentLoaded', () => {
    dataLoader.getServerIP();
});