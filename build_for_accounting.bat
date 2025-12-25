@echo off
REM Скрипт для сборки пакета для бухгалтерии

echo ========================================
echo Сборка ZVD Nesting Calculator
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Сборка frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ОШИБКА: Не удалось собрать frontend
    pause
    exit /b 1
)
cd ..

echo.
echo [2/3] Копирование electron в frontend...
if not exist "frontend\electron" (
    xcopy /E /I /Y electron frontend\electron
)

echo.
echo [3/3] Сборка Electron приложения...
cd frontend
set CSC_IDENTITY_AUTO_DISCOVERY=false
call npx electron-builder --win --config.win.sign=null
if errorlevel 1 (
    echo ОШИБКА: Не удалось собрать Electron приложение
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo ✓ СБОРКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Установщик находится в:
echo frontend\dist-electron\
echo.
echo Файл для передачи в бухгалтерию:
dir /b "frontend\dist-electron\ZVD Nesting Calculator Setup *.exe"
echo.
echo Инструкция для бухгалтерии: INSTALLATION_GUIDE.md
echo.

pause

