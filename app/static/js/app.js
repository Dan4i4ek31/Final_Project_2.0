// Замените ВСЕ содержимое app.js на этот код:

// Основной файл приложения "Фолиант"
console.log('Загружен app.js');

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
const elements = {};

// Инициализация приложения
async function init() {
    console.log('Инициализация приложения "Фолиант"...');
    
    try {
        // Получаем все DOM элементы
        cacheElements();
        
        // Проверяем наличие элементов
        if (!elements.bookGrid) {
            console.error('Основной элемент bookGrid не найден');
            return;
        }
        
        // Настройка обработчиков событий
        setupEventListeners();
        
        // Загружаем данные
        await loadData();
        
        // Первоначальная отрисовка
        renderBooks();
        updatePagination();
        updateStats();
        
        console.log('Приложение инициализировано успешно');
    } catch (error) {
        console.error('Ошибка инициализации:', error);
        showError('Ошибка загрузки приложения');
    }
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
    
    // Проверяем, что все элементы найдены
    console.log('Найденные элементы:', elements);
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

// Показать ошибку
function showError(message) {
    if (elements.bookGrid) {
        elements.bookGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #dc3545;">
                <div style="font-size: 48px; margin-bottom: 10px;">❌</div>
                <h3>${message}</h3>
                <p>Пожалуйста, проверьте консоль для деталей</p>
            </div>
        `;
    }
}

// Загрузка данных
async function loadData() {
    console.log('Начинаем загрузку данных...');
    
    try {
        // Показываем сообщение о загрузке
        showLoadingMessage();
        
        // Загружаем книги
        console.log('Загружаем книги с API...');
        const booksResponse = await fetch('/books/');
        
        console.log('Ответ от /books/:', {
            status: booksResponse.status,
            statusText: booksResponse.statusText,
            ok: booksResponse.ok
        });
        
        if (!booksResponse.ok) {
            throw new Error(`Ошибка загрузки книг: ${booksResponse.status} ${booksResponse.statusText}`);
        }
        
        books = await booksResponse.json();
        console.log(`Загружено ${books.length} книг:`, books);
        
        // Загружаем авторов
        console.log('Загружаем авторов...');
        let authors = [];
        try {
            const authorsResponse = await fetch('/authors/');
            if (authorsResponse.ok) {
                authors = await authorsResponse.json();
                console.log(`Загружено ${authors.length} авторов`);
            } else {
                console.warn('Не удалось загрузить авторов');
            }
        } catch (error) {
            console.warn('Ошибка загрузки авторов:', error);
        }
        
        // Загружаем жанры
        console.log('Загружаем жанры...');
        let genres = [];
        try {
            const genresResponse = await fetch('/genres/');
            if (genresResponse.ok) {
                genres = await genresResponse.json();
                console.log(`Загружено ${genres.length} жанров`);
            } else {
                console.warn('Не удалось загрузить жанры');
            }
        } catch (error) {
            console.warn('Ошибка загрузки жанров:', error);
        }
        
        // Обогащаем книги данными авторов и жанров
        books.forEach(book => {
            // Находим автора
            let authorName = 'Неизвестный автор';
            if (authors.length > 0) {
                const author = authors.find(a => a.id === book.author_id);
                if (author) {
                    authorName = author.name;
                }
            } else if (book.author) {
                // Если автор приходит с книгой (relationship)
                authorName = book.author.name;
            }
            
            // Находим жанр
            let genreName = 'Неизвестный жанр';
            if (genres.length > 0) {
                const genre = genres.find(g => g.id === book.genre_id);
                if (genre) {
                    genreName = genre.name;
                }
            } else if (book.genre) {
                // Если жанр приходит с книгой (relationship)
                genreName = book.genre.name;
            }
            
            // Сохраняем данные
            book.author_name = authorName;
            book.genre_name = genreName;
            book.comments = book.book_comments || [];
            
            // Проверяем наличие необходимых полей
            if (!book.title) book.title = 'Без названия';
            if (!book.year) book.year = 'Не указан';
            if (!book.description) book.description = 'Описание отсутствует';
        });
        
        filteredBooks = [...books];
        
        // Применяем сортировку по умолчанию
        applySorting();
        
        // Показываем уведомление об успехе
        if (window.showNotification && books.length > 0) {
            window.showNotification(`Загружено ${books.length} книг`, 'success');
        } else if (window.showNotification) {
            window.showNotification('Книги не найдены. Добавьте книги в базу данных.', 'info');
        }
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        
        // Используем тестовые данные
        console.log('Используем тестовые данные...');
        books = getMockBooks();
        filteredBooks = [...books];
        
        if (window.showNotification) {
            window.showNotification('Используются тестовые данные', 'warning');
        }
    }
}

// Показать сообщение о загрузке
function showLoadingMessage() {
    if (elements.bookGrid) {
        elements.bookGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted);">
                <div style="font-size: 48px; margin-bottom: 10px; animation: spin 2s linear infinite;">📚</div>
                <h3>Загрузка книг...</h3>
                <p>Пожалуйста, подождите</p>
            </div>
        `;
    }
}

// Обработка поиска
function handleSearch() {
    if (!elements.searchInput) return;
    
    const searchTerm = elements.searchInput.value.toLowerCase().trim();
    
    if (!searchTerm) {
        filteredBooks = [...books];
    } else {
        filteredBooks = books.filter(book => {
            const titleMatch = book.title && book.title.toLowerCase().includes(searchTerm);
            const authorMatch = book.author_name && book.author_name.toLowerCase().includes(searchTerm);
            const descMatch = book.description && book.description.toLowerCase().includes(searchTerm);
            return titleMatch || authorMatch || descMatch;
        });
    }
    
    currentPage = 1;
    applySorting();
    renderBooks();
    updatePagination();
    updateStats();
}

// Обработка изменения сортировки
function handleSortChange() {
    if (!elements.sortSelect) return;
    
    currentSort = elements.sortSelect.value;
    applySorting();
    renderBooks();
}

// Применение сортировки
function applySorting() {
    switch(currentSort) {
        case 'title':
            filteredBooks.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
            break;
        case 'author':
            filteredBooks.sort((a, b) => (a.author_name || '').localeCompare(b.author_name || ''));
            break;
        case 'genre':
            filteredBooks.sort((a, b) => (a.genre_name || '').localeCompare(b.genre_name || ''));
            break;
        case 'year_desc':
            filteredBooks.sort((a, b) => (b.year || 0) - (a.year || 0));
            break;
        case 'year_asc':
            filteredBooks.sort((a, b) => (a.year || 0) - (b.year || 0));
            break;
        default:
            filteredBooks.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    }
}

// Применение фильтров
function applyFilters() {
    const yearFrom = elements.yearFromInput?.value ? parseInt(elements.yearFromInput.value) : null;
    const yearTo = elements.yearToInput?.value ? parseInt(elements.yearToInput.value) : null;
    
    currentFilters.yearFrom = yearFrom;
    currentFilters.yearTo = yearTo;
    
    filteredBooks = books.filter(book => {
        if (yearFrom && book.year < yearFrom) return false;
        if (yearTo && book.year > yearTo) return false;
        return true;
    });
    
    // Применяем текущий поиск
    const searchTerm = elements.searchInput?.value.toLowerCase().trim() || '';
    if (searchTerm) {
        filteredBooks = filteredBooks.filter(book => {
            const titleMatch = book.title && book.title.toLowerCase().includes(searchTerm);
            const authorMatch = book.author_name && book.author_name.toLowerCase().includes(searchTerm);
            return titleMatch || authorMatch;
        });
    }
    
    currentPage = 1;
    applySorting();
    renderBooks();
    updatePagination();
    updateStats();
}

// Сброс фильтров
function clearFilters() {
    if (elements.yearFromInput) elements.yearFromInput.value = '';
    if (elements.yearToInput) elements.yearToInput.value = '';
    
    currentFilters.yearFrom = null;
    currentFilters.yearTo = null;
    
    filteredBooks = [...books];
    
    // Применяем текущий поиск
    const searchTerm = elements.searchInput?.value.toLowerCase().trim() || '';
    if (searchTerm) {
        filteredBooks = filteredBooks.filter(book => {
            const titleMatch = book.title && book.title.toLowerCase().includes(searchTerm);
            const authorMatch = book.author_name && book.author_name.toLowerCase().includes(searchTerm);
            return titleMatch || authorMatch;
        });
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
    const totalPages = Math.ceil(filteredBooks.length / booksPerPage) || 1;
    
    if (elements.pageInfo) {
        elements.pageInfo.textContent = `${currentPage} / ${totalPages}`;
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
                <button onclick="logoutUser()" class="btn ghost small">Выйти</button>
            </div>
        `;
    } else {
        statsHtml += `
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.1);">
                <strong>👥 Гость</strong><br>
                <small>Войдите для доступа ко всем функциям</small>
            </div>
            <div style="margin-top: 10px;">
                <button onclick="showLogin()" class="btn primary small">Войти</button>
                <button onclick="showRegister()" class="btn secondary ghost small">Регистрация</button>
            </div>
        `;
    }
    
    elements.statsEl.innerHTML = statsHtml;
}

// Функции для кнопок в статистике
function logoutUser() {
    if (window.authSystem && window.authSystem.logout) {
        window.authSystem.logout();
    }
}

function showLogin() {
    if (window.authSystem && window.authSystem.login) {
        window.authSystem.login();
    }
}

function showRegister() {
    if (window.authSystem && window.authSystem.register) {
        window.authSystem.register();
    }
}

// Отрисовка книг
function renderBooks() {
    if (!elements.bookGrid) return;
    
    elements.bookGrid.innerHTML = '';
    
    const startIndex = (currentPage - 1) * booksPerPage;
    const endIndex = Math.min(startIndex + booksPerPage, filteredBooks.length);
    const booksToShow = filteredBooks.slice(startIndex, endIndex);
    
    if (booksToShow.length === 0) {
        elements.bookGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted);">
                <div style="font-size: 48px; margin-bottom: 10px;">📚</div>
                <h3>Книги не найдены</h3>
                <p>Попробуйте изменить параметры поиска или фильтры</p>
            </div>
        `;
        return;
    }
    
    booksToShow.forEach((book, index) => {
        const bookEl = createBookElement(book);
        bookEl.style.animationDelay = `${index * 0.05}s`;
        elements.bookGrid.appendChild(bookEl);
    });
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
    
    // Устанавливаем ID книги
    bookEl.dataset.bookId = book.id;
    
    // Устанавливаем данные
    const cover = bookEl.querySelector('.cover');
    const title = bookEl.querySelector('.title');
    const author = bookEl.querySelector('.author');
    const description = bookEl.querySelector('.description');
    const year = bookEl.querySelector('.year');
    const genre = bookEl.querySelector('.genre');
    const badge = bookEl.querySelector('.badge');
    const commentsList = bookEl.querySelector('.comments-list');
    const commentForm = bookEl.querySelector('.comments-form');
    const commentInput = bookEl.querySelector('.comment-input');
    const commentAdd = bookEl.querySelector('.comment-add');
    const readToggle = bookEl.querySelector('.read-toggle');
    
    // Цвет обложки на основе названия
    const colors = ['#ffd9b3', '#ffb86b', '#ff9a3d', '#ff7b0f', '#e65c00'];
    const colorIndex = book.title.length % colors.length;
    cover.style.background = colors[colorIndex];
    cover.textContent = book.title.charAt(0).toUpperCase();
    
    title.textContent = book.title;
    author.textContent = `Автор: ${book.author_name || 'Неизвестен'}`;
    description.textContent = book.description || 'Описание отсутствует';
    year.textContent = book.year || 'Не указан';
    genre.textContent = `Жанр: ${book.genre_name || 'Неизвестен'}`;
    
    // Бейдж с количеством комментариев
    const commentCount = book.comments ? book.comments.length : 0;
    badge.textContent = commentCount > 0 ? `💬 ${commentCount}` : '💬 0';
    
    // Показываем комментарии
    if (commentsList && book.comments && book.comments.length > 0) {
        commentsList.innerHTML = '';
        book.comments.forEach(comment => {
            const commentEl = document.createElement('div');
            commentEl.className = 'comment';
            commentEl.textContent = comment.comment_text || comment.text || 'Комментарий';
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
            readToggle.style.display = 'inline-block';
            
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
        if (window.showNotification) {
            window.showNotification('Войдите, чтобы отмечать книги как прочитанные', 'warning');
        }
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
                if (window.showNotification) {
                    window.showNotification('Статус обновлен', 'success');
                }
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
                if (window.showNotification) {
                    window.showNotification('Книга добавлена в прочитанные', 'success');
                }
            }
        }
    } catch (error) {
        console.error('Ошибка при обновлении статуса:', error);
        if (window.showNotification) {
            window.showNotification('Ошибка при обновлении статуса', 'error');
        }
    }
}

// Добавление комментария
async function addComment(bookId, text, bookEl) {
    if (!window.authSystem || !window.authSystem.isAuthenticated()) {
        if (window.showNotification) {
            window.showNotification('Войдите, чтобы оставлять комментарии', 'warning');
        }
        return;
    }
    
    if (!text.trim()) {
        if (window.showNotification) {
            window.showNotification('Введите текст комментария', 'warning');
        }
        return;
    }
    
    if (text.length > 200) {
        if (window.showNotification) {
            window.showNotification('Комментарий не должен превышать 200 символов', 'warning');
        }
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
                const currentCount = parseInt(badge.textContent.match(/\d+/)?.[0]) || 0;
                badge.textContent = `💬 ${currentCount + 1}`;
            }
            
            // Добавляем комментарий в локальные данные
            const book = books.find(b => b.id === bookId);
            if (book) {
                if (!book.comments) book.comments = [];
                book.comments.push(comment);
            }
            
            // Очищаем поле ввода
            const commentInput = bookEl.querySelector('.comment-input');
            if (commentInput) {
                commentInput.value = '';
            }
            
            if (window.showNotification) {
                window.showNotification('Комментарий добавлен', 'success');
            }
            
        } else {
            const errorData = await response.json();
            if (window.showNotification) {
                window.showNotification(errorData.detail || 'Ошибка при добавлении комментария', 'error');
            }
        }
    } catch (error) {
        console.error('Ошибка:', error);
        if (window.showNotification) {
            window.showNotification('Ошибка соединения', 'error');
        }
    }
}

// Добавление случайной книги
async function addRandomBook() {
    if (!window.authSystem || !window.authSystem.isAuthenticated()) {
        if (window.showNotification) {
            window.showNotification('Войдите, чтобы добавлять книги', 'warning');
        }
        return;
    }
    
    try {
        // Получаем список авторов и жанров
        console.log('Загружаем авторов и жанры для добавления книги...');
        const [authorsResponse, genresResponse] = await Promise.all([
            fetch('/authors/?skip=0&limit=100'),
            fetch('/genres/?skip=0&limit=100')
        ]);
        
        const authors = authorsResponse.ok ? await authorsResponse.json() : [];
        const genres = genresResponse.ok ? await genresResponse.json() : [];
        
        console.log(`Найдено авторов: ${authors.length}, жанров: ${genres.length}`);
        
        if (authors.length === 0 || genres.length === 0) {
            if (window.showNotification) {
                window.showNotification('Нужно создать авторов и жанры перед добавлением книг', 'warning');
            }
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
        
        console.log('Отправляем данные книги:', bookData);
        
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
            currentPage = 1;
            renderBooks();
            updatePagination();
            updateStats();
            
            if (window.showNotification) {
                window.showNotification(`Книга "${newBook.title}" добавлена`, 'success');
            }
            
        } else {
            const errorData = await response.json();
            console.error('Ошибка добавления книги:', errorData);
            
            let errorMessage = 'Ошибка при добавлении книги';
            if (errorData.detail) {
                if (typeof errorData.detail === 'string') {
                    errorMessage = errorData.detail;
                } else if (Array.isArray(errorData.detail)) {
                    errorMessage = errorData.detail.map(err => err.msg || err).join(', ');
                }
            }
            
            if (window.showNotification) {
                window.showNotification(errorMessage, 'error');
            }
        }
    } catch (error) {
        console.error('Ошибка:', error);
        if (window.showNotification) {
            window.showNotification('Ошибка соединения', 'error');
        }
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
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM загружен, запускаем приложение...');
    
    // Даем время на загрузку всех скриптов
    setTimeout(() => {
        if (window.app && window.app.init) {
            window.app.init();
        } else {
            console.error('Модуль app не загружен');
            showError('Ошибка загрузки приложения');
        }
    }, 100);
});

// Добавляем анимацию спиннера в CSS
if (!document.querySelector('style#spin-animation')) {
    const style = document.createElement('style');
    style.id = 'spin-animation';
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

console.log('Приложение "Фолиант" загружено и готово к работе');