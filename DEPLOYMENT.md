# 🚀 Инструкция по развертыванию

## Варианты развертывания приложения

### 1. Локальный запуск (Разработка)

См. раздел "Установка и запуск" в README.md

---

### 2. Docker (Рекомендуется для продакшена)

#### Создание Dockerfile для Backend

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

#### Создание Dockerfile для Frontend

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend/uploads:/app/uploads
    environment:
      - FLASK_ENV=production

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

#### Запуск

```bash
docker-compose up -d
```

---

### 3. Heroku

#### Подготовка

1. Создайте `Procfile` в корне проекта:
```
web: cd backend && python app.py
```

2. Создайте `runtime.txt`:
```
python-3.11.0
```

3. Установите Heroku CLI и войдите:
```bash
heroku login
heroku create your-app-name
```

4. Деплой:
```bash
git push heroku main
```

---

### 4. Railway

1. Подключите GitHub репозиторий
2. Railway автоматически определит Python проект
3. Укажите команду запуска: `cd backend && python app.py`
4. Добавьте переменные окружения при необходимости

---

### 5. Render

1. Создайте новый Web Service
2. Подключите GitHub репозиторий
3. Настройки:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && python app.py`
4. Деплой автоматический при push

---

### 6. Создание EXE файла (Windows)

#### Вариант A: PyInstaller (только Backend)

```bash
pip install pyinstaller

cd backend
pyinstaller --onefile --name "ZVD_Backend" --add-data "uploads;uploads" app.py
```

#### Вариант B: Electron (Полное приложение)

1. Установите Electron:
```bash
npm install -g electron electron-builder
```

2. Создайте `electron/main.js`:
```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let backendProcess;
let mainWindow;

function startBackend() {
  const backendPath = path.join(__dirname, '../backend/app.py');
  backendProcess = spawn('python', [backendPath]);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false
    }
  });
  
  mainWindow.loadURL('http://localhost:5173');
}

app.whenReady().then(() => {
  startBackend();
  setTimeout(createWindow, 2000);
});

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill();
  app.quit();
});
```

3. Обновите `package.json`:
```json
{
  "main": "electron/main.js",
  "scripts": {
    "electron": "electron .",
    "build:electron": "electron-builder"
  }
}
```

4. Сборка:
```bash
npm run build:electron
```

---

### 7. GitHub Actions (CI/CD)

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
```

---

## Рекомендации

### Для разработки:
- Локальный запуск (самый простой)

### Для продакшена:
- **Docker** - если есть свой сервер
- **Railway/Render** - если нужен быстрый деплой без настройки
- **Heroku** - если нужна стабильность и поддержка

### Для распространения:
- **EXE через Electron** - для Windows пользователей
- **Docker образ** - для серверов
- **Установочный пакет** - через Inno Setup или NSIS

---

## Переменные окружения

Создайте `.env` файл для продакшена:

```env
FLASK_ENV=production
FLASK_DEBUG=False
MAX_CONTENT_LENGTH=52428800  # 50 MB
UPLOAD_FOLDER=uploads
```

