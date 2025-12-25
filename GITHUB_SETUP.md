# 📤 Инструкция по загрузке на GitHub

## Шаг 1: Подготовка репозитория

Репозиторий уже инициализирован. Теперь нужно:

1. **Добавить все файлы:**
```bash
git add .
```

2. **Создать первый коммит:**
```bash
git commit -m "Initial commit: ZVD Nesting Calculator v1.0.0"
```

## Шаг 2: Подключение к GitHub

1. **Добавить remote репозиторий:**
```bash
git remote add origin https://github.com/AlexPror/zvd_raschet_ploshDXF_raskroy.git
```

2. **Проверить remote:**
```bash
git remote -v
```

## Шаг 3: Загрузка на GitHub

```bash
# Переименовать ветку в main (если нужно)
git branch -M main

# Загрузить код
git push -u origin main
```

Если возникнет ошибка аутентификации, используйте Personal Access Token:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Создайте новый token с правами `repo`
3. Используйте токен вместо пароля при push

## Шаг 4: Создание релиза

После загрузки кода:

1. Перейдите на GitHub в репозиторий
2. Нажмите "Releases" → "Create a new release"
3. Укажите:
   - Tag: `v1.0.0`
   - Title: `Release v1.0.0`
   - Описание: см. CHANGELOG.md
4. Нажмите "Publish release"

## Шаг 5: Настройка GitHub Pages (опционально)

GitHub Pages поддерживает только статические сайты. Для этого приложения:

### Вариант A: Только документация
- Используйте GitHub Pages для README и документации
- Backend нужно деплоить отдельно (Heroku, Railway, etc.)

### Вариант B: Frontend на Pages + Backend отдельно
1. Соберите frontend: `cd frontend && npm run build`
2. Настройте GitHub Pages на папку `frontend/dist`
3. Backend деплойте на отдельный сервис

## Шаг 6: GitHub Actions (CI/CD)

Создайте `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Check version
      run: |
        python -c "import sys; sys.path.insert(0, 'backend'); from app import VERSION; print(f'Version: {VERSION}')"
```

## Полезные команды

```bash
# Проверить статус
git status

# Посмотреть изменения
git diff

# Добавить изменения
git add .

# Создать коммит
git commit -m "Описание изменений"

# Загрузить на GitHub
git push origin main

# Создать тег версии
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Структура для GitHub

Рекомендуемая структура файлов в репозитории:

```
zvd_raschet_ploshDXF_raskroy/
├── README.md          # Главная документация
├── QUICKSTART.md      # Быстрый старт
├── DEPLOYMENT.md      # Инструкции по деплою
├── CHANGELOG.md       # История изменений
├── VERSION            # Текущая версия
├── .gitignore         # Игнорируемые файлы
├── .gitattributes     # Настройки git
├── backend/           # Backend код
├── frontend/          # Frontend код
└── .github/           # GitHub Actions, Issues templates
    └── workflows/
        └── ci.yml
```

