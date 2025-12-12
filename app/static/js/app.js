// Основной файл приложения "Фолиант"
import './auth.js';

// Глобальные переменные
let books = [];
let filteredBooks = [];
let currentPage = 1;
const booksPerPage = 12;
let currentSort = 'title';
let currentFilters = {
    yearFrom: null,
    yearTo: null
};

// DOM элементы
const elements = {
    bookGrid: null,
    searchInput: null,
    sortSelect: null,
    yearFromInput: null,
    yearToInput: null,
    applyFiltersBtn: null,
    clearFiltersBtn: null,
    prevPageBtn: null,
    nextPageBtn: null,
    pageInfo: null,
    totalCount: null,
    viewInfo: null,
    addRandomBtn: null,
    statsEl: null
};

// Инициализация приложения
async function init() {
    console.log('Инициализация приложения "Фолиант"...');
    
    // Получаем все DOM элементы
    cacheElements();
    
    // Проверяем наличие элементов
    if (!elements.bookGrid) {
        console.error('Основной элемент bookGrid не найден');
        return;
    }
    
    // Устанавливаем текущий год в футере
    document.getElementById('year').textContent = new Date().getFullYear();
    
    // Инициализация системы аутентификации
    if (window.authSystem) {
        window.authSystem.init();
    } else {
        console.error('Модуль аутентификации не найден');
    }
    
    // Инициализация системы уведомлений
    initNotifications();
    
    // Настройка обработчиков событий
    setupEventListeners();
    
    // Загружаем данные
    await loadData();
    
    // Первоначальная отрисовка
    renderBooks();
    updatePagination();
    updateStats();
    
    console.log('Приложение инициализировано');
}

// Кэширование DOM элементов
function cacheElements() {
    elements.bookGrid = document.getElementById('bookGrid');
    elements.searchInput = document.getElementById('search');
    elements.sortSelect = document.getElementById('sort');
    elements.yearFromInput = document.getElementById('yearFrom');
    elements.yearToInput = document.getElementById('yearTo');
    elements.applyFiltersBtn = document.getElementById('applyFilters');
    elements.clearFiltersBtn = document.getElementById('clearFilters');
    elements.prevPageBtn = document.getElementById('prevPage');
    elements.nextPageBtn = document.getElementById('nextPage');
    elements.pageInfo = document.getElementById('pageInfo');
    elements.totalCount = document.getElementById('totalCount');
    elements.viewInfo = document.getElementById('viewInfo');
    elements.addRandomBtn = document.getElementById('addRandom');
    elements.statsEl = document.getElementById('stats');
}

// Инициализация системы уведомлений
function initNotifications() {
    if (!window.showNotification) {
        // Создаем простую систему уведомлений, если её нет
        window.showNotification = function(message, type = 'info', duration = 3000) {
            console.log(`[${type.toUpperCase()}] ${message}`);
            
            // Создаем уведомление в DOM
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                background: ${type === 'success' ? '#d4edda' : 
                            type === 'error' ? '#f8d7da' : 
                            type === 'warning' ? '#fff3cd' : '#d1ecf1'};
                color: ${type === 'success' ? '#155724' : 
                        type === 'error' ? '#721c24' : 
                        type === 'warning' ? '#856404' : '#0c5460'};
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                animation: slideInRight 0.3s ease;
                max-width: 300px;
            `;
            
            document.body.appendChild(notification);
            
            // Удаляем через указанное время
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, duration);
        };
        
        // Добавляем стили для анимаций
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Поиск
    if (elements.searchInput) {
        elements.searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Сортировка
    if (elements.sortSelect) {
        elements.sortSelect.addEventListener('change', handleSortChange);
    }
    
    // Фильтры
    if (elements.applyFiltersBtn) {
        elements.applyFiltersBtn.addEventListener('click', applyFilters);
    }
    
    if (elements.clearFiltersBtn) {
        elements.clearFiltersBtn.addEventListener('click', clearFilters);
    }
    
    // Пагинация
    if (elements.prevPageBtn) {
        elements.prevPageBtn.addEventListener('click', goToPrevPage);
    }
    
    if (elements.nextPageBtn) {
        elements.nextPageBtn.addEventListener('click', goToNextPage);
    }
    
    // Добавление случайной книги
    if (elements.addRandomBtn) {
        elements.addRandomBtn.addEventListener('click', addRandomBook);
    }
    
    // Обработка клавиатуры
    document.addEventListener('keydown', handleKeyDown);
}

// Загрузка данных
async function loadData() {
    try {
        showNotification('Загрузка данных...', 'info');
        
        // Загружаем книги
        const booksResponse = await fetch('/books/?skip=0&limit=1000');
        if (!booksResponse.ok) throw new Error('Ошибка загрузки книг');
        books = await booksResponse.json();
        
        // Загружаем авторов
        const authorsResponse = await fetch('/authors/?skip=0&limit=1000');
        const authors = authorsResponse.ok ? await authorsResponse.json() : [];
        
        // Загружаем жанры
        const genresResponse = await fetch('/genres/?skip=0&limit=1000');
        const genres = genresResponse.ok ? await genresResponse.json() : [];
        
        // Обогащаем книги данными авторов и жанров
        books.forEach(book => {
            const author = authors.find(a => a.id === book.author_id);
            const genre = genres.find(g => g.id === book.genre_id);
            
            book.author_name = author ? author.name : 'Неизвестный автор';
            book.genre_name = genre ? genre.name : 'Неизвестный жанр';
        });
        
        // Загружаем комментарии для каждой книги
        await loadCommentsForBooks();
        
        filteredBooks = [...books];
        
        showNotification(`Загружено ${books.length} книг`, 'success');
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        showNotification('Ошибка загрузки данных', 'error');
        
        // Используем тестовые данные, если API недоступно
        books = getMockBooks();
        filteredBooks = [...books];
        showNotification('Используются тестовые данные', 'warning');
    }
}

// Загрузка комментариев для книг
async function loadCommentsForBooks() {
    try {
        const commentsResponse = await fetch('/book-comments/?skip=0&limit=1000');
        if (!commentsResponse.ok) return;
        
        const comments = await commentsResponse.json();
        
        // Группируем комментарии по book_id
        const commentsByBookId = {};
        comments.forEach(comment => {
            if (!commentsByBookId[comment.book_id]) {
                commentsByBookId[comment.book_id] = [];
            }
            commentsByBookId[comment.book_id].push(comment);
        });
        
        // Добавляем комментарии к книгам
        books.forEach(book => {
            book.comments = commentsByBookId[book.id] || [];
        });
        
    } catch (error) {
        console.error('Ошибка загрузки комментариев:', error);
    }
}

// Обработка поиска
function handleSearch() {
    const searchTerm = elements.searchInput.value.toLowerCase().trim();
    
    if (!searchTerm) {
        filteredBooks = [...books];
    } else {
        filteredBooks = books.filter(book => 
            book.title.toLowerCase().includes(searchTerm) ||
            (book.author_name && book.author_name.toLowerCase().includes(searchTerm)) ||
            (book.description && book.description.toLowerCase().includes(searchTerm))
        );
    }
    
    currentPage = 1;
    applySorting();
    renderBooks();
    updatePagination();
    updateStats();
}

// Обработка изменения сортировки
function handleSortChange() {
    currentSort = elements.sortSelect.value;
    applySorting();
    renderBooks();
}

// Применение сортировки
function applySorting() {
    switch(currentSort) {
        case 'title':
            filteredBooks.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'author':
            filteredBooks.sort((a, b) => a.author_name.localeCompare(b.author_name));
            break;
        case 'genre':
            filteredBooks.sort((a, b) => a.genre_name.localeCompare(b.genre_name));
            break;
        case 'year_desc':
            filteredBooks.sort((a, b) => b.year - a.year);
            break;
        case 'year_asc':
            filteredBooks.sort((a, b) => a.year - b.year);
            break;
        default:
            filteredBooks.sort((a, b) => a.title.localeCompare(b.title));
    }
}

// Применение фильтров
function applyFilters() {
    const yearFrom = elements.yearFromInput.value ? parseInt(elements.yearFromInput.value) : null;
    const yearTo = elements.yearToInput.value ? parseInt(elements.yearToInput.value) : null;
    
    currentFilters.yearFrom = yearFrom;
    currentFilters.yearTo = yearTo;
    
    filteredBooks = books.filter(book => {
        if (yearFrom && book.year < yearFrom) return false;
        if (yearTo && book.year > yearTo) return false;
        return true;
    });
    
    // Применяем текущий поиск
    const searchTerm = elements.searchInput.value.toLowerCase().trim();
    if (searchTerm) {
        filteredBooks = filteredBooks.filter(book => 
            book.title.toLowerCase().includes(searchTerm) ||
            (book.author_name && book.author_name.toLowerCase().includes(searchTerm))
        );
    }
    
    currentPage = 1;
    applySorting();
    renderBooks();
    updatePagination();
    updateStats();
}

// Сброс фильтров
function clearFilters() {
    elements.yearFromInput.value = '';
    elements.yearToInput.value = '';
    currentFilters.yearFrom = null;
    currentFilters.yearTo = null;
    
    filteredBooks = [...books];
    
    // Применяем текущий поиск
    const searchTerm = elements.searchInput.value.toLowerCase().trim();
    if (searchTerm) {
        filteredBooks = filteredBooks.filter(book => 
            book.title.toLowerCase().includes(searchTerm) ||
            (book.author_name && book.author_name.toLowerCase().includes(searchTerm))
        );
    }
    
    currentPage = 1;
    applySorting();
    renderBooks();
    updatePagination();
    updateStats();
}

// Пагинация: предыдущая страница
function goToPrevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderBooks();
        updatePagination();
        scrollToTop();
    }
}

// Пагинация: следующая страница
function goToNextPage() {
    const totalPages = Math.ceil(filteredBooks.length / booksPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderBooks();
        updatePagination();
        scrollToTop();
    }
}

// Обновление пагинации
function updatePagination() {
    const totalPages = Math.ceil(filteredBooks.length / booksPerPage);
    
    if (elements.pageInfo) {
        elements.pageInfo.textContent = `${currentPage} / ${totalPages || 1}`;
    }
    
    if (elements.prevPageBtn) {
        elements.prevPageBtn.disabled = currentPage === 1;
        elements.prevPageBtn.style.opacity = currentPage === 1 ? '0.5' : '1';
    }
    
    if (elements.nextPageBtn) {
        elements.nextPageBtn.disabled = currentPage === totalPages;
        elements.nextPageBtn.style.opacity = currentPage === totalPages ? '0.5' : '1';
    }
    
    if (elements.viewInfo) {
        const startIndex = (currentPage - 1) * booksPerPage;
        const endIndex = Math.min(startIndex + booksPerPage, filteredBooks.length);
        elements.viewInfo.textContent = `Показано ${startIndex + 1}-${endIndex} из ${filteredBooks.length}`;
    }
    
    if (elements.totalCount) {
        elements.totalCount.textContent = filteredBooks.length;
    }
}

// Обновление статистики
function updateStats() {
    if (!elements.statsEl) return;
    
    const user = window.authSystem ? window.authSystem.getUser() : null;
    
    // Базовая статистика
    let statsHtml = `
        <div style="margin-bottom: 10px;">
            <strong>📊 Статистика:</strong><br>
            <small>Всего книг: ${books.length}</small><br>
            <small>Найдено: ${filteredBooks.length}</small><br>
            <small>Жанров: ${new Set(books.map(b => b.genre_name)).size}</small><br>
            <small>Авторов: ${new Set(books.map(b => b.author_name)).size}</small>
        </div>
    `;
    
    // Информация о пользователе
    if (user) {
        statsHtml += `
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.1);">
                <strong>👤 Вы вошли как:</strong><br>
                <small>${user.name}</small><br>
                <small>${user.email}</small>
            </div>
            <div style="margin-top: 10px;">
                <button onclick="window.authSystem.logout()" class="btn ghost small">Выйти</button>
            </div>
        `;
    } else {
        statsHtml += `
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.1);">
                <strong>👥 Гость</strong><br>
                <small>Войдите для доступа ко всем функциям</small>
            </div>
            <div style="margin-top: 10px;">
                <button onclick="window.authSystem.login()" class="btn primary small">Войти</button>
                <button onclick="window.authSystem.register()" class="btn secondary ghost small">Регистрация</button>
            </div>
        `;
    }
    
    elements.statsEl.innerHTML = statsHtml;
}

// Отрисовка книг
function renderBooks() {
    if (!elements.bookGrid) return;
    
    elements.bookGrid.innerHTML = '';
    
    const startIndex = (currentPage - 1) * booksPerPage;
    const endIndex = Math.min(startIndex + booksPerPage, filteredBooks.length);
    const booksToShow = filteredBooks.slice(startIndex, endIndex);
    
    booksToShow.forEach((book, index) => {
        const bookEl = createBookElement(book);
        bookEl.style.animationDelay = `${index * 0.05}s`;
        elements.bookGrid.appendChild(bookEl);
    });
    
    // Если нет книг для отображения
    if (booksToShow.length === 0) {
        elements.bookGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted);">
                <div style="font-size: 48px; margin-bottom: 10px;">📚</div>
                <h3>Книги не найдены</h3>
                <p>Попробуйте изменить параметры поиска или фильтры</p>
            </div>
        `;
    }
}

// Создание элемента книги
function createBookElement(book) {
    const template = document.getElementById('bookCard');
    if (!template) {
        console.error('Шаблон bookCard не найден');
        return document.createElement('div');
    }
    
    const clone = template.content.cloneNode(true);
    const bookEl = clone.querySelector('.book');
    
    // Устанавливаем данные
    const cover = bookEl.querySelector('.cover');
    const title = bookEl.querySelector('.title');
    const author = bookEl.querySelector('.author');
    const description = bookEl.querySelector('.description');
    const year = bookEl.querySelector('.year');
    const genre = bookEl.querySelector('.genre');
    const badge = bookEl.querySelector('.badge');
    const commentsList = bookEl.querySelector('.comments-list');
    
    // Цвет обложки на основе названия
    const colors = ['#ffd9b3', '#ffb86b', '#ff9a3d', '#ff7b0f', '#e65c00'];
    const colorIndex = book.title.length % colors.length;
    cover.style.background = colors[colorIndex];
    cover.textContent = book.title.charAt(0).toUpperCase();
    
    title.textContent = book.title;
    author.textContent = `Автор: ${book.author_name}`;
    description.textContent = book.description || 'Описание отсутствует';
    year.textContent = book.year;
    genre.textContent = `Жанр: ${book.genre_name}`;
    
    // Бейдж с количеством комментариев
    const commentCount = book.comments ? book.comments.length : 0;
    badge.textContent = commentCount > 0 ? `💬 ${commentCount}` : '💬 0';
    
    // Показываем комментарии
    if (commentsList && book.comments) {
        book.comments.forEach(comment => {
            const commentEl = document.createElement('div');
            commentEl.className = 'comment';
            commentEl.textContent = comment.comment_text;
            commentsList.appendChild(commentEl);
        });
    }
    
    // Настройка обработчиков событий
    setupBookEvents(bookEl, book);
    
    return bookEl;
}

// Настройка обработчиков событий для книги
function setupBookEvents(bookEl, book) {
    // Раскрытие/сворачивание карточки
    bookEl.addEventListener('click', function(e) {
        // Не раскрываем, если клик был по интерактивным элементам
        if (e.target.closest('.read-toggle') || 
            e.target.closest('.comment-add') ||
            e.target.closest('.comment-input')) {
            return;
        }
        
        // Закрываем другие открытые карточки
        document.querySelectorAll('.book.expanded').forEach(otherBook => {
            if (otherBook !== bookEl) {
                otherBook.classList.remove('expanded');
            }
        });
        
        bookEl.classList.toggle('expanded');
    });
    
    // Кнопка "Читать/Прочитано"
    const readToggle = bookEl.querySelector('.read-toggle');
    if (readToggle) {
        if (window.authSystem && window.authSystem.isAuthenticated()) {
            readToggle.style.display = 'block';
            
            // Проверяем текущий статус
            checkReadStatus(book.id, readToggle);
            
            readToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                toggleReadStatus(book.id, this);
            });
        } else {
            readToggle.style.display = 'none';
        }
    }
    
    // Форма комментариев
    const commentForm = bookEl.querySelector('.comments-form');
    const commentInput = bookEl.querySelector('.comment-input');
    const commentAdd = bookEl.querySelector('.comment-add');
    
    if (commentForm && commentInput && commentAdd) {
        if (window.authSystem && window.authSystem.isAuthenticated()) {
            commentForm.style.display = 'flex';
            
            commentAdd.addEventListener('click', function(e) {
                e.stopPropagation();
                addComment(book.id, commentInput.value, bookEl);
            });
            
            commentInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.stopPropagation();
                    addComment(book.id, this.value, bookEl);
                }
            });
        } else {
            commentForm.style.display = 'none';
            commentInput.placeholder = 'Войдите, чтобы оставить комментарий';
        }
    }
}

// Проверка статуса "Прочитано"
async function checkReadStatus(bookId, button) {
    if (!window.authSystem || !window.authSystem.isAuthenticated()) return;
    
    try {
        const user = window.authSystem.getUser();
        const response = await fetch(`/shelf/user/${user.id}/book/${bookId}`);
        
        if (response.ok) {
            const shelfData = await response.json();
            if (shelfData.status_read) {
                button.classList.add('read');
                button.textContent = 'Прочитано';
            }
        }
    } catch (error) {
        console.error('Ошибка проверки статуса:', error);
    }
}

// Переключение статуса "Прочитано"
async function toggleReadStatus(bookId, button) {
    if (!window.authSystem || !window.authSystem.isAuthenticated()) {
        showNotification('Войдите, чтобы отмечать книги как прочитанные', 'warning');
        return;
    }
    
    try {
        const user = window.authSystem.getUser();
        
        // Проверяем, есть ли уже запись на полке
        const response = await fetch(`/shelf/user/${user.id}/book/${bookId}`);
        
        if (response.ok) {
            const existing = await response.json();
            // Обновляем статус
            const updateResponse = await fetch(`/shelf/${existing.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    status_read: !existing.status_read
                })
            });
            
            if (updateResponse.ok) {
                button.classList.toggle('read');
                button.textContent = button.classList.contains('read') ? 'Прочитано' : 'Читать';
                showNotification('Статус обновлен', 'success');
            }
        } else {
            // Создаем новую запись
            const shelfData = {
                book_id: bookId,
                user_id: user.id,
                status_read: true
            };
            
            const createResponse = await fetch('/shelf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(shelfData)
            });
            
            if (createResponse.ok) {
                button.classList.add('read');
                button.textContent = 'Прочитано';
                showNotification('Книга добавлена в прочитанные', 'success');
            }
        }
    } catch (error) {
        console.error('Ошибка при обновлении статуса:', error);
        showNotification('Ошибка при обновлении статуса', 'error');
    }
}

// Добавление комментария
async function addComment(bookId, text, bookEl) {
    if (!window.authSystem || !window.authSystem.isAuthenticated()) {
        showNotification('Войдите, чтобы оставлять комментарии', 'warning');
        return;
    }
    
    if (!text.trim()) {
        showNotification('Введите текст комментария', 'warning');
        return;
    }
    
    if (text.length > 200) {
        showNotification('Комментарий не должен превышать 200 символов', 'warning');
        return;
    }
    
    try {
        const user = window.authSystem.getUser();
        const commentData = {
            book_id: bookId,
            user_id: user.id,
            comment_text: text.trim()
        };
        
        const response = await fetch('/book-comments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(commentData)
        });
        
        if (response.ok) {
            const comment = await response.json();
            
            // Добавляем комментарий в UI
            const commentsList = bookEl.querySelector('.comments-list');
            if (commentsList) {
                const commentElement = document.createElement('div');
                commentElement.className = 'comment';
                commentElement.textContent = comment.comment_text;
                commentsList.appendChild(commentElement);
            }
            
            // Обновляем счетчик комментариев
            const badge = bookEl.querySelector('.badge');
            if (badge) {
                const currentCount = parseInt(badge.textContent.match(/\d+/)[0]) || 0;
                badge.textContent = `💬 ${currentCount + 1}`;
            }
            
            // Добавляем комментарий в локальные данные
            const book = books.find(b => b.id === bookId);
            if (book) {
                if (!book.comments) book.comments = [];
                book.comments.push(comment);
            }
            
            showNotification('Комментарий добавлен', 'success');
            
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Ошибка при добавлении комментария', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка соединения', 'error');
    }
}

// Добавление случайной книги
async function addRandomBook() {
    if (!window.authSystem || !window.authSystem.isAuthenticated()) {
        showNotification('Войдите, чтобы добавлять книги', 'warning');
        return;
    }
    
    try {
        // Получаем список авторов и жанров
        const [authorsResponse, genresResponse] = await Promise.all([
            fetch('/authors/?skip=0&limit=100'),
            fetch('/genres/?skip=0&limit=100')
        ]);
        
        const authors = authorsResponse.ok ? await authorsResponse.json() : [];
        const genres = genresResponse.ok ? await genresResponse.json() : [];
        
        if (authors.length === 0 || genres.length === 0) {
            showNotification('Нужно создать авторов и жанры перед добавлением книг', 'warning');
            return;
        }
        
        // Случайные данные
        const randomTitles = [
            "Тайна заброшенного замка",
            "Путешествие к центру Земли",
            "Звёздные войны: Новая надежда",
            "Мастер и Маргарита",
            "1984",
            "Преступление и наказание",
            "Война и мир",
            "Маленький принц",
            "Гарри Поттер и философский камень",
            "Властелин колец"
        ];
        
        const randomDescriptions = [
            "Захватывающая история о приключениях и открытиях.",
            "Роман, изменивший представление о литературе.",
            "Классика мировой литературы в новом прочтении.",
            "Фантастическое произведение о далёких мирах.",
            "Детективная история с неожиданной развязкой."
        ];
        
        const randomAuthor = authors[Math.floor(Math.random() * authors.length)];
        const randomGenre = genres[Math.floor(Math.random() * genres.length)];
        const randomTitle = randomTitles[Math.floor(Math.random() * randomTitles.length)];
        const randomDescription = randomDescriptions[Math.floor(Math.random() * randomDescriptions.length)];
        const randomYear = Math.floor(Math.random() * (2024 - 1900 + 1)) + 1900;
        
        const bookData = {
            title: randomTitle,
            description: randomDescription,
            author_id: randomAuthor.id,
            genre_id: randomGenre.id,
            year: randomYear
        };
        
        const response = await fetch('/books/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookData)
        });
        
        if (response.ok) {
            const newBook = await response.json();
            
            // Обогащаем данными
            newBook.author_name = randomAuthor.name;
            newBook.genre_name = randomGenre.name;
            newBook.comments = [];
            
            // Добавляем в локальные данные
            books.unshift(newBook);
            filteredBooks.unshift(newBook);
            
            // Обновляем UI
            renderBooks();
            updatePagination();
            updateStats();
            
            showNotification(`Книга "${newBook.title}" добавлена`, 'success');
            
        } else {
            const errorData = await response.json();
            showNotification(errorData.detail || 'Ошибка при добавлении книги', 'error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка соединения', 'error');
    }
}

// Обработка нажатий клавиш
function handleKeyDown(e) {
    switch(e.key) {
        case 'Escape':
            // Закрываем все раскрытые карточки
            document.querySelectorAll('.book.expanded').forEach(book => {
                book.classList.remove('expanded');
            });
            break;
            
        case 'ArrowLeft':
            if (e.altKey) goToPrevPage();
            break;
            
        case 'ArrowRight':
            if (e.altKey) goToNextPage();
            break;
    }
}

// Функция debounce для поиска
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Прокрутка к верху
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Тестовые данные для демонстрации
function getMockBooks() {
    return [
        {
            id: 1,
            title: "Мастер и Маргарита",
            description: "Роман Михаила Булгакова, работа над которым началась в конце 1920-х годов и продолжалась вплоть до смерти писателя.",
            author_id: 1,
            genre_id: 1,
            year: 1967,
            author_name: "Михаил Булгаков",
            genre_name: "Роман",
            comments: [
                { id: 1, comment_text: "Отличная книга!", user_id: 1 },
                { id: 2, comment_text: "Перечитываю каждый год", user_id: 2 }
            ]
        },
        {
            id: 2,
            title: "Преступление и наказание",
            description: "Социально-психологический и социально-философский роман Фёдора Михайловича Достоевского.",
            author_id: 2,
            genre_id: 1,
            year: 1866,
            author_name: "Фёдор Достоевский",
            genre_name: "Роман",
            comments: [
                { id: 3, comment_text: "Классика!", user_id: 1 }
            ]
        },
        {
            id: 3,
            title: "Война и мир",
            description: "Роман-эпопея Льва Николаевича Толстого, описывающий русское общество в эпоху войн против Наполеона.",
            author_id: 3,
            genre_id: 1,
            year: 1869,
            author_name: "Лев Толстой",
            genre_name: "Роман-эпопея",
            comments: []
        },
        {
            id: 4,
            title: "1984",
            description: "Роман-антиутопия Джорджа Оруэлла, изданный в 1949 году.",
            author_id: 4,
            genre_id: 2,
            year: 1949,
            author_name: "Джордж Оруэлл",
            genre_name: "Антиутопия",
            comments: [
                { id: 4, comment_text: "Актуально и сегодня", user_id: 3 }
            ]
        },
        {
            id: 5,
            title: "Маленький принц",
            description: "Аллегорическая повесть-сказка, наиболее известное произведение Антуана де Сент-Экзюпери.",
            author_id: 5,
            genre_id: 3,
            year: 1943,
            author_name: "Антуан де Сент-Экзюпери",
            genre_name: "Сказка",
            comments: []
        }
    ];
}

// Экспортируем функции для использования в консоли разработчика
window.app = {
    init,
    loadData,
    renderBooks,
    addRandomBook,
    getBooks: () => books,
    getFilteredBooks: () => filteredBooks,
    getCurrentUser: () => window.authSystem ? window.authSystem.getUser() : null
};

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', init);

// Для отладки
console.log('Приложение "Фолиант" загружено');