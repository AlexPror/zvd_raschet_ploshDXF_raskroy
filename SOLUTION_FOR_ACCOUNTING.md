# ✅ Решение: Портативная версия вместо установщика

## Проблема
Установщик `ZVD Nesting Calculator Setup 1.0.0.exe` не запускается из-за проблем с подписью кода.

## Решение: Использовать портативную версию

### Вариант 1: ZIP архив (РЕКОМЕНДУЕТСЯ)

**Файл:** `frontend\dist-electron\ZVD_Nesting_Calculator_Portable.zip`

**Инструкция для бухгалтерии:**
1. Распаковать ZIP архив в любую папку (например, `C:\Program Files\ZVD Nesting Calculator\`)
2. Запустить `ZVD Nesting Calculator.exe`
3. **ВАЖНО:** Установить Python 3.8+ и зависимости (см. ниже)

### Вариант 2: Папка win-unpacked

**Папка:** `frontend\dist-electron\win-unpacked\`

**Инструкция для бухгалтерии:**
1. Скопировать всю папку `win-unpacked` на компьютер
2. Переименовать папку в `ZVD Nesting Calculator`
3. Запустить `ZVD Nesting Calculator.exe`
4. **ВАЖНО:** Установить Python 3.8+ и зависимости

## Что передать в бухгалтерию

### Обязательно:
1. **ZIP архив:** `ZVD_Nesting_Calculator_Portable.zip`
   ИЛИ
   **Папка:** `win-unpacked` (скопировать всю папку)

2. **Инструкция:** `INSTALLATION_GUIDE.md`

### Дополнительно:
- `README_FOR_ACCOUNTING.md` - краткая инструкция

## Инструкция для бухгалтерии

### Шаг 1: Распаковка
1. Распаковать `ZVD_Nesting_Calculator_Portable.zip` в папку
   Например: `C:\Program Files\ZVD Nesting Calculator\`

### Шаг 2: Установка Python
1. Скачать Python 3.8+ с https://www.python.org/downloads/
2. При установке **обязательно** отметить "Add Python to PATH"
3. Проверить установку: открыть командную строку и ввести `py --version`

### Шаг 3: Установка зависимостей Python
1. Открыть командную строку (Win+R → cmd)
2. Перейти в папку backend:
   ```cmd
   cd "C:\Program Files\ZVD Nesting Calculator\resources\backend"
   ```
3. Установить зависимости:
   ```cmd
   py -m pip install -r requirements.txt
   ```

### Шаг 4: Запуск
1. Запустить `ZVD Nesting Calculator.exe` из папки приложения
2. Приложение готово к работе!

## Создание ярлыка на рабочем столе

1. Правой кнопкой на `ZVD Nesting Calculator.exe`
2. Выбрать "Создать ярлык"
3. Переместить ярлык на рабочий стол

## Преимущества портативной версии

✅ Не требует установки  
✅ Можно запускать с флешки  
✅ Не оставляет следов в реестре  
✅ Легко удалить (просто удалить папку)

## Решение проблем

**Приложение не запускается:**
- Проверьте Python: `py --version`
- Установите зависимости Python
- Попробуйте запустить от имени администратора

**Ошибка "Python not found":**
- Установите Python с https://www.python.org/downloads/
- Убедитесь, что отмечено "Add Python to PATH"
- Перезагрузите компьютер

---

**Версия:** 1.0.0  
**Дата:** 2025-12-25

