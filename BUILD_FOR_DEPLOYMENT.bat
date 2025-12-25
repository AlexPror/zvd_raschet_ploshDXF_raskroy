@echo off
REM Скрипт для сборки готового установщика для передачи в бухгалтерию

echo ========================================
echo Сборка ZVD Nesting Calculator
echo ========================================
echo.

cd /d "%~dp0"

REM Шаг 1: Проверка Python
echo [1/4] Проверка Python...
if not exist "build\python\python.exe" (
    echo Python не найден в build\python\
    echo.
    echo Устанавливаю Python...
    cd build
    call install_python.bat
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ОШИБКА: Не удалось установить Python
        echo Пожалуйста, установите Python вручную:
        echo 1. Скачайте: https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip
        echo 2. Распакуйте в: build\python\
        echo 3. Запустите этот скрипт снова
        pause
        exit /b 1
    )
    cd ..
) else (
    echo Python найден!
)

echo.
echo [2/4] Сборка frontend...
cd frontend
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ОШИБКА: Не удалось собрать frontend
    pause
    exit /b 1
)
echo Frontend собран успешно!

echo.
echo [3/4] Сборка Electron приложения...
call npm run electron:build:win
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ОШИБКА: Не удалось собрать Electron приложение
    pause
    exit /b 1
)
echo Electron приложение собрано успешно!

echo.
echo [4/4] Поиск установщика...
cd ..
if exist "frontend\dist-electron\ZVD Nesting Calculator Setup*.exe" (
    echo.
    echo ========================================
    echo УСПЕШНО! Установщик готов!
    echo ========================================
    echo.
    echo Установщик находится в:
    for %%f in ("frontend\dist-electron\ZVD Nesting Calculator Setup*.exe") do (
        echo   %%f
        echo.
        echo Размер: 
        for %%s in ("%%f") do echo   %%~zs байт (%%~zs / 1048576 MB)
    )
    echo.
    echo Этот файл можно передать в бухгалтерию.
    echo Они смогут установить программу двойным кликом.
    echo.
    echo Нажмите любую клавишу для открытия папки с установщиком...
    pause >nul
    explorer "frontend\dist-electron"
) else (
    echo.
    echo ОШИБКА: Установщик не найден
    echo Проверьте папку: frontend\dist-electron\
    pause
    exit /b 1
)

