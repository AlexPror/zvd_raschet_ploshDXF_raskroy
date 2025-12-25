@echo off
REM Простая сборка без подписи

echo Сборка ZVD Nesting Calculator...
echo.

cd /d "%~dp0\frontend"

echo [1/2] Сборка frontend...
call npm run build
if errorlevel 1 exit /b 1

echo.
echo [2/2] Сборка Electron (может быть предупреждение о подписи - это нормально)...
if not exist "electron" (
    xcopy /E /I /Y ..\electron electron
)

REM Отключаем подпись полностью
set WIN_CSC_LINK=
set CSC_IDENTITY_AUTO_DISCOVERY=false
set CSC_LINK=

call npx --yes electron-builder --win --config.win.sign=null 2>&1 | findstr /V "symbolic link darwin libcrypto libssl"

echo.
if exist "dist-electron\ZVD Nesting Calculator Setup *.exe" (
    echo ✓ УСТАНОВЩИК СОЗДАН!
    echo.
    echo Файл: dist-electron\ZVD Nesting Calculator Setup 1.0.0.exe
    echo.
    echo Инструкция для бухгалтерии: ..\INSTALLATION_GUIDE.md
) else (
    echo Проверьте папку dist-electron\
)

pause

