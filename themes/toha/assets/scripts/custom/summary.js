async function loadSummaries() {
    try {
        const response = await fetch('/assets/summaries.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const summaries = await response.json();
        console.log(summaries); // 这里得到的是 JavaScript 对象
        // 接下来可以调用函数将数据显示在页面上
        displaySummaries(summaries);
    } catch (error) {
        console.error('加载摘要失败：', error);
    }
}

function displaySummaries(summaries) {
    const container = document.getElementById('summary-container');
    // 假设 summaries 是一个对象，键是文章名，值是摘要
    for (const [slug, summary] of Object.entries(summaries)) {
        const div = document.createElement('div');
        div.innerHTML = `<strong>${slug}</strong>: ${summary}`;
        container.appendChild(div);
    }
}

// 页面加载完成后调用
window.addEventListener('DOMContentLoaded', loadSummaries);