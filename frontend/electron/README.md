# Electron приложение

Эта папка содержит файлы для Electron приложения.

## Структура

- `main.js` - главный процесс Electron
- `preload.js` - preload скрипт для безопасной связи с веб-контентом
- `README.md` - этот файл

## Как это работает

1. **main.js** запускает backend сервер (Python Flask)
2. Затем создает окно браузера
3. Загружает frontend (Vite dev server в разработке, или собранный dist в production)
4. Frontend подключается к backend через API

## Требования

- Python должен быть установлен на системе пользователя
- Все зависимости backend должны быть установлены

## Режим разработки

```bash
# Терминал 1: Backend
cd backend
python app.py

# Терминал 2: Frontend
cd frontend
npm run dev

# Терминал 3: Electron
cd frontend
npm run electron:dev
```

## Production сборка

```bash
cd frontend
npm run build          # Собрать frontend
npm run electron:build  # Собрать Electron приложение
```

