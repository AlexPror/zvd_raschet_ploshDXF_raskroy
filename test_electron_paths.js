// Временный скрипт для проверки путей в Electron
const { app } = require('electron');
const path = require('path');
const fs = require('fs');

app.whenReady().then(() => {
  console.log('App path:', app.getAppPath());
  console.log('Resources path:', process.resourcesPath);
  console.log('__dirname:', __dirname);
  
  const possiblePaths = [
    path.join(app.getAppPath(), 'dist', 'index.html'),
    path.join(process.resourcesPath, 'app.asar', 'dist', 'index.html'),
    path.join(process.resourcesPath, 'app', 'dist', 'index.html'),
    path.join(__dirname, '..', 'dist', 'index.html'),
    path.join(__dirname, '..', 'frontend', 'dist', 'index.html')
  ];
  
  console.log('\nChecking paths:');
  possiblePaths.forEach(p => {
    const exists = fs.existsSync(p);
    console.log(`${exists ? '✓' : '✗'} ${p}`);
  });
  
  app.quit();
});

