        // 鏇存柊绯荤粺淇℃伅
        function updateSystemInfo() {
            fetch('/api/system-info')
                .then(response => response.json())
                .then(data => {
                    // 鏇存柊CPU浣跨敤鐜?
                    document.getElementById('cpu-percent').textContent = data.system.cpu_percent.toFixed(2) + '%';
                    
                    // 鏇存柊鍐呭瓨浣跨敤鐜?
                    const memoryPercent = data.system.memory_percent;
                    document.getElementById('memory-percent').textContent = memoryPercent.toFixed(2) + '%';
                    const memoryCard = document.getElementById('memory-card');
                    memoryCard.className = 'card metric-card ' + 
                        (memoryPercent > 80 ? 'critical' : memoryPercent > 60 ? 'warning' : 'normal');
                    
                    // 鏇存柊纾佺洏浣跨敤鐜?
                    let maxDiskPercent = 0;
                    data.disks.forEach(disk => {
                        if (disk.percent > maxDiskPercent) {
                            maxDiskPercent = disk.percent;
                        }
                    });
                    document.getElementById('disk-percent').textContent = maxDiskPercent.toFixed(2) + '%';
                    const diskCard = document.getElementById('disk-card');
                    diskCard.className = 'card metric-card ' + 
                        (maxDiskPercent > 80 ? 'critical' : maxDiskPercent > 60 ? 'warning' : 'normal');
                    
                    // 鏇存柊搴旂敤绋嬪簭鐗堟湰
                    document.getElementById('python-version').textContent = data.applications.python || '鏈畨瑁?;
                    document.getElementById('java-version').textContent = data.applications.java || '鏈畨瑁?;
                    document.getElementById('docker-version').textContent = data.applications.docker || '鏈畨瑁?;
                    
                    // 鏇存柊纾佺洏璇︽儏琛ㄦ牸
                    const diskTableBody = document.getElementById('disk-table-body');
                    diskTableBody.innerHTML = '';
                    data.disks.forEach(disk => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${disk.device}</td>
                            <td>${disk.mountpoint}</td>
                            <td>${formatBytes(disk.total)}</td>
                            <td>${formatBytes(disk.used)}</td>
                            <td>${formatBytes(disk.free)}</td>
                            <td>${disk.percent.toFixed(2)}%</td>
                        `;
                        diskTableBody.appendChild(row);
                    });
                })
                .catch(error => {
                    console.error('鑾峰彇绯荤粺淇℃伅澶辫触:', error);
                });
        }
        
        // 缁樺埗鍐呭瓨浣跨敤瓒嬪娍鍥?
        function drawMemoryChart(historyData) {
            if (!historyData || historyData.length === 0) return;
            
            // 鎻愬彇鏃堕棿鍜屽唴瀛樹娇鐢ㄧ巼鏁版嵁
            const timestamps = historyData.map(item => new Date(item.timestamp));
            const memoryPercents = historyData.map(item => item.memory_percent);
            
            // 鍒涘缓鍥捐〃鏁版嵁
            const chartData = [{
                x: timestamps,
                y: memoryPercents,
                type: 'scatter',
                mode: 'lines+markers',
                name: '鍐呭瓨浣跨敤鐜?,
                line: {shape: 'spline'},
                marker: {size: 6}
            }];
            
            // 鍥捐〃甯冨眬
            const layout = {
                title: '鍐呭瓨浣跨敤瓒嬪娍',
                xaxis: {title: '鏃堕棿'},
                yaxis: {title: '浣跨敤鐜?(%)', range: [0, 100]},
                margin: {t: 30, l: 50, r: 30, b: 50}
            };
            
            // 缁樺埗鍥捐〃
            Plotly.newPlot('memory-chart', chartData, layout);
        }
        
        // 缁樺埗纾佺洏浣跨敤瓒嬪娍鍥?
        function drawDiskChart(historyData) {
            if (!historyData || Object.keys(historyData).length === 0) return;
            
            // 鍒涘缓鍥捐〃鏁版嵁
            const chartData = [];
            
            // 涓烘瘡涓鐩樿澶囧垱寤轰竴鏉＄嚎
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
                    line: {shape: 'spline'},
                    marker: {size: 6}
                });
            }
            
            // 鍥捐〃甯冨眬
            const layout = {
                title: '纾佺洏浣跨敤瓒嬪娍',
                xaxis: {title: '鏃堕棿'},
                yaxis: {title: '浣跨敤鐜?(%)', range: [0, 100]},
                margin: {t: 30, l: 50, r: 30, b: 50}
            };
            
            // 缁樺埗鍥捐〃
            Plotly.newPlot('disk-chart', chartData, layout);
        }
        
        // 鏇存柊鍥捐〃鏁版嵁
        function updateCharts() {
            // 鑾峰彇鍐呭瓨鍘嗗彶鏁版嵁
            fetch('/api/memory-info')
                .then(response => response.json())
                .then(data => {
                    if (data.history && data.history.length > 0) {
                        drawMemoryChart(data.history);
                    }
                })
                .catch(error => {
                    console.error('鑾峰彇鍐呭瓨鍘嗗彶鏁版嵁澶辫触:', error);
                });
            
            // 鑾峰彇纾佺洏鍘嗗彶鏁版嵁
            fetch('/api/disk-info')
                .then(response => response.json())
                .then(data => {
                    if (data.history && Object.keys(data.history).length > 0) {
                        drawDiskChart(data.history);
                    }
                })
                .catch(error => {
                    console.error('鑾峰彇纾佺洏鍘嗗彶鏁版嵁澶辫触:', error);
                });
        }
        
        // 鏇存柊杩涚▼鍒楄〃
        function updateProcessList() {
            fetch('/api/processes')
                .then(response => response.json())
                .then(data => {
                    const processTableBody = document.getElementById('process-table-body');
                    processTableBody.innerHTML = '';
                    
                    // 鎸塁PU浣跨敤鐜囨帓搴忥紝鍙栧墠20涓繘绋?
                    const sortedProcesses = data.processes.sort((a, b) => b.cpu_percent - a.cpu_percent).slice(0, 20);
                    
                    sortedProcesses.forEach(proc => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${proc.pid}</td>
                            <td>${proc.name}</td>
                            <td>${proc.status}</td>
                            <td>${proc.cpu_percent.toFixed(2)}</td>
                            <td>${proc.memory_percent.toFixed(2)}</td>
                        `;
                        processTableBody.appendChild(row);
                    });
                })
                .catch(error => {
                    console.error('鑾峰彇杩涚▼鍒楄〃澶辫触:', error);
                });
        }
        
        // 鏍煎紡鍖栧瓧鑺傛暟
        function formatBytes(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // 鍒濆鍖栭〉闈?
        document.addEventListener('DOMContentLoaded', function() {
            // 鍒濇鍔犺浇鏁版嵁
            updateSystemInfo();
            updateProcessList();
            updateCharts(); // 娣诲姞鍥捐〃鏇存柊
            
            // 姣?绉掕嚜鍔ㄥ埛鏂版暟鎹?
            setInterval(() => {
                updateSystemInfo();
                updateProcessList();
                updateCharts(); // 娣诲姞鍥捐〃鏇存柊
            }, 5000);
        });
    </script>
</body>
</html>
