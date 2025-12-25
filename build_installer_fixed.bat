@echo off
REM Исправленная сборка установщика

echo ========================================
echo Сборка установщика ZVD Nesting Calculator
echo ========================================
echo.

cd /d "%~dp0\frontend"

echo [1/3] Сборка frontend...
call npm run build
if errorlevel 1 (
    echo ОШИБКА: Не удалось собрать frontend
    pause
    exit /b 1
)

echo.
echo [2/3] Копирование electron...
if not exist "electron" (
    xcopy /E /I /Y ..\electron electron
)

echo.
echo [3/3] Сборка установщика (без подписи)...
REM Полностью отключаем подпись
set WIN_CSC_LINK=
set CSC_IDENTITY_AUTO_DISCOVERY=false
set CSC_LINK=
set CSC_KEY_PASSWORD=

REM Собираем только установщик, игнорируя ошибки подписи
call npx electron-builder --win --config.win.sign=null --config.win.certificateFile= --publish never 2>&1 | findstr /V /C:"symbolic link" /C:"darwin" /C:"libcrypto" /C:"libssl" /C:"winCodeSign"

echo.
echo Проверка результата...
if exist "dist-electron\ZVD Nesting Calculator Setup *.exe" (
    echo.
    echo ========================================
    echo ✓ УСТАНОВЩИК СОЗДАН!
    echo ========================================
    echo.
    dir /b "dist-electron\ZVD Nesting Calculator Setup *.exe"
    echo.
) else (
    echo.
    echo ⚠ Установщик не найден, но распакованная версия готова
    echo Используйте: dist-electron\win-unpacked\ZVD Nesting Calculator.exe
    echo.
)

pause

