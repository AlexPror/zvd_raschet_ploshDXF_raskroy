// Preload script для безопасной связи между Electron и веб-контентом
// Этот файл выполняется в изолированном контексте перед загрузкой веб-страницы

const { contextBridge, ipcRenderer } = require('electron');

// Экспортируем безопасные API для использования в веб-контенте
contextBridge.exposeInMainWorld('electronAPI', {
  // Получить версию приложения
  getVersion: () => ipcRenderer.invoke('get-version'),
  
  // Проверить статус backend
  checkBackend: () => ipcRenderer.invoke('check-backend'),
  
  // Показать сообщение
  showMessage: (message) => ipcRenderer.invoke('show-message', message),
  
  // Слушать события от backend
  onBackendError: (callback) => {
    ipcRenderer.on('backend-error', (event, error) => callback(error));
  },
  
  // Удалить слушатель
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

