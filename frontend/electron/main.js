const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let backendProcess;
let mainWindow;
let isQuitting = false;

// Функция для запуска backend сервера
function startBackend() {
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  
  // Определяем путь к Python
  let pythonPath;
  
  // Используем системный Python (пользователь должен установить его)
  if (process.platform === 'win32') {
    pythonPath = 'py';  // Windows Python Launcher
  } else if (process.platform === 'darwin' || process.platform === 'linux') {
    pythonPath = 'python3';
  } else {
    pythonPath = 'python';
  }
  
  // В production можно попробовать встроенный Python (если есть)
  if (!isDev) {
    let embeddedPythonPath;
    if (process.platform === 'win32') {
      embeddedPythonPath = path.join(process.resourcesPath, 'python', 'python.exe');
    } else {
      embeddedPythonPath = path.join(process.resourcesPath, 'python', 'bin', 'python3');
    }
    
    if (fs.existsSync(embeddedPythonPath)) {
      pythonPath = embeddedPythonPath;
      console.log('Using embedded Python');
    } else {
      console.log('Using system Python (user must install Python 3.8+)');
    }
  }
  
  // Путь к app.py
  const backendPath = isDev 
    ? path.join(__dirname, '..', 'backend', 'app.py')
    : path.join(process.resourcesPath, 'backend', 'app.py');
  
  // Проверяем существование файла
  if (!fs.existsSync(backendPath)) {
    console.error(`Backend file not found: ${backendPath}`);
    console.error(`isDev: ${isDev}, isPackaged: ${app.isPackaged}`);
    if (!isDev) {
      console.error(`resourcesPath: ${process.resourcesPath}`);
    }
    console.error(`__dirname: ${__dirname}`);
    return;
  }
  
  console.log(`Starting backend: ${pythonPath} ${backendPath}`);
  console.log(`Working directory: ${isDev ? path.join(__dirname, '..') : process.resourcesPath}`);
  
  // Настраиваем переменные окружения для встроенного Python
  const env = { ...process.env };
  if (!isDev) {
    const pythonDir = path.join(process.resourcesPath, 'python');
    if (process.platform === 'win32') {
      // Windows: добавляем путь к Python в PATH
      env.PATH = `${pythonDir};${env.PATH}`;
      env.PYTHONPATH = path.join(pythonDir, 'lib', 'site-packages');
    } else {
      // macOS/Linux: добавляем bin в PATH
      env.PATH = `${path.join(pythonDir, 'bin')}:${env.PATH}`;
      env.PYTHONPATH = path.join(pythonDir, 'lib', 'site-packages');
    }
  }
  
  // Запускаем backend процесс
  backendProcess = spawn(pythonPath, [backendPath], {
    cwd: isDev ? path.join(__dirname, '..') : process.resourcesPath,
    stdio: 'inherit',
    shell: process.platform === 'win32',
    env: env
  });
  
  backendProcess.on('error', (err) => {
    console.error('Failed to start backend:', err);
    // Показываем ошибку пользователю
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-error', err.message);
    }
  });
  
  backendProcess.on('exit', (code) => {
    if (code !== 0 && !isQuitting) {
      console.error(`Backend process exited with code ${code}`);
    }
  });
  
  // Логируем вывод backend
  if (backendProcess.stdout) {
    backendProcess.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });
  }
  
  if (backendProcess.stderr) {
    backendProcess.stderr.on('data', (data) => {
      console.error(`Backend error: ${data}`);
    });
  }
}

// Функция для создания окна приложения
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    },
    icon: path.join(__dirname, 'icon.png'), // Опционально, если есть иконка
    show: false // Не показываем окно до полной загрузки
  });
  
  // Показываем окно когда готово
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Фокус на окне
    if (process.platform === 'darwin') {
      app.dock.show();
    }
  });
  
  // Загружаем frontend
  const isDev = process.env.NODE_ENV === 'development';
  
  if (isDev) {
    // В режиме разработки используем Vite dev server
    mainWindow.loadURL('http://localhost:5173');
    
    // Открываем DevTools в режиме разработки
    mainWindow.webContents.openDevTools();
  } else {
    // В production загружаем собранный frontend
    // В Electron приложении файлы находятся в app.asar
    const appPath = app.getAppPath();
    console.log(`App path: ${appPath}`);
    console.log(`Resources path: ${process.resourcesPath}`);
    
    // Путь к index.html в app.asar
    const indexPath = path.join(appPath, 'dist', 'index.html');
    console.log(`Trying to load: ${indexPath}`);
    console.log(`File exists: ${fs.existsSync(indexPath)}`);
    
    if (fs.existsSync(indexPath)) {
      // Используем loadFile для загрузки HTML файла
      mainWindow.loadFile(indexPath).catch(err => {
        console.error('Error loading file:', err);
        // Пробуем альтернативный способ - через file:// протокол
        const fileUrl = `file://${indexPath.replace(/\\/g, '/')}`;
        console.log(`Trying file:// URL: ${fileUrl}`);
        mainWindow.loadURL(fileUrl);
      });
    } else {
      // Пробуем альтернативные пути
      const alternativePaths = [
        path.join(process.resourcesPath, 'app.asar', 'dist', 'index.html'),
        path.join(process.resourcesPath, 'app', 'dist', 'index.html'),
        path.join(__dirname, '..', 'dist', 'index.html')
      ];
      
      const foundPath = alternativePaths.find(p => {
        const exists = fs.existsSync(p);
        if (exists) console.log(`Found at: ${p}`);
        return exists;
      });
      
      if (foundPath) {
        console.log(`Loading from: ${foundPath}`);
        mainWindow.loadFile(foundPath);
      } else {
        console.error('Frontend not found! Checked paths:');
        console.error(`  - ${indexPath}`);
        alternativePaths.forEach(p => console.error(`  - ${p}`));
        
        // Показываем ошибку пользователю
        mainWindow.loadURL(`data:text/html,<html><body style="font-family: Arial; padding: 20px; text-align: center;"><h1>Ошибка загрузки приложения</h1><p>Не удалось найти файлы frontend.</p><p>Проверьте консоль для подробностей.</p><p style="color: #666; font-size: 12px;">App path: ${appPath}</p></body></html>`);
      }
    }
  }
  
  // Обработка ошибок загрузки
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load:', errorCode, errorDescription);
    
    // Если backend еще не запустился, ждем и перезагружаем
    if (errorCode === -106) {
      setTimeout(() => {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.reload();
        }
      }, 2000);
    }
  });
  
  // Обработка закрытия окна
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Когда приложение готово
app.whenReady().then(() => {
  console.log('Electron app ready');
  
  // Запускаем backend
  startBackend();
  
  // Ждем немного перед созданием окна (чтобы backend успел запуститься)
  setTimeout(() => {
    createWindow();
  }, 2000);
  
  // Для macOS: когда все окна закрыты, но приложение все еще работает
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Закрытие всех окон (кроме macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    isQuitting = true;
    if (backendProcess) {
      backendProcess.kill();
    }
    app.quit();
  }
});

// Перед выходом из приложения
app.on('before-quit', (event) => {
  isQuitting = true;
  if (backendProcess) {
    console.log('Stopping backend process...');
    backendProcess.kill();
    // Даем время на корректное завершение
    setTimeout(() => {
      if (backendProcess && !backendProcess.killed) {
        backendProcess.kill('SIGKILL');
      }
    }, 2000);
  }
});

// Обработка необработанных исключений
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

