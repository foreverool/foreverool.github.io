// 打赏功能独立JS - IIFE 隔离作用域，避免全局变量污染
(function() {
  // 等待DOM加载完成后执行
  document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素（使用唯一类名，避免与主题冲突）
    const coffeeButton = document.querySelector('.toha-donate-coffee-btn');
    const tipModal = document.querySelector('.toha-donate-modal');
    const closeButton = document.querySelector('.toha-donate-close-btn');
    const paymentItems = document.querySelectorAll('.toha-donate-payment-item');

    // 校验元素是否存在（避免报错）
    if (!coffeeButton || !tipModal || !closeButton) return;

    // 打开模态窗口
    coffeeButton.addEventListener('click', function() {
      tipModal.classList.add('active');
      document.documentElement.style.overflow = 'hidden'; // 禁止背景滚动（兼容多浏览器）
    });

    // 关闭模态窗口
    function closeModal() {
      tipModal.classList.remove('active');
      document.documentElement.style.overflow = ''; // 恢复背景滚动
    }

    // 点击关闭按钮关闭
    closeButton.addEventListener('click', closeModal);

    // 点击模态窗口外部关闭
    tipModal.addEventListener('click', function(e) {
      if (e.target === tipModal) {
        closeModal();
      }
    });

    // 按ESC键关闭
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && tipModal.classList.contains('active')) {
        closeModal();
      }
    });

    // 支付项点击效果（可选，不影响核心功能）
    paymentItems.forEach(function(item) {
      item.addEventListener('click', function() {
        // 点击缩放效果
        item.classList.add('scale-95');
        setTimeout(function() {
          item.classList.remove('scale-95');
        }, 150);

        // 提示信息（可自定义）
        const paymentName = item.querySelector('.toha-donate-payment-name').textContent;
        alert(`请使用${paymentName}扫描二维码进行支付，感谢您的支持！`);
      });
    });
  });
})();