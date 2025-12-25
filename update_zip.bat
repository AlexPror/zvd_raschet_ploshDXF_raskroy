@echo off
REM Скрипт для обновления ZIP архива из актуальной версии win-unpacked

echo ========================================
echo Обновление ZIP архива
echo ========================================
echo.

cd /d "%~dp0\frontend\dist-electron"

if not exist "win-unpacked\ZVD Nesting Calculator.exe" (
    echo ОШИБКА: win-unpacked не найден!
    echo Сначала соберите портативную версию: .\build_portable.bat
    pause
    exit /b 1
)

echo Удаляю старый ZIP архив...
if exist "ZVD_Nesting_Calculator_Portable.zip" (
    del /Q "ZVD_Nesting_Calculator_Portable.zip"
    echo ✓ Старый ZIP удален
)

echo.
echo Создаю новый ZIP из актуальной версии win-unpacked...
powershell -Command "Compress-Archive -Path 'win-unpacked\*' -DestinationPath 'ZVD_Nesting_Calculator_Portable.zip' -Force"

if exist "ZVD_Nesting_Calculator_Portable.zip" (
    echo.
    echo ========================================
    echo ✓ ZIP АРХИВ ОБНОВЛЕН!
    echo ========================================
    echo.
    for %%F in ("ZVD_Nesting_Calculator_Portable.zip") do (
        set /a sizeMB=%%~zF/1048576
        echo Размер: !sizeMB! MB
        echo Файл: %%~fF
    )
    echo.
    echo Готово к передаче в бухгалтерию!
) else (
    echo ОШИБКА: Не удалось создать ZIP архив
)

pause

