# Добавление логотипа проекта

## Описание

Логотип проекта "Фолиант" успешно добавлен в сайт. Он отображается в верхней части страницы рядом с названием сайта.

## Изменения в коде

### 1. HTML (app/templates/index.html)
- Добавлена новая секция `brand-container` в хедер
- Добавлен тег `<img>` для логотипа с путём `/app/static/images/logo.png`
- Логотип расположен слева от названия "Фолиант"

```html
<div class="brand-container">
    <img src="/app/static/images/logo.png" alt="Логотип Фолиант" class="brand-logo" />
    <h1 class="brand">Фолиант</h1>
</div>
```

### 2. CSS (app/static/css/style.css)
- Добавлены стили для `.brand-container` (flexbox layout)
- Добавлены стили для `.brand-logo` (размер, скругление углов, анимация)
- Анимация: логотип появляется при загрузке страницы (эффект скольжения и масштабирования)

```css
.brand-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: 12px;
}

.brand-logo {
  width: 40px;
  height: 40px;
  display: block;
  border-radius: 8px;
  object-fit: contain;
  object-position: center;
  animation: logoSlideIn 0.5s cubic-bezier(0.2, 0.9, 0.2, 1);
}
```

### 3. Структура папок
```
app/
  static/
    images/
      logo.png  ← Разместите логотип здесь
    css/
    js/
  templates/
    index.html  ← Обновлен
```

## Как загрузить логотип

### Вариант 1: Через веб-интерфейс GitHub
1. Откройте репозиторий на GitHub: https://github.com/Dan4i4ek31/Final_Project_2.0
2. Перейдите в папку `app/static/images/`
3. Нажмите "Add file" → "Upload files"
4. Выберите файл логотипа (поддерживаются: PNG, JPG, SVG)
5. Назовите файл `logo.png`
6. Нажмите "Commit changes"

### Вариант 2: Через командную строку (локально)
```bash
# 1. Клонируйте репозиторий (если ещё не клонировали)
git clone https://github.com/Dan4i4ek31/Final_Project_2.0.git
cd Final_Project_2.0

# 2. Убедитесь, что папка существует
mkdir -p app/static/images

# 3. Скопируйте логотип в папку
cp /path/to/your/logo.png app/static/images/logo.png

# 4. Добавьте файл в git
git add app/static/images/logo.png

# 5. Сделайте коммит
git commit -m "Add project logo"

# 6. Отправьте изменения
git push origin master
```

### Вариант 3: Конвертирование JPG → PNG

Если у вас есть JPG версия логотипа:

#### Linux/Mac (с использованием ImageMagick):
```bash
convert input.jpg output.png
```

#### Онлайн конвертер:
1. Откройте https://convertio.co/ru/jpg-png/ или аналогичный сервис
2. Загрузите JPG файл
3. Скачайте PNG версию
4. Сохраните как `logo.png`

#### Python:
```python
from PIL import Image
img = Image.open('logo.jpg')
img.save('logo.png')
```

## Рекомендации

- **Формат**: PNG или SVG (прозрачный фон)
- **Размер**: 40×40 пикселей или больше (CSS масштабирует до 40px)
- **Фон**: Прозрачный или белый для лучшей интеграции
- **Качество**: Высокое разрешение для резких краёв на экранах Retina

## Тестирование

1. Убедитесь, что логотип загружен: `app/static/images/logo.png`
2. Запустите приложение
3. Откройте главную страницу
4. Проверьте, что логотип отображается рядом с названием "Фолиант"
5. При загрузке логотип должен плавно появиться (анимация)

## Структура HTML

```html
<header class="topbar">
  <div class="container">
    <!-- Логотип и название -->
    <div class="brand-container">
      <img src="/app/static/images/logo.png" alt="Логотип Фолиант" class="brand-logo" />
      <h1 class="brand">Фолиант</h1>
    </div>
    
    <!-- Остальные элементы хедера -->
    <div class="controls">...</div>
  </div>
</header>
```

## Чек-лист

- [x] HTML обновлён с изображением логотипа
- [x] CSS стили добавлены (layout + анимация)
- [x] Папка `app/static/images/` создана
- [ ] Логотип загружен как `logo.png`
- [ ] Тестирование на локальной машине
- [ ] Коммит с логотипом отправлен на GitHub

---

**Статус**: Готово к использованию. Ожидание загрузки файла логотипа.
