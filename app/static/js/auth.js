// Система аутентификации для сайта "Фолиант"

let currentUser = null;
let availableRoles = [];

// Инициализация системы аутентификации
function initAuth() {
    console.log('Инициализация системы аутентификации...');
    
    // Загружаем список ролей
    loadRoles();
    
    // Настройка обработчиков событий
    setupAuthEventListeners();
    
    // Проверяем, авторизован ли пользователь
    checkAuthStatus();
}

// Загрузка списка ролей из API
function loadRoles() {
    fetch('/roles/?skip=0&limit=100')
        .then(response => {
            if (!response.ok) {
                console.warn('Не удалось загрузить роли, статус:', response.status);
                return [];
            }
            return response.json();
        })
        .then(roles => {
            availableRoles = roles || [];
            console.log('Загружены роли:', availableRoles);
        })
        .catch(error => {
            console.error('Ошибка загрузки ролей:', error);
            availableRoles = [];
        });
}

// Проверка статуса аутентификации
function checkAuthStatus() {
    const userId = localStorage.getItem('user_id');
    const userEmail = localStorage.getItem('user_email');
    const userName = localStorage.getItem('user_name');
    
    if (userId && userEmail) {
        currentUser = {
            id: parseInt(userId),
            email: userEmail,
            name: userName || userEmail
        };
        updateUIForAuthUser();
        console.log('Пользователь авторизован:', currentUser);
    } else {
        currentUser = null;
        updateUIForGuest();
        console.log('Пользователь не авторизован');
    }
}

// Обновление UI для авторизованного пользователя
function updateUIForAuthUser() {
    const loginBtn = document.getElementById('btnLogin');
    const registerBtn = document.getElementById('btnRegister');
    const userBadge = document.getElementById('userBadge');
    const userNameSpan = document.getElementById('userName');
    const logoutBtn = document.getElementById('btnLogout');
    
    if (loginBtn) loginBtn.style.display = 'none';
    if (registerBtn) registerBtn.style.display = 'none';
    if (userBadge) userBadge.style.display = 'block';
    if (userNameSpan) userNameSpan.textContent = currentUser.name;
    
    // Настройка кнопки выхода
    if (logoutBtn) {
        logoutBtn.onclick = function(e) {
            e.preventDefault();
            logout();
        };
    }
    
    // Обновляем доступные действия
    enableUserFeatures();
}

// Обновление UI для гостя
function updateUIForGuest() {
    const loginBtn = document.getElementById('btnLogin');
    const registerBtn = document.getElementById('btnRegister');
    const userBadge = document.getElementById('userBadge');
    
    if (loginBtn) loginBtn.style.display = 'block';
    if (registerBtn) registerBtn.style.display = 'block';
    if (userBadge) userBadge.style.display = 'none';
    
    // Отключаем функции, требующие авторизации
    disableUserFeatures();
}

// Настройка обработчиков событий
function setupAuthEventListeners() {
    // Кнопка "Войти"
    const loginBtn = document.getElementById('btnLogin');
    if (loginBtn) {
        loginBtn.addEventListener('click', showLoginModal);
    }
    
    // Кнопка "Регистрация"
    const registerBtn = document.getElementById('btnRegister');
    if (registerBtn) {
        registerBtn.addEventListener('click', showRegisterModal);
    }
    
    // Закрытие модального окна
    const authClose = document.getElementById('authClose');
    if (authClose) {
        authClose.addEventListener('click', hideAuthModal);
    }
    
    // Кнопка отмены
    const authCancel = document.getElementById('authCancel');
    if (authCancel) {
        authCancel.addEventListener('click', hideAuthModal);
    }
    
    // Отправка формы
    const authSubmit = document.getElementById('authSubmit');
    if (authSubmit) {
        authSubmit.removeEventListener('click', handleLogin);
        authSubmit.removeEventListener('click', handleRegister);
        // Будем добавлять обработчик в зависимости от типа формы
    }
    
    // Закрытие по клику вне модального окна
    const authModal = document.getElementById('authModal');
    if (authModal) {
        authModal.addEventListener('click', function(e) {
            if (e.target === this) {
                hideAuthModal();
            }
        });
    }
}

// Показать модальное окно входа
function showLoginModal() {
    const modal = document.getElementById('authModal');
    const modalTitle = document.getElementById('modalTitle');
    const authContent = document.getElementById('authContent');
    const authSubmit = document.getElementById('authSubmit');
    
    // Очищаем содержимое
    if (authContent) authContent.innerHTML = '';
    
    // Устанавливаем заголовок
    if (modalTitle) modalTitle.textContent = 'Вход в систему';
    
    // Создаем форму входа
    const formHtml = `
        <div class="auth-fields">
            <label>
                Email
                <input type="email" id="authEmail" placeholder="Ваш email" required>
                <div class="validation-message" id="emailError"></div>
            </label>
            <label>
                Пароль
                <input type="password" id="authPassword" placeholder="Ваш пароль" required>
                <div class="validation-message" id="passwordError"></div>
            </label>
        </div>
    `;
    
    // Вставляем форму
    if (authContent) {
        authContent.innerHTML = formHtml;
    }
    
    // Устанавливаем текст кнопки и обработчик
    if (authSubmit) {
        authSubmit.textContent = 'Войти';
        // Удаляем старые обработчики
        authSubmit.removeEventListener('click', handleLogin);
        authSubmit.removeEventListener('click', handleRegister);
        // Добавляем новый
        authSubmit.addEventListener('click', handleLogin);
    }
    
    // Показываем модальное окно
    if (modal) {
        modal.setAttribute('aria-hidden', 'false');
        // Фокусируемся на поле email
        setTimeout(() => {
            const emailInput = document.getElementById('authEmail');
            if (emailInput) emailInput.focus();
        }, 100);
    }
}

// Показать модальное окно регистрации
function showRegisterModal() {
    const modal = document.getElementById('authModal');
    const modalTitle = document.getElementById('modalTitle');
    const authContent = document.getElementById('authContent');
    const authSubmit = document.getElementById('authSubmit');
    
    // Очищаем содержимое
    if (authContent) authContent.innerHTML = '';
    
    // Устанавливаем заголовок
    if (modalTitle) modalTitle.textContent = 'Регистрация';
    
    // Создаем форму регистрации
    let roleOptions = '<option value="">Выберите роль</option>';
    if (availableRoles.length > 0) {
        availableRoles.forEach(role => {
            roleOptions += `<option value="${role.id}">${role.name}</option>`;
        });
    } else {
        roleOptions = '<option value="" disabled>Роли не загружены</option>';
    }
    
    const formHtml = `
        <div class="auth-fields">
            <label>
                Имя
                <input type="text" id="regName" placeholder="Ваше имя" required>
                <div class="validation-message" id="nameError"></div>
            </label>
            <label>
                Email
                <input type="email" id="regEmail" placeholder="Ваш email" required>
                <div class="validation-message" id="regEmailError"></div>
            </label>
            <label>
                Пароль
                <input type="password" id="regPassword" placeholder="Пароль (мин. 6 символов)" required minlength="6">
                <div class="validation-message" id="regPasswordError"></div>
            </label>
            <label>
                Подтверждение пароля
                <input type="password" id="regConfirmPassword" placeholder="Повторите пароль" required>
                <div class="validation-message" id="confirmPasswordError"></div>
            </label>
            <label>
                Роль
                <select id="regRole" required>
                    ${roleOptions}
                </select>
                <div class="validation-message" id="roleError"></div>
            </label>
            ${availableRoles.length === 0 ? '<div class="role-info">Роли не загружены. Сначала создайте роли через API.</div>' : ''}
        </div>
    `;
    
    // Вставляем форму
    if (authContent) {
        authContent.innerHTML = formHtml;
    }
    
    // Устанавливаем текст кнопки и обработчик
    if (authSubmit) {
        authSubmit.textContent = 'Зарегистрироваться';
        // Удаляем старые обработчики
        authSubmit.removeEventListener('click', handleLogin);
        authSubmit.removeEventListener('click', handleRegister);
        // Добавляем новый
        authSubmit.addEventListener('click', handleRegister);
    }
    
    // Показываем модальное окно
    if (modal) {
        modal.setAttribute('aria-hidden', 'false');
        // Фокусируемся на поле имени
        setTimeout(() => {
            const nameInput = document.getElementById('regName');
            if (nameInput) nameInput.focus();
        }, 100);
    }
}

// Скрыть модальное окно
function hideAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.setAttribute('aria-hidden', 'true');
    }
}

// Обработка входа
async function handleLogin() {
    const authContent = document.getElementById('authContent');
    if (!authContent) {
        console.error('Не найден элемент authContent');
        return;
    }
    
    const email = authContent.querySelector('#authEmail');
    const password = authContent.querySelector('#authPassword');
    const submitBtn = document.getElementById('authSubmit');
    
    // Проверяем, что элементы найдены
    if (!email || !password || !submitBtn) {
        console.error('Не найдены элементы формы входа');
        return;
    }
    
    // Валидация
    let isValid = true;
    
    // Валидация email
    if (!email.value || !isValidEmail(email.value)) {
        showValidationError('emailError', 'Введите корректный email');
        isValid = false;
    } else {
        clearValidationError('emailError');
    }
    
    // Валидация пароля
    if (!password.value) {
        showValidationError('passwordError', 'Введите пароль');
        isValid = false;
    } else {
        clearValidationError('passwordError');
    }
    
    if (!isValid) {
        return;
    }
    
    // Показываем индикатор загрузки
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Вход...';
    submitBtn.classList.add('auth-submit-loading');
    submitBtn.disabled = true;
    
    try {
        // Отправляем запрос на вход
        const loginUrl = `/users/login?email=${encodeURIComponent(email.value)}&password=${encodeURIComponent(password.value)}`;
        console.log('Отправка запроса на вход:', loginUrl);
        
        const response = await fetch(loginUrl, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
            }
        });
        
        console.log('Ответ сервера:', response.status);
        
        if (response.status === 401) {
            showAuthMessage('Неверный email или пароль', 'error');
            return;
        }
        
        if (!response.ok) {
            let errorMessage = 'Ошибка входа';
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    errorMessage = typeof errorData.detail === 'string' 
                        ? errorData.detail 
                        : 'Ошибка аутентификации';
                }
            } catch (e) {
                errorMessage = `Ошибка ${response.status}`;
            }
            
            showAuthMessage(errorMessage, 'error');
            return;
        }
        
        const data = await response.json();
        console.log('Успешный вход:', data);
        
        // Сохраняем данные пользователя
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('user_email', data.email || email.value);
        
        // Получаем информацию о пользователе для имени
        try {
            const userResponse = await fetch(`/users/${data.user_id}`);
            if (userResponse.ok) {
                const userData = await userResponse.json();
                localStorage.setItem('user_name', userData.name);
            }
        } catch (e) {
            console.warn('Не удалось получить имя пользователя:', e);
        }
        
        // Обновляем UI
        checkAuthStatus();
        
        // Показываем сообщение об успехе
        showAuthMessage('Вход выполнен успешно!', 'success');
        
        // Закрываем модальное окно через 1.5 секунды
        setTimeout(() => {
            hideAuthModal();
        }, 1500);
        
    } catch (error) {
        console.error('Ошибка сети:', error);
        showAuthMessage('Ошибка соединения с сервером', 'error');
    } finally {
        // Восстанавливаем кнопку
        submitBtn.textContent = originalText;
        submitBtn.classList.remove('auth-submit-loading');
        submitBtn.disabled = false;
    }
}

// Обработка регистрации
async function handleRegister() {
    const authContent = document.getElementById('authContent');
    if (!authContent) {
        console.error('Не найден элемент authContent');
        return;
    }
    
    const name = authContent.querySelector('#regName');
    const email = authContent.querySelector('#regEmail');
    const password = authContent.querySelector('#regPassword');
    const confirmPassword = authContent.querySelector('#regConfirmPassword');
    const role = authContent.querySelector('#regRole');
    const submitBtn = document.getElementById('authSubmit');
    
    // Проверяем, что элементы найдены
    if (!name || !email || !password || !confirmPassword || !role || !submitBtn) {
        console.error('Не найдены элементы формы регистрации');
        return;
    }
    
    // Валидация
    let isValid = true;
    
    // Валидация имени
    if (!name.value.trim()) {
        showValidationError('nameError', 'Введите ваше имя');
        isValid = false;
    } else {
        clearValidationError('nameError');
    }
    
    // Валидация email
    if (!email.value || !isValidEmail(email.value)) {
        showValidationError('regEmailError', 'Введите корректный email');
        isValid = false;
    } else {
        clearValidationError('regEmailError');
    }
    
    // Валидация пароля
    if (!password.value || password.value.length < 6) {
        showValidationError('regPasswordError', 'Пароль должен содержать минимум 6 символов');
        isValid = false;
    } else {
        clearValidationError('regPasswordError');
    }
    
    // Проверка совпадения паролей
    if (!confirmPassword.value || password.value !== confirmPassword.value) {
        showValidationError('confirmPasswordError', 'Пароли не совпадают');
        isValid = false;
    } else {
        clearValidationError('confirmPasswordError');
    }
    
    // Валидация роли
    if (!role.value) {
        showValidationError('roleError', 'Выберите роль');
        isValid = false;
    } else {
        clearValidationError('roleError');
    }
    
    if (!isValid) {
        return;
    }
    
    // Показываем индикатор загрузки
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Регистрация...';
    submitBtn.classList.add('auth-submit-loading');
    submitBtn.disabled = true;
    
    try {
        // Подготавливаем данные для регистрации
        const userData = {
            name: name.value.trim(),
            email: email.value,
            password: password.value,
            role_id: parseInt(role.value)
        };
        
        console.log('Отправка данных регистрации:', userData);
        
        const response = await fetch('/users/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        console.log('Ответ сервера:', response.status);
        
        if (!response.ok) {
            let errorMessage = 'Ошибка регистрации';
            try {
                const errorData = await response.json();
                console.error('Данные ошибки:', errorData);
                
                if (errorData.detail) {
                    if (typeof errorData.detail === 'string') {
                        errorMessage = errorData.detail;
                    } else if (Array.isArray(errorData.detail)) {
                        errorMessage = errorData.detail.map(err => err.msg || err).join(', ');
                    } else if (typeof errorData.detail === 'object') {
                        errorMessage = JSON.stringify(errorData.detail);
                    }
                }
            } catch (e) {
                errorMessage = `Ошибка ${response.status}`;
            }
            
            showAuthMessage(errorMessage, 'error');
            return;
        }
        
        const data = await response.json();
        console.log('Успешная регистрация:', data);
        
        // Сохраняем данные пользователя
        localStorage.setItem('user_id', data.id);
        localStorage.setItem('user_email', data.email);
        localStorage.setItem('user_name', data.name);
        
        // Обновляем UI
        checkAuthStatus();
        
        // Показываем сообщение об успехе
        showAuthMessage('Регистрация успешна! Теперь вы можете войти.', 'success');
        
        // Переключаемся на форму входа через 2 секунды
        setTimeout(() => {
            showLoginModal();
            // Автозаполняем email в форме входа
            const authContentNew = document.getElementById('authContent');
            if (authContentNew) {
                const loginEmail = authContentNew.querySelector('#authEmail');
                if (loginEmail) {
                    loginEmail.value = email.value;
                }
            }
        }, 2000);
        
    } catch (error) {
        console.error('Ошибка сети:', error);
        showAuthMessage('Ошибка соединения с сервером', 'error');
    } finally {
        // Восстанавливаем кнопку
        submitBtn.textContent = originalText;
        submitBtn.classList.remove('auth-submit-loading');
        submitBtn.disabled = false;
    }
}

// Выход из системы
function logout() {
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    
    currentUser = null;
    updateUIForGuest();
    
    // Показываем сообщение об успешном выходе
    if (window.showNotification) {
        window.showNotification('Вы успешно вышли из системы', 'info');
    }
    
    // Перезагружаем страницу для обновления данных
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

// Вспомогательные функции
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showValidationError(elementId, message) {
    const authContent = document.getElementById('authContent');
    if (authContent) {
        const element = authContent.querySelector(`#${elementId}`);
        if (element) {
            element.textContent = message;
            element.className = 'validation-message error';
            
            // Подсвечиваем поле ввода
            const input = element.closest('label').querySelector('input, select');
            if (input) {
                input.classList.add('error');
                input.classList.remove('success');
            }
        }
    }
}

function clearValidationError(elementId) {
    const authContent = document.getElementById('authContent');
    if (authContent) {
        const element = authContent.querySelector(`#${elementId}`);
        if (element) {
            element.textContent = '';
            element.className = 'validation-message';
            
            // Убираем подсветку с поля ввода
            const input = element.closest('label').querySelector('input, select');
            if (input) {
                input.classList.remove('error');
                input.classList.remove('success');
            }
        }
    }
}

function showAuthMessage(message, type = 'info') {
    const authContent = document.getElementById('authContent');
    if (authContent) {
        // Создаем элемент для сообщения
        let messageEl = authContent.querySelector('.auth-message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.className = 'auth-message';
            authContent.prepend(messageEl);
        }
        
        messageEl.textContent = message;
        messageEl.className = `auth-message ${type}`;
        messageEl.style.cssText = `
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 15px;
            font-size: 14px;
            border-left: 4px solid;
        `;
        
        if (type === 'error') {
            messageEl.style.background = 'linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%)';
            messageEl.style.color = '#721c24';
            messageEl.style.borderLeftColor = '#dc3545';
        } else if (type === 'success') {
            messageEl.style.background = 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)';
            messageEl.style.color = '#155724';
            messageEl.style.borderLeftColor = '#28a745';
        } else {
            messageEl.style.background = 'linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%)';
            messageEl.style.color = '#856404';
            messageEl.style.borderLeftColor = '#ffc107';
        }
        
        // Автоматическое скрытие через 5 секунд (кроме ошибок)
        if (type !== 'error') {
            setTimeout(() => {
                if (messageEl && messageEl.parentNode) {
                    messageEl.remove();
                }
            }, 5000);
        }
    }
}

// Функции для включения/отключения возможностей для пользователя
function enableUserFeatures() {
    // Здесь можно включить функции, доступные только авторизованным пользователям
    console.log('Включение функций для авторизованного пользователя');
    
    // Пример: показываем кнопку выхода
    const logoutBtn = document.getElementById('btnLogout');
    if (logoutBtn) {
        logoutBtn.style.display = 'inline-block';
    }
}

function disableUserFeatures() {
    // Здесь можно отключить функции, доступные только авторизованным пользователям
    console.log('Отключение функций для гостя');
    
    // Пример: скрываем кнопку выхода
    const logoutBtn = document.getElementById('btnLogout');
    if (logoutBtn) {
        logoutBtn.style.display = 'none';
    }
}

// Экспортируем функции для использования в других модулях
window.authSystem = {
    init: initAuth,
    login: showLoginModal,
    register: showRegisterModal,
    logout: logout,
    getUser: () => currentUser,
    isAuthenticated: () => currentUser !== null
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Даем время на загрузку DOM
    setTimeout(initAuth, 100);
});

// Для отладки
console.log('Модуль аутентификации загружен');