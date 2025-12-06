/* ...existing code... */
const PAGE_SIZE = 12;
let books = [];
let filtered = [];
let page = 1;
// auth + state
let currentUser = null;
const STORAGE_KEY = 'foliant_state_v1';

const qs = s => document.querySelector(s);
const qsa = s => Array.from(document.querySelectorAll(s));

function loadLocalState(){
  const raw = localStorage.getItem(STORAGE_KEY);
  if(!raw) return {users:[], sessions:{}, reads:{}, comments:{}};
  try{ return JSON.parse(raw); }catch(e){ return {users:[], sessions:{}, reads:{}, comments:{}}; }
}
function saveLocalState(state){ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }

const localState = loadLocalState();

const EMBEDDED_BOOKS = [
  {"id":1,"title":"Мудрость леса","author":"А. Петров","year":1998,"color":"#FFD9B3","genre":"Эссе","description":"Нежные размышления о природе и человеческой душе."},
  {"id":2,"title":"Тайна старого манускрипта","author":"И. Волков","year":2003,"color":"#FFECB8","genre":"Детектив","description":"Захватывающий детектив вокруг древнего текста и тайн библиотеки."},
  {"id":3,"title":"Путешествие в длину страниц","author":"С. Лебедев","year":2010,"color":"#FFE1C6","genre":"Приключения","description":"Приключенческий роман о странствиях по миру книг и памяти."},
  {"id":4,"title":"Книги и люди","author":"Н. Смирнова","year":1987,"color":"#FFD2A6","genre":"Эссе","description":"Эссе о роли литературы в жизни разных поколений."},
  {"id":5,"title":"Алхимия слов","author":"Д. Козлов","year":2015,"color":"#FFC79A","genre":"Фантастика","description":"Фантастическая история о силе языка и изменении реальности."},
  {"id":6,"title":"Читательский дневник","author":"О. Иванова","year":2001,"color":"#FFD9B3","genre":"Дневник","description":"Личные заметки одного преданного читателя."},
  {"id":7,"title":"Антология редких страниц","author":"Е. Морозов","year":1995,"color":"#FFE7C9","genre":"Антология","description":"Сборник редких и забытых текстов."},
  {"id":8,"title":"Мастерская редактуры","author":"Л. Крылов","year":2020,"color":"#FFDAB5","genre":"Руководство","description":"Практическое руководство по искусству редактирования текста."},
  {"id":9,"title":"Библиотечные заметки","author":"В. Никитин","year":1992,"color":"#FFE2CA","genre":"Заметки","description":"Короткие наблюдения из повседневной жизни библиотеки."},
  {"id":10,"title":"Сборник затей","author":"М. Громов","year":1980,"color":"#FFCFA8","genre":"Юмор","description":"Юмористические зарисовки и рассказы для настроения."},
  {"id":11,"title":"Тихие страницы","author":"А. Беляев","year":2008,"color":"#FFD9B3","genre":"Роман","description":"Тонкий роман о внутренних переживаниях и отношениях."},
  {"id":12,"title":"Перо и чернила","author":"И. Соколов","year":1999,"color":"#FFEFCF","genre":"Поэзия","description":"Сборник лирических стихотворений о мелочах жизни."},
  {"id":13,"title":"Хранители томов","author":"С. Миронов","year":2012,"color":"#FFD7A8","genre":"История","description":"Исторические очерки о людях, хранящих книги."},
  {"id":14,"title":"Записки библиотекаря","author":"Н. Рябова","year":1994,"color":"#FFDEA6","genre":"Дневник","description":"Личные заметки и случаи из работы библиотекаря."},
  {"id":15,"title":"Карта чтений","author":"Д. Орлов","year":1985,"color":"#FFD9B3","genre":"Путеводитель","description":"Путеводитель по важным книгам и чтению."},
  {"id":16,"title":"Листая вечность","author":"О. Филиппов","year":2006,"color":"#FFF0D9","genre":"Роман","description":"Роман о времени, памяти и книжных свидетельствах."},
  {"id":17,"title":"Портрет автора","author":"Е. Соловьёв","year":2018,"color":"#FFD2B3","genre":"Биография","description":"Биографический очерк о жизни и творчестве писателя."},
  {"id":18,"title":"Серые страницы","author":"Л. Павлова","year":1991,"color":"#FFE9D2","genre":"Драма","description":"Драматическая история о выборе и последствиях."},
  {"id":19,"title":"Каталог мыслей","author":"В. Романов","year":2000,"color":"#FFCFA8","genre":"Эссе","description":"Краткие философские заметки и размышления."},
  {"id":20,"title":"Страницы времени","author":"М. Васильев","year":1978,"color":"#FFD9B3","genre":"История","description":"Хроники и заметки о прошлом и его следах."},
  {"id":21,"title":"Сон о книге","author":"А. Ефремов","year":2011,"color":"#FFE1BE","genre":"Фантастика","description":"Мягкая фантастика о мечтах и книжных мирах."},
  {"id":22,"title":"Забытые тома","author":"И. Крылова","year":1996,"color":"#FFDAB5","genre":"Архив","description":"Исследование утраченных и забытых изданий."},
  {"id":23,"title":"Хроники читателя","author":"С. Зайцев","year":2004,"color":"#FFF2DF","genre":"Дневник","description":"Записи и мысли постоянного читателя."},
  {"id":24,"title":"Слово и сюжет","author":"Н. Белова","year":2017,"color":"#FFD7A8","genre":"Роман","description":"Современный роман о жизни через призму слова."},
  {"id":25,"title":"Нити книг","author":"Д. Мельников","year":1989,"color":"#FFE7C9","genre":"Антология","description":"Антология связных сюжетов и рассказов."},
  {"id":26,"title":"Книжный классификатор","author":"О. Литвин","year":1993,"color":"#FFD9B3","genre":"Справочник","description":"Полезный справочник по систематике книг."},
  {"id":27,"title":"Чтение в сумерках","author":"Е. Громова","year":2009,"color":"#FFECD0","genre":"Мистика","description":"Мистическая повесть о ночных открытиях и загадках."},
  {"id":28,"title":"Руководство по сохранению","author":"Л. Новик","year":2002,"color":"#FFCFA8","genre":"Руководство","description":"Практические советы по сохранению бумажных носителей."},
  {"id":29,"title":"Литературные маршруты","author":"В. Денисов","year":2013,"color":"#FFD9B3","genre":"Путеводитель","description":"Путеводитель по местам, связанным с литературой."},
  {"id":30,"title":"Сборник заметок","author":"М. Орехова","year":1997,"color":"#FFE2CA","genre":"Заметки","description":"Разнообразные заметки на литературные темы."},
  {"id":31,"title":"Письма из читальни","author":"А. Горбачёв","year":2005,"color":"#FFDAB5","genre":"Эссе","description":"Сборник писем и размышлений о чтении."},
  {"id":32,"title":"Архив воспоминаний","author":"И. Ковалёв","year":1983,"color":"#FFD9B3","genre":"Биография","description":"Воспоминания и документы из жизни автора."},
  {"id":33,"title":"Шелест страниц","author":"С. Логинов","year":2016,"color":"#FFF0D9","genre":"Поэзия","description":"Поэтические зарисовки о небольших радостях."},
  {"id":34,"title":"Вечная полка","author":"Н. Сергеева","year":1990,"color":"#FFE7C9","genre":"Антология","description":"Сборник вечных текстов для долгого чтения."},
  {"id":35,"title":"Листки истории","author":"Д. Чернов","year":1975,"color":"#FFC79A","genre":"История","description":"Исторические очерки и документы эпохи."},
  {"id":36,"title":"Голоса томов","author":"О. Рожков","year":2014,"color":"#FFD9B3","genre":"Эссе","description":"Эссе о значении книг и их голосах."},
  {"id":37,"title":"Привратник книг","author":"Е. Федорова","year":1988,"color":"#FFECD0","genre":"Фантастика","description":"Фантастическая повесть о хранителях знаний."},
  {"id":38,"title":"Схема хранения","author":"Л. Мартынов","year":2007,"color":"#FFD2A6","genre":"Справочник","description":"Методические рекомендации по организации хранения."},
  {"id":39,"title":"Мозаика сюжетов","author":"В. Шишков","year":1995,"color":"#FFD9B3","genre":"Роман","description":"Роман, составленный из переплетающихся историй."},
  {"id":40,"title":"Том за томом","author":"М. Киселёв","year":2019,"color":"#FFF6E6","genre":"Антология","description":"Современная антология небольших произведений."},
  {"id":41,"title":"Книжный порядок","author":"А. Титаренко","year":1984,"color":"#FFE7C9","genre":"Справочник","description":"Практическое руководство по систематизации коллекций."},
  {"id":42,"title":"Сборник фактов","author":"И. Лебедева","year":2003,"color":"#FFDAB5","genre":"Наука","description":"Набор фактов и наблюдений в популярном виде."},
  {"id":43,"title":"Палитра жанров","author":"С. Чернышёв","year":2010,"color":"#FFD9B3","genre":"Роман","description":"Роман, играющий с разнообразием литературных жанров."},
  {"id":44,"title":"Томик подборок","author":"Н. Алексеева","year":1992,"color":"#FFE2CA","genre":"Антология","description":"Подборка заметных и запоминающихся текстов."},
  {"id":45,"title":"Наследие страниц","author":"Д. Беляева","year":2001,"color":"#FFCFA8","genre":"Эссе","description":"Размышления о культурном наследии книг."},
  {"id":46,"title":"Фолиант: заметки","author":"О. Николаев","year":2021,"color":"#FFD9B3","genre":"Заметки","description":"Современные заметки и короткие зарисовки."},
  {"id":47,"title":"Маркер читателя","author":"Е. Макаров","year":1999,"color":"#FFF0D9","genre":"Руководство","description":"Практические советы для активных читателей."},
  {"id":48,"title":"Книжный обзор","author":"Л. Сидоров","year":1986,"color":"#FFD2B3","genre":"Обзор","description":"Обзоры и рецензии на интересные издания."},
  {"id":49,"title":"Секреты каталогизации","author":"В. Кузнецов","year":2000,"color":"#FFE9D2","genre":"Руководство","description":"Инструкция по тонкостям каталогизации библиотечных фондов."},
  {"id":50,"title":"Маленькая библиотека","author":"М. Полякова","year":1979,"color":"#FFD9B3","genre":"Детская","description":"Тёплые детские истории и сказки."},
  {"id":51,"title":"Страницы вдохновения","author":"А. Лазарев","year":2022,"color":"#FFF6E6","genre":"Поэзия","description":"Свежая поэзия для вдохновения и размышлений."},
  {"id":52,"title":"Путеводитель по томам","author":"И. Ромашова","year":1982,"color":"#FFDAB5","genre":"Путеводитель","description":"Краткий гид по коллекциям и классике литературы."}
];

async function loadBooks(){
  // use embedded data instead of fetching external JSON
  books = EMBEDDED_BOOKS.slice();
  filtered = books.slice();
  render();
}

function render(){
  const grid = qs('#bookGrid');
  grid.innerHTML = '';
  const start = (page-1)*PAGE_SIZE;
  const pageItems = filtered.slice(start, start+PAGE_SIZE);
  const tpl = qs('#bookCard');
  pageItems.forEach((b,i)=>{
    const node = tpl.content.cloneNode(true);
    const art = node.querySelector('.book');
    art.classList.add('animate');
    art.style.animationDelay = `${i * 45}ms`;
    const cover = node.querySelector('.cover');
    cover.style.background = b.color || '#FFD9B3';
    cover.textContent = b.title.split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase();
    node.querySelector('.title').textContent = b.title;
    node.querySelector('.author').textContent = b.author;
    const descEl = node.querySelector('.description');
    if(descEl) descEl.textContent = b.description ? b.description : (b.genre ? `${b.genre} · Краткое описание отсутствует.` : 'Краткое описание отсутствует.');
    node.querySelector('.year').textContent = b.year;
    const gEl = node.querySelector('.genre');
    if(gEl) gEl.textContent = b.genre ? `Жанр: ${b.genre}` : '';
    const badge = node.querySelector('.badge');
    if(badge) badge.textContent = b.genre || '';
    // read status per user — use the read control located inside comments-form (if present)
    const readBtn = node.querySelector('.comments-form .read-toggle');
    if(readBtn){
      const reads = localState.reads || {};
      const userReads = currentUser ? (reads[currentUser]||{}) : {};
      if(userReads[b.id]) { readBtn.classList.add('read'); readBtn.textContent = 'Прочитано'; }
      else { readBtn.classList.remove('read'); readBtn.textContent = 'Читать'; }
      readBtn.addEventListener('click', (e)=>{ e.stopPropagation(); toggleRead(b.id, readBtn); });
    }
    // comments
    const commentsList = node.querySelector('.comments-list');
    const commentsForm = node.querySelector('.comments-form');
    const commentInput = node.querySelector('.comment-input');
    const addBtn = node.querySelector('.comment-add');
    const bookComments = (localState.comments && localState.comments[b.id]) ? localState.comments[b.id] : [];
    commentsList.innerHTML = '';
    bookComments.forEach(c=>{
      const el = document.createElement('div');
      el.className = 'comment';
      el.textContent = `${c.user}: ${c.text}`;
      commentsList.appendChild(el);
    });
    addBtn.addEventListener('click', ()=> {
      if(!currentUser){ alert('Пожалуйста, войдите чтобы оставить комментарий.'); return; }
      const t = commentInput.value.trim(); if(!t) return;
      const arr = localState.comments[b.id] = localState.comments[b.id] || [];
      arr.push({user: currentUser, text: t, ts: Date.now()});
      saveLocalState(localState);
      // append new comment in-place to avoid re-render (which collapses cards)
      const el = document.createElement('div');
      el.className = 'comment';
      el.textContent = `${currentUser}: ${t}`;
      commentsList.appendChild(el);
      commentInput.value = '';
      // ensure the card is expanded so user sees the new comment
      art.classList.add('expanded');
    });
    // open focused panel on click / key (shows centered panel with dim backdrop)
    const openPanel = () => showCardPanel(b, art);
    art.addEventListener('click', openPanel);
    art.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPanel(); } });
    grid.appendChild(node);
  });

  qs('#totalCount').textContent = books.length;
  qs('#viewInfo').textContent = `Показано ${pageItems.length} из ${filtered.length}`;
  qs('#pageInfo').textContent = `${page} / ${Math.max(1,Math.ceil(filtered.length/PAGE_SIZE))}`;
  qs('#stats').textContent = `Всего записей: ${books.length}. Фильтровано: ${filtered.length}.`;
  updateAuthUI();
}

/* create backdrop container (once) */
function ensureBackdrop(){
  let bd = document.querySelector('.backdrop');
  if(bd) return bd;
  bd = document.createElement('div');
  bd.className = 'backdrop';
  bd.setAttribute('aria-hidden','true');
  document.body.appendChild(bd);
  return bd;
}

function showCardPanel(book, sourceArt){
  const bd = ensureBackdrop();
  bd.innerHTML = '';
  bd.setAttribute('aria-hidden','false');
  bd.classList.add('show');
  // build panel content (reuse structure similar to card)
  const panel = document.createElement('div');
  panel.className = 'card-panel';
  panel.setAttribute('role','dialog');
  panel.setAttribute('aria-label', `Карточка: ${book.title}`);

  const closeBtn = document.createElement('button');
  closeBtn.className = 'panel-close';
  closeBtn.innerHTML = '&times;';
  closeBtn.addEventListener('click', hideCardPanel);
  panel.appendChild(closeBtn);

  const header = document.createElement('div');
  header.style.display = 'flex';
  header.style.alignItems = 'flex-start';
  header.style.gap = '12px';

  const cover = document.createElement('div');
  cover.className = 'cover';
  cover.style.background = book.color || '#FFD9B3';
  cover.style.flex = '0 0 auto';
  cover.textContent = book.title.split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase();
  header.appendChild(cover);

  const meta = document.createElement('div');
  meta.className = 'meta';
  const t = document.createElement('h3'); t.textContent = book.title;
  const a = document.createElement('div'); a.textContent = book.author;
  const d = document.createElement('div'); d.className = 'panel-description'; d.textContent = book.description || 'Описание не добавлено.';
  const y = document.createElement('div'); y.textContent = `Год: ${book.year}`;
  const g = document.createElement('div'); g.textContent = `Жанр: ${book.genre || '—'}`;
  meta.appendChild(t); meta.appendChild(a); meta.appendChild(d); meta.appendChild(y); meta.appendChild(g);
  header.appendChild(meta);
  panel.appendChild(header);

  // comments section inside panel
  const commWrap = document.createElement('div');
  commWrap.style.marginTop = '12px';
  const cl = document.createElement('div'); cl.className = 'comments-list';
  const bookComments = (localState.comments && localState.comments[book.id]) ? localState.comments[book.id] : [];
  bookComments.forEach(c=>{
    const el = document.createElement('div');
    el.className = 'comment';
    el.textContent = `${c.user}: ${c.text}`;
    cl.appendChild(el);
  });
  commWrap.appendChild(cl);
  const cf = document.createElement('div'); cf.className = 'comments-form';
  const ci = document.createElement('input'); ci.className = 'comment-input'; ci.placeholder = 'Оставить комментарий…';
  const ca = document.createElement('button'); ca.className = 'comment-add'; ca.textContent = 'Отправить';
  cf.appendChild(ci); cf.appendChild(ca);
  commWrap.appendChild(cf);
  panel.appendChild(commWrap);

  // read toggle (panel)
  const panelRead = document.createElement('button');
  panelRead.className = 'read-toggle panel-read';
  const reads = localState.reads || {};
  const userReads = currentUser ? (reads[currentUser]||{}) : {};
  if(userReads[book.id]) { panelRead.classList.add('read'); panelRead.textContent = 'Прочитано'; } else { panelRead.textContent = 'Читать'; }
  panelRead.addEventListener('click', (e)=>{
    e.stopPropagation();
    toggleRead(book.id, panelRead);
    // sync button label
    if(panelRead.classList.contains('read')) panelRead.textContent = 'Прочитано'; else panelRead.textContent = 'Читать';
  });
  // append the read button after the comments area so it sits lower in the panel
  panel.appendChild(panelRead);

  // wire comment add in panel
  ca.addEventListener('click', ()=>{
    if(!currentUser){ alert('Пожалуйста, войдите чтобы оставить комментарий.'); return; }
    const t = ci.value.trim(); if(!t) return;
    const arr = localState.comments[book.id] = localState.comments[book.id] || [];
    arr.push({user: currentUser, text: t, ts: Date.now()});
    saveLocalState(localState);
    const el = document.createElement('div'); el.className = 'comment'; el.textContent = `${currentUser}: ${t}`;
    cl.appendChild(el);
    ci.value = '';
  });

  bd.appendChild(panel);

  // clicking backdrop (outside panel) closes
  bd.addEventListener('click', onBackdropClick);
  // key handling (Esc)
  window.addEventListener('keydown', onEscClose);

  // focus management
  panel.tabIndex = -1; panel.focus();

  function onBackdropClick(e){
    if(e.target === bd) hideCardPanel();
  }
  function onEscClose(e){
    if(e.key === 'Escape') hideCardPanel();
  }
  // store references for removal
  bd._cleanup = ()=>{ bd.removeEventListener('click', onBackdropClick); window.removeEventListener('keydown', onEscClose); };
}

function hideCardPanel(){
  const bd = document.querySelector('.backdrop');
  if(!bd) return;
  bd._cleanup && bd._cleanup();
  bd.classList.remove('show');
  bd.setAttribute('aria-hidden','true');
  bd.innerHTML = '';
}

/* new auth helpers */
function updateAuthUI(){
  const logged = !!currentUser;
  qs('#btnLogin').style.display = logged ? 'none' : '';
  qs('#btnRegister').style.display = logged ? 'none' : '';
  const ub = qs('#userBadge');
  if(logged){ ub.style.display = ''; qs('#userName').textContent = currentUser; } else { ub.style.display = 'none'; }
}

function toggleRead(bookId, btn){
  if(!currentUser){ alert('Войдите чтобы отмечать прочитанное.'); return; }
  localState.reads = localState.reads || {};
  localState.reads[currentUser] = localState.reads[currentUser] || {};
  const cur = !!localState.reads[currentUser][bookId];
  if(cur) delete localState.reads[currentUser][bookId]; else localState.reads[currentUser][bookId] = true;
  saveLocalState(localState);
  if(!cur){ btn.classList.add('read'); btn.textContent = 'Прочитано'; } else { btn.classList.remove('read'); btn.textContent = 'Читать'; }
}

function applySearchSortFilters(){
  const q = qs('#search').value.trim().toLowerCase();
  const sort = qs('#sort').value;
  const yFrom = parseInt(qs('#yearFrom').value) || -Infinity;
  const yTo = parseInt(qs('#yearTo').value) || Infinity;

  filtered = books.filter(b=>{
    const matches = (b.title + ' ' + b.author + ' ' + (b.genre||'')).toLowerCase().includes(q);
    const inYear = b.year >= yFrom && b.year <= yTo;
    return matches && inYear;
  });

  if(sort === 'title') filtered.sort((a,b)=>a.title.localeCompare(b.title));
  if(sort === 'author') filtered.sort((a,b)=>a.author.localeCompare(b.author));
  if(sort === 'genre') filtered.sort((a,b)=>{
    const A = (a.genre||'').toLowerCase();
    const B = (b.genre||'').toLowerCase();
    return A.localeCompare(B) || a.title.localeCompare(b.title);
  });
  if(sort === 'year_desc') filtered.sort((a,b)=>b.year - a.year);
  if(sort === 'year_asc') filtered.sort((a,b)=>a.year - b.year);

  page = 1;
  render();
}

function wire(){
  qs('#search').addEventListener('input', debounce(()=>applySearchSortFilters(), 200));
  qs('#sort').addEventListener('change', applySearchSortFilters);
  qs('#applyFilters').addEventListener('click', applySearchSortFilters);
  qs('#clearFilters').addEventListener('click', ()=>{
    qs('#yearFrom').value = ''; qs('#yearTo').value = ''; qs('#search').value = '';
    applySearchSortFilters();
  });
  qs('#prevPage').addEventListener('click', ()=>{
    if(page>1){page--; render();}
  });
  qs('#nextPage').addEventListener('click', ()=>{
    const max = Math.max(1,Math.ceil(filtered.length/PAGE_SIZE));
    if(page<max){page++; render();}
  });
  qs('#addRandom').addEventListener('click', ()=>{
    const id = books.length ? Math.max(...books.map(b=>b.id))+1 : 1;
    const genres = ['Роман','Эссе','Поэзия','Детектив','Приключения','Руководство','История','Наука','Фантастика','Дневник','Антология','Юмор','Мистика','Путеводитель','Обзор','Детская','Справочник','Заметки','Биография','Драма'];
    const sample = {id, title:`Новая книга ${id}`, author:`Автор ${id}`, year:2000 + (id%23), color: '#FFECB8', genre: genres[id % genres.length]};
    books.unshift(sample);
    applySearchSortFilters();
  });

  // auth wiring
  qs('#btnLogin').addEventListener('click', ()=>openAuthModal('login'));
  qs('#btnRegister').addEventListener('click', ()=>openAuthModal('register'));
  qs('#authCancel').addEventListener('click', ()=>closeAuthModal());
  // close icon inside modal
  const modalClose = qs('#authClose');
  if(modalClose) modalClose.addEventListener('click', ()=>closeAuthModal());
  qs('#authSubmit').addEventListener('click', ()=>handleAuthSubmit());
  qs('#btnLogout').addEventListener('click', ()=>{
    currentUser = null; updateAuthUI(); render();
  });
}

/* auth modal functions */
function openAuthModal(mode='login'){
  qs('#authModal').setAttribute('aria-hidden','false');
  qs('#modalTitle').textContent = mode==='login' ? 'Вход' : 'Регистрация';
  qs('#authSubmit').textContent = mode==='login' ? 'Войти' : 'Зарегистрироваться';
  qs('#authModal').dataset.mode = mode;
  qs('#authMsg').textContent = '';
  qs('#authLogin').value = ''; qs('#authPass').value = '';
}
function closeAuthModal(){ qs('#authModal').setAttribute('aria-hidden','true'); }

function handleAuthSubmit(){
  const mode = qs('#authModal').dataset.mode || 'login';
  const login = qs('#authLogin').value.trim();
  const pass = qs('#authPass').value;
  if(!login || !pass){ qs('#authMsg').textContent = 'Введите логин и пароль'; return; }
  localState.users = localState.users || [];
  const existing = localState.users.find(u=>u.login===login);
  if(mode==='register'){
    if(existing){ qs('#authMsg').textContent = 'Пользователь уже существует'; return; }
    localState.users.push({login, pass});
    saveLocalState(localState);
    currentUser = login;
    closeAuthModal();
    updateAuthUI();
    render();
    return;
  } else {
    if(!existing || existing.pass !== pass){ qs('#authMsg').textContent = 'Неверные данные'; return; }
    currentUser = login;
    closeAuthModal();
    updateAuthUI();
    render();
  }
}

function debounce(fn, wait=150){
  let t;
  return (...a)=>{ clearTimeout(t); t = setTimeout(()=>fn(...a), wait); };
}

window.addEventListener('load', async ()=>{
  await loadBooks();
  wire();
  // set footer year
  const y = new Date().getFullYear();
  const el = document.getElementById('year');
  if(el) el.textContent = y;
});