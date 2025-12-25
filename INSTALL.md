# 📦 Варианты установки и распространения

## 1. Локальная установка (для разработки)

См. [QUICKSTART.md](QUICKSTART.md)

---

## 2. Создание EXE файла (Windows)

### Вариант A: PyInstaller (Backend + Frontend bundle)

**Требования:**
- Python 3.8+
- Node.js 16+
- PyInstaller

**Шаги:**

1. **Соберите frontend:**
```bash
cd frontend
npm run build
```

2. **Установите PyInstaller:**
```bash
pip install pyinstaller
```

3. **Создайте spec файл для PyInstaller:**

Создайте `build_exe.spec`:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['backend/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),
        ('backend/uploads', 'backend/uploads'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ZVD_Nesting_Calculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

4. **Соберите EXE:**
```bash
pyinstaller build_exe.spec
```

5. **Результат:** `dist/ZVD_Nesting_Calculator.exe`

**Недостатки:**
- Большой размер файла (100+ MB)
- Медленный запуск
- Нужно включать все зависимости

---

### Вариант B: Electron (Рекомендуется)

**Преимущества:**
- Кроссплатформенность (Windows, Mac, Linux)
- Меньший размер
- Лучшая производительность

**Шаги:**

1. **Установите Electron:**
```bash
npm install -g electron electron-builder
```

2. **Создайте структуру:**

Создайте `electron/main.js`:
```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let backendProcess;
let mainWindow;

function startBackend() {
  const backendPath = path.join(__dirname, '../backend/app.py');
  const pythonPath = 'python'; // или полный путь к python.exe
  
  backendProcess = spawn(pythonPath, [backendPath], {
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit'
  });
  
  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    icon: path.join(__dirname, 'icon.png') // опционально
  });
  
  // Ждем запуска backend
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:5173');
  }, 3000);
  
  // Для разработки можно использовать:
  // mainWindow.loadURL('http://localhost:5173');
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
```

3. **Обновите `package.json`:**
```json
{
  "main": "electron/main.js",
  "scripts": {
    "electron": "electron .",
    "build:win": "electron-builder --win",
    "build:all": "electron-builder --win --mac --linux"
  },
  "build": {
    "appId": "com.zvd.nesting",
    "productName": "ZVD Nesting Calculator",
    "directories": {
      "output": "dist-electron"
    },
    "win": {
      "target": "nsis",
      "icon": "electron/icon.ico"
    }
  }
}
```

4. **Соберите приложение:**
```bash
npm run build:win
```

**Результат:** Установочный файл в `dist-electron/`

---

## 3. Docker контейнер

См. [DEPLOYMENT.md](DEPLOYMENT.md) раздел "Docker"

---

## 4. Онлайн деплой

### Heroku (Простой вариант)

1. Установите Heroku CLI
2. Войдите: `heroku login`
3. Создайте приложение: `heroku create zvd-nesting-calc`
4. Деплой: `git push heroku main`

### Railway (Рекомендуется)

1. Зайдите на [railway.app](https://railway.app)
2. Подключите GitHub репозиторий
3. Railway автоматически определит проект
4. Настройте команду запуска: `cd backend && python app.py`

### Render

1. Создайте новый Web Service
2. Подключите GitHub
3. Настройки:
   - Build: `cd backend && pip install -r requirements.txt`
   - Start: `cd backend && python app.py`

---

## 5. Рекомендации

### Для разработки:
✅ Локальный запуск

### Для распространения Windows пользователям:
✅ Electron приложение (лучший UX)
✅ Или PyInstaller EXE (проще, но больше размер)

### Для онлайн доступа:
✅ Railway или Render (проще всего)
✅ Heroku (стабильно, но платно)
✅ VPS + Docker (полный контроль)

### Для корпоративного использования:
✅ Docker контейнер
✅ VPS с автоматическим деплоем

---

## Сравнение вариантов

| Вариант | Сложность | Размер | Производительность | Кроссплатформенность |
|---------|-----------|--------|-------------------|---------------------|
| Локальный запуск | ⭐ | - | ⭐⭐⭐⭐⭐ | ✅ |
| PyInstaller EXE | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ (только Windows) |
| Electron | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ✅ |
| Docker | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ✅ |
| Heroku/Railway | ⭐ | - | ⭐⭐⭐ | ✅ |

---

## Следующие шаги

1. Выберите подходящий вариант
2. Следуйте инструкциям в соответствующих разделах
3. Протестируйте на целевой платформе
4. Создайте релиз на GitHub

