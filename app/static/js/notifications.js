// Система уведомлений
class NotificationSystem {
    constructor() {
        this.container = null;
        this.init();
    }
    
    init() {
        // Создаем контейнер для уведомлений
        this.container = document.createElement('div');
        this.container.id = 'notifications-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 350px;
        `;
        document.body.appendChild(this.container);
    }
    
    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            padding: 12px 20px;
            background: ${this.getBackgroundColor(type)};
            color: ${this.getTextColor(type)};
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-left: 4px solid ${this.getBorderColor(type)};
            animation: slideInRight 0.3s ease;
            font-size: 14px;
            line-height: 1.4;
        `;
        
        this.container.appendChild(notification);
        
        // Автоматическое скрытие
        if (duration > 0) {
            setTimeout(() => {
                this.hide(notification);
            }, duration);
        }
        
        // Кнопка закрытия
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: none;
            border: none;
            color: inherit;
            cursor: pointer;
            font-size: 18px;
            line-height: 1;
            opacity: 0.7;
        `;
        closeBtn.addEventListener('click', () => this.hide(notification));
        notification.appendChild(closeBtn);
        
        return notification;
    }
    
    hide(notification) {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    getBackgroundColor(type) {
        const colors = {
            success: 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
            error: 'linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)',
            warning: 'linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%)',
            info: 'linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%)'
        };
        return colors[type] || colors.info;
    }
    
    getTextColor(type) {
        const colors = {
            success: '#155724',
            error: '#721c24',
            warning: '#856404',
            info: '#0c5460'
        };
        return colors[type] || colors.info;
    }
    
    getBorderColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }
}

// Добавляем CSS анимации
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(notificationStyles);

// Создаем глобальный экземпляр
window.notifications = new NotificationSystem();

// Функция-помощник для быстрого вызова
function showNotification(message, type = 'info', duration = 3000) {
    return window.notifications.show(message, type, duration);
}

// Экспортируем
window.showNotification = showNotification;