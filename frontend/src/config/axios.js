import axios from 'axios'

// Определяем базовый URL для API
// В Electron нужно использовать localhost:5000
// В браузере (dev mode) используем относительные пути (прокси Vite)
const getBaseURL = () => {
  // Проверяем, запущено ли в Electron
  // Electron добавляет различные признаки в window
  if (typeof window === 'undefined') {
    return ''
  }
  
  // Проверяем протокол - в Electron обычно file://
  const isFileProtocol = window.location && window.location.protocol === 'file:'
  
  // Проверяем другие признаки Electron
  const hasElectronProcess = window.process && window.process.type === 'renderer'
  const hasElectronUserAgent = navigator && navigator.userAgent && navigator.userAgent.includes('Electron')
  const hasRequire = window.require && typeof window.require === 'function'
  const hasElectronAPI = window.electron
  
  const isElectron = isFileProtocol || hasElectronProcess || hasElectronUserAgent || hasRequire || hasElectronAPI
  
  if (isElectron) {
    // В Electron используем localhost:5000
    const baseURL = 'http://localhost:5000'
    console.log('🔌 Electron detected, using', baseURL, 'for API')
    console.log('  Protocol:', window.location?.protocol)
    console.log('  UserAgent:', navigator?.userAgent?.substring(0, 50))
    console.log('  Process type:', window.process?.type)
    return baseURL
  }
  
  // В браузере (dev mode) используем относительные пути
  // Vite proxy будет перенаправлять на localhost:5000
  console.log('🌐 Browser mode, using relative paths (Vite proxy)')
  return ''
}

// Создаем экземпляр axios с правильным baseURL
const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 120000, // 2 минуты для больших файлов
  headers: {
    'Content-Type': 'application/json'
  }
})

// Переопределяем baseURL динамически при каждом запросе (на случай, если определение не сработало)
apiClient.interceptors.request.use(
  (config) => {
    // Если baseURL пустой, но мы в Electron, устанавливаем его
    if (!config.baseURL && typeof window !== 'undefined' && window.location?.protocol === 'file:') {
      config.baseURL = 'http://localhost:5000'
      console.log('🔧 Fixed baseURL to http://localhost:5000 (detected file:// protocol)')
    }
    return config
  }
)

// Добавляем interceptor для логирования (опционально)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.baseURL || ''}${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('❌ API Response Error:', error)
    if (error.code === 'ERR_NETWORK' || error.message.includes('ERR_FILE_NOT_FOUND')) {
      console.error('⚠️ Backend не доступен. Убедитесь, что Flask сервер запущен на порту 5000')
    }
    return Promise.reject(error)
  }
)

export default apiClient

