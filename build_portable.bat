@echo off
REM Сборка портативной версии (без установщика)

echo ========================================
echo Сборка портативной версии ZVD Nesting Calculator
echo ========================================
echo.

cd /d "%~dp0\frontend"

echo [1/3] Сборка frontend...
call npm run build
if errorlevel 1 exit /b 1

echo.
echo [2/3] Копирование electron...
if not exist "electron" (
    xcopy /E /I /Y ..\electron electron
)

echo.
echo [3/3] Сборка портативной версии (без установщика)...
set WIN_CSC_LINK=
set CSC_IDENTITY_AUTO_DISCOVERY=false
set CSC_LINK=
set CSC_KEY_PASSWORD=

REM Собираем только распакованную версию (portable)
call npx electron-builder --win --config.win.target=dir --config.win.sign=null 2>&1 | findstr /V /C:"symbolic link" /C:"darwin" /C:"libcrypto" /C:"libssl" /C:"winCodeSign" /C:"code signing"

echo.
if exist "dist-electron\win-unpacked\ZVD Nesting Calculator.exe" (
    echo ========================================
    echo ✓ ПОРТАТИВНАЯ ВЕРСИЯ ГОТОВА!
    echo ========================================
    echo.
    echo Папка: dist-electron\win-unpacked
    echo Запуск: ZVD Nesting Calculator.exe
    echo.
    echo Можно скопировать всю папку win-unpacked на другой компьютер
    echo.
) else (
    echo ОШИБКА: Портативная версия не создана
)

pause

