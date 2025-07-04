// 配置
function getApiBaseUrl() {
    // 如果是file://协议（直接打开HTML文件），使用localhost
    if (window.location.protocol === 'file:') {
        return 'http://localhost:8000';
    }
    // 如果是开发环境（localhost:8080），使用localhost:8000
    if (window.location.hostname === 'localhost' && window.location.port === '8080') {
        return 'http://localhost:8000';
    }
    // 生产环境，使用相对路径
    return window.location.protocol + '//' + window.location.hostname + (window.location.port ? ':' + window.location.port : '');
}

const API_BASE_URL = getApiBaseUrl();

// 全局变量
let currentQuote = null;

// DOM元素
const loadingState = document.getElementById('loadingState');
const quoteCard = document.getElementById('quoteCard');
const errorState = document.getElementById('errorState');
const quoteDate = document.getElementById('quoteDate');
const quoteContent = document.getElementById('quoteContent');
const quoteAuthor = document.getElementById('quoteAuthor');
const errorMessage = document.getElementById('errorMessage');
const historyModal = document.getElementById('historyModal');
const historyContent = document.getElementById('historyContent');

// 按钮元素
const historyBtn = document.getElementById('historyBtn');
const copyBtn = document.getElementById('copyBtn');
const retryBtn = document.getElementById('retryBtn');
const closeHistoryBtn = document.getElementById('closeHistoryBtn');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化...');
    console.log('API_BASE_URL:', API_BASE_URL);
    loadTodayQuote();
    bindEvents();
    console.log('初始化完成');
});

// 绑定事件
function bindEvents() {
    historyBtn.addEventListener('click', showHistory);
    copyBtn.addEventListener('click', copyQuote);
    retryBtn.addEventListener('click', loadTodayQuote);
    closeHistoryBtn.addEventListener('click', hideHistory);

    // 点击模态框背景关闭
    historyModal.addEventListener('click', function(e) {
        if (e.target === historyModal) {
            hideHistory();
        }
    });
}

// 加载今日语录
async function loadTodayQuote() {
    showLoading();

    try {
        console.log('API_BASE_URL:', API_BASE_URL);
        console.log('请求URL:', `${API_BASE_URL}/api/quote`);

        const response = await fetch(`${API_BASE_URL}/api/quote`);
        console.log('Response:', response);

        const result = await response.json();
        console.log('Result:', result);

        if (result.success && result.data) {
            currentQuote = result.data;
            displayQuote(currentQuote);
        } else {
            showError(result.message || '获取语录失败');
        }
    } catch (error) {
        console.error('获取语录失败:', error);
        showError('网络连接失败，请检查网络后重试');
    }
}

// 显示语录
function displayQuote(quote) {
    quoteContent.textContent = quote.content;
    quoteAuthor.textContent = `—— ${quote.author}`;
    quoteDate.textContent = formatDate(quote.date);

    hideLoading();
    hideError();
    showQuote();
}

// 显示加载状态
function showLoading() {
    loadingState.classList.remove('hidden');
    quoteCard.classList.add('hidden');
    errorState.classList.add('hidden');
}

// 隐藏加载状态
function hideLoading() {
    loadingState.classList.add('hidden');
}

// 显示语录卡片
function showQuote() {
    quoteCard.classList.remove('hidden');
    quoteCard.classList.add('fade-in');
}

// 显示错误状态
function showError(message) {
    errorMessage.textContent = message;
    hideLoading();
    quoteCard.classList.add('hidden');
    errorState.classList.remove('hidden');
}

// 隐藏错误状态
function hideError() {
    errorState.classList.add('hidden');
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();

    const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
    const weekday = weekdays[date.getDay()];

    return `${year}年${month}月${day}日 星期${weekday}`;
}

// 复制语录
function copyQuote() {
    if (!currentQuote) return;

    const copyText = `${currentQuote.content}\n—— ${currentQuote.author}`;
    copyToClipboard(copyText);
    showToast('语录已复制');
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).catch(console.error);
    } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
}

// 显示历史语录
async function showHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/quotes/recent?limit=20`);
        const result = await response.json();

        if (result.success && result.data) {
            displayHistory(result.data);
            historyModal.classList.remove('hidden');
        } else {
            showToast('获取历史语录失败');
        }
    } catch (error) {
        console.error('获取历史语录失败:', error);
        showToast('网络连接失败');
    }
}

// 显示历史语录列表
function displayHistory(quotes) {
    historyContent.innerHTML = '';

    if (quotes.length === 0) {
        historyContent.innerHTML = '<p class="text-gray-400 text-center py-8 text-sm">暂无历史语录</p>';
        return;
    }

    quotes.forEach(quote => {
        const quoteElement = document.createElement('div');
        quoteElement.className = 'border-b border-gray-100 pb-3 mb-3 last:border-b-0 last:mb-0';
        quoteElement.innerHTML = `
            <div class="text-xs text-gray-400 mb-2">${formatDate(quote.date)}</div>
            <blockquote class="text-gray-700 text-sm mb-2 leading-relaxed">${quote.content}</blockquote>
            <cite class="text-xs text-gray-500">—— ${quote.author}</cite>
        `;
        historyContent.appendChild(quoteElement);
    });
}

// 隐藏历史语录模态框
function hideHistory() {
    historyModal.classList.add('hidden');
}

// 显示提示消息
function showToast(message) {
    // 创建提示元素
    const toast = document.createElement('div');
    toast.className = 'fixed top-8 left-1/2 transform -translate-x-1/2 bg-black/80 text-white px-4 py-2 rounded-full text-sm shadow-lg z-50 transition-all duration-300';
    toast.textContent = message;
    toast.style.opacity = '0';
    toast.style.transform = 'translate(-50%, -20px)';

    document.body.appendChild(toast);

    // 显示动画
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translate(-50%, 0)';
    }, 10);

    // 2秒后自动消失
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translate(-50%, -20px)';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 2000);
}
