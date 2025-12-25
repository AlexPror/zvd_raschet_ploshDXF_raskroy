@echo off
REM Скрипт для сборки готового пакета для бухгалтерии

echo ========================================
echo Сборка пакета ZVD Nesting Calculator
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Проверка Python...
if not exist "build\python\python.exe" (
    echo Python не найден. Устанавливаю...
    cd build
    call install_python.bat
    cd ..
    if errorlevel 1 (
        echo ОШИБКА: Не удалось установить Python
        pause
        exit /b 1
    )
) else (
    echo Python найден ✓
)

echo.
echo [2/4] Сборка frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ОШИБКА: Не удалось собрать frontend
    pause
    exit /b 1
)
cd ..

echo.
echo [3/4] Сборка Electron приложения...
cd frontend
call npm run electron:build:win
if errorlevel 1 (
    echo ОШИБКА: Не удалось собрать Electron приложение
    pause
    exit /b 1
)
cd ..

echo.
echo [4/4] Подготовка пакета для передачи...
if exist "frontend\dist-electron\ZVD Nesting Calculator Setup *.exe" (
    echo.
    echo ========================================
    echo ✓ СБОРКА ЗАВЕРШЕНА УСПЕШНО!
    echo ========================================
    echo.
    echo Установщик находится в:
    echo frontend\dist-electron\
    echo.
    echo Файл для передачи в бухгалтерию:
    dir /b "frontend\dist-electron\ZVD Nesting Calculator Setup *.exe"
    echo.
    echo Инструкция для бухгалтерии находится в:
    echo INSTRUCTIONS_FOR_USERS.md
    echo.
) else (
    echo ПРЕДУПРЕЖДЕНИЕ: Установщик не найден
    echo Проверьте папку frontend\dist-electron\
)

pause

