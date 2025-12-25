@echo off
REM Сборка установщика с полным отключением подписи

echo ========================================
echo Сборка установщика (без подписи)
echo ========================================
echo.

cd /d "%~dp0\frontend"

REM Полностью отключаем подпись через переменные окружения
set WIN_CSC_LINK=
set CSC_IDENTITY_AUTO_DISCOVERY=false
set CSC_LINK=
set CSC_KEY_PASSWORD=
set CSC_NAME=

REM Удаляем старый установщик
if exist "dist-electron\ZVD Nesting Calculator Setup *.exe" del /Q "dist-electron\ZVD Nesting Calculator Setup *.exe"

echo Сборка установщика...
call npx electron-builder --win --config.win.sign=null --config.win.certificateFile= --config.win.certificatePassword= --publish never 2>&1 | findstr /V /C:"symbolic link" /C:"darwin" /C:"libcrypto" /C:"libssl" /C:"winCodeSign" /C:"code signing" /C:"password"

echo.
if exist "dist-electron\ZVD Nesting Calculator Setup *.exe" (
    echo ========================================
    echo ✓ УСТАНОВЩИК СОЗДАН!
    echo ========================================
    echo.
    dir /b "dist-electron\ZVD Nesting Calculator Setup *.exe"
    echo.
) else (
    echo ⚠ Установщик не создан из-за ошибок подписи
    echo.
    echo Используйте портативную версию:
    echo   - Папка: dist-electron\win-unpacked
    echo   - ZIP: dist-electron\ZVD_Nesting_Calculator_Portable.zip
    echo.
)

pause

