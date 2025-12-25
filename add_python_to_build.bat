@echo off
REM Скрипт для добавления Python в портативную версию

echo ========================================
echo Добавление Python в портативную версию
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Проверка Python...
if not exist "build\python\python.exe" (
    echo Python не найден в build\python\
    echo.
    echo Устанавливаю Python...
    cd build
    call install_python.bat
    cd ..
    if errorlevel 1 (
        echo ОШИБКА: Не удалось установить Python
        echo.
        echo ВАЖНО: Python должен быть установлен в build\python\
        echo Запустите: build\install_python.bat
        pause
        exit /b 1
    )
) else (
    echo ✓ Python найден в build\python\
)

echo.
echo [2/3] Проверка зависимостей Python...
cd build\python
python.exe -c "import flask" 2>nul
if errorlevel 1 (
    echo Зависимости не установлены. Устанавливаю...
    python.exe -m pip install -r ..\..\backend\requirements.txt
    if errorlevel 1 (
        echo ОШИБКА: Не удалось установить зависимости
        pause
        exit /b 1
    )
) else (
    echo ✓ Зависимости установлены
)
cd ..\..

echo.
echo [3/3] Пересборка Electron с Python...
cd frontend
call npm run build
if errorlevel 1 (
    echo ОШИБКА: Не удалось собрать frontend
    pause
    exit /b 1
)

REM Копируем electron если нужно
if not exist "electron" (
    xcopy /E /I /Y ..\electron electron
)

REM Собираем портативную версию
set WIN_CSC_LINK=
set CSC_IDENTITY_AUTO_DISCOVERY=false
set CSC_LINK=
set CSC_KEY_PASSWORD=

call npx electron-builder --win --config.win.target=dir --config.win.sign=null 2>&1 | findstr /V /C:"symbolic link" /C:"darwin" /C:"libcrypto" /C:"libssl" /C:"winCodeSign" /C:"code signing"

cd ..

echo.
if exist "frontend\dist-electron\win-unpacked\resources\python\python.exe" (
    echo ========================================
    echo ✓ Python включен в портативную версию!
    echo ========================================
    echo.
    echo Проверка:
    echo   frontend\dist-electron\win-unpacked\resources\python\python.exe
    echo.
) else (
    echo ⚠ Python не найден в собранной версии
    echo Проверьте конфигурацию в frontend\package.json
    echo.
)

pause

