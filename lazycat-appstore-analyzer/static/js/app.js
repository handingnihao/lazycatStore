// 懒猫应用商店数据分析系统 - 前端交互脚本

// 全局变量
let currentPage = 1;
let searchQuery = '';

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化搜索框
    initSearchBox();
    
    // 初始化图表（如果在统计页面）
    if (document.getElementById('statsChart')) {
        initCharts();
    }
    
    // 初始化批量检查（如果在批量检查页面）
    if (document.getElementById('batchCheckForm')) {
        initBatchCheck();
    }
});

// 初始化工具提示
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化搜索框
function initSearchBox() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        // 实时搜索
        let searchTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                searchApps(this.value);
            }, 500);
        });
        
        // 回车搜索
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchApps(this.value);
            }
        });
    }
}

// 搜索应用
function searchApps(query) {
    searchQuery = query;
    currentPage = 1;
    
    // 构建URL
    const params = new URLSearchParams({
        q: query,
        page: currentPage
    });
    
    // 跳转到搜索结果
    window.location.href = '/?' + params.toString();
}

// 删除应用
function deleteApp(appId, appName) {
    if (confirm(`确定要删除应用 "${appName}" 吗？`)) {
        fetch(`/delete/${appId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', '应用删除成功');
                // 移除卡片
                const card = document.getElementById(`app-${appId}`);
                if (card) {
                    card.style.animation = 'fadeOut 0.5s';
                    setTimeout(() => card.remove(), 500);
                }
            } else {
                showToast('error', data.message || '删除失败');
            }
        })
        .catch(error => {
            showToast('error', '删除失败: ' + error);
        });
    }
}

// 批量检查初始化
function initBatchCheck() {
    const form = document.getElementById('batchCheckForm');
    const resultsDiv = document.getElementById('checkResults');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const appsTextarea = document.getElementById('appsTextarea');
        const apps = appsTextarea.value.split('\n').filter(app => app.trim());
        
        if (apps.length === 0) {
            showToast('warning', '请输入应用名称');
            return;
        }
        
        // 显示加载状态
        resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p>正在检查...</p></div>';
        
        // 发送请求
        fetch('/api/batch_check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ apps: apps })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayCheckResults(data.results, data.summary);
            } else {
                showToast('error', data.error || '检查失败');
            }
        })
        .catch(error => {
            showToast('error', '检查失败: ' + error);
        });
    });
}

// 显示批量检查结果
function displayCheckResults(results, summary) {
    const resultsDiv = document.getElementById('checkResults');
    
    // 构建HTML
    let html = `
        <div class="card">
            <div class="card-header">
                <h5>检查结果</h5>
                <div class="row mt-2">
                    <div class="col-md-4">
                        <span class="badge bg-info">总计: ${summary.total}</span>
                    </div>
                    <div class="col-md-4">
                        <span class="badge bg-success">已存在: ${summary.found}</span>
                    </div>
                    <div class="col-md-4">
                        <span class="badge bg-warning">缺失: ${summary.missing}</span>
                    </div>
                </div>
            </div>
            <div class="card-body">
    `;
    
    // 缺失的应用列表
    const missingApps = results.filter(r => !r.found).map(r => r.name);
    
    if (missingApps.length > 0) {
        html += `
            <div class="alert alert-warning">
                <h6>缺失的应用:</h6>
                <ul>
                    ${missingApps.map(app => `<li>${app}</li>`).join('')}
                </ul>
                <button class="btn btn-primary" onclick="batchAddMissing(${JSON.stringify(missingApps).replace(/"/g, '&quot;')})">
                    <i class="fas fa-plus"></i> 一键添加缺失应用
                </button>
                <button class="btn btn-secondary" onclick="copyToClipboard('${missingApps.join('\\n')}')">
                    <i class="fas fa-copy"></i> 复制列表
                </button>
            </div>
        `;
    }
    
    // 详细结果
    html += '<div class="list-group">';
    results.forEach(result => {
        const statusClass = result.found ? 'success' : 'warning';
        const statusIcon = result.found ? 'check-circle' : 'times-circle';
        const statusText = result.found ? '已存在' : '缺失';
        
        html += `
            <div class="list-group-item check-result ${result.found ? 'found' : 'missing'}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <i class="fas fa-${statusIcon} text-${statusClass}"></i>
                        <strong>${result.name}</strong>
                    </div>
                    <span class="badge bg-${statusClass}">${statusText}</span>
                </div>
                ${result.found && result.data ? `
                    <small class="text-muted">
                        下载量: ${result.data.downloads} | 
                        状态: ${result.data.status}
                    </small>
                ` : ''}
            </div>
        `;
    });
    html += '</div></div></div>';
    
    resultsDiv.innerHTML = html;
}

// 批量添加缺失应用
function batchAddMissing(missingApps) {
    if (confirm(`确定要添加 ${missingApps.length} 个缺失应用吗？`)) {
        fetch('/batch_add_missing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ missing_apps: missingApps })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('success', `成功添加 ${data.summary.added_count} 个应用`);
                if (data.summary.skipped_count > 0) {
                    showToast('info', `跳过 ${data.summary.skipped_count} 个已存在的应用`);
                }
            } else {
                showToast('error', data.error || '添加失败');
            }
        })
        .catch(error => {
            showToast('error', '添加失败: ' + error);
        });
    }
}

// 复制到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('success', '已复制到剪贴板');
    }).catch(err => {
        showToast('error', '复制失败: ' + err);
    });
}

// 显示提示消息
function showToast(type, message) {
    // 创建提示元素
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // 自动移除
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// 初始化图表
function initCharts() {
    // 这里可以使用Chart.js或其他图表库
    // 示例代码（需要引入Chart.js库）
    const ctx = document.getElementById('statsChart');
    if (ctx && typeof Chart !== 'undefined') {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [], // 从API获取
                datasets: [{
                    label: '下载量',
                    data: [], // 从API获取
                    backgroundColor: 'rgba(74, 144, 226, 0.5)',
                    borderColor: 'rgba(74, 144, 226, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

// 动画效果
@keyframes fadeOut {
    from {
        opacity: 1;
        transform: translateX(0);
    }
    to {
        opacity: 0;
        transform: translateX(-100%);
    }
}