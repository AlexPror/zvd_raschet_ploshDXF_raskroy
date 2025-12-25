#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оптимизатор раскроя с использованием rectpack
Адаптирован для веб-интерфейса
"""

import logging
from typing import List, Dict

try:
    from rectpack import newPacker, PackingMode, PackingBin
    RECTPACK_AVAILABLE = True
except ImportError:
    RECTPACK_AVAILABLE = False

logger = logging.getLogger(__name__)


def optimize_nesting(parts: List[Dict], sheet_width: float = 2500, 
                     sheet_height: float = 1250, allow_rotation: bool = True,
                     cut_gap: float = 5.0, edge_margin: float = 10.0) -> Dict:
    """
    Оптимизирует раскрой деталей на листах
    
    Args:
        parts: список деталей [{'name': str, 'width': float, 'height': float, 'quantity': int}]
        sheet_width: ширина листа
        sheet_height: высота листа
        allow_rotation: разрешить поворот деталей
    
    Returns:
        {
            'success': bool,
            'sheets_needed': int,
            'utilization_percent': float,
            'sheets': [...]  # данные по каждому листу
        }
    """
    
    if not RECTPACK_AVAILABLE:
        return {
            'success': False,
            'error': 'rectpack not installed. Run: pip install rectpack'
        }
    
    try:
        logger.info(f"[NESTING] Оптимизация раскроя: {len(parts)} деталей")
        logger.info(f"   Лист: {sheet_width}x{sheet_height} мм")
        logger.info(f"   Поворот: {allow_rotation}")
        
        if not RECTPACK_AVAILABLE:
            logger.error("[ERROR] rectpack не установлен!")
            return {
                'success': False,
                'error': 'rectpack not installed. Run: pip install rectpack'
            }
        
        logger.info("[NESTING] Создаю packer...")
        
        # Создаем packer с упрощенными параметрами
        # Используем более простую конфигурацию, чтобы избежать ошибок
        try:
            packer = newPacker(
                rotation=allow_rotation
            )
            logger.info("[NESTING] Packer создан (простая конфигурация)")
        except Exception as packer_error:
            logger.error(f"[ERROR] Ошибка создания packer: {packer_error}", exc_info=True)
            # Пробуем еще более простой вариант
            try:
                packer = newPacker()
                logger.info("[NESTING] Packer создан (минимальная конфигурация)")
            except Exception as packer_error2:
                logger.error(f"[ERROR] Критическая ошибка создания packer: {packer_error2}", exc_info=True)
                return {
                    'success': False,
                    'error': f'Ошибка создания packer: {str(packer_error2)}'
                }
        
        # Зазоры для раскроя
        # cut_gap - зазор между деталями (5мм между деталями)
        # edge_margin - отступ от края листа (5мм со всех сторон)
        # Отступы могут накладываться, поэтому добавляем только половину зазора к каждой стороне детали
        logger.info(f"[NESTING] Зазоры: между деталями {cut_gap} мм, от края {edge_margin} мм")
        
        # Рабочая область листа (с учетом отступов от краев)
        # edge_margin - отступ от края листа (5мм со всех сторон)
        # cut_gap/2 - половина зазора, которая будет добавлена к координатам детали с каждой стороны
        # rectpack размещает детали размером (width + cut_gap) x (height + cut_gap)
        # Реальная деталь будет смещена на cut_gap/2 от координат rectpack
        # Итого: рабочая область = лист - 2*edge_margin - cut_gap (чтобы учесть зазор cut_gap/2 с каждой стороны)
        # Это гарантирует, что деталь не выйдет за границы листа
        usable_width = sheet_width - 2 * edge_margin - cut_gap
        usable_height = sheet_height - 2 * edge_margin - cut_gap
        
        if usable_width <= 0 or usable_height <= 0:
            logger.error(f"[ERROR] Рабочая область некорректна: {usable_width}x{usable_height} (лист {sheet_width}x{sheet_height}, edge_margin={edge_margin}, cut_gap={cut_gap})")
            return {
                'success': False,
                'error': f'Рабочая область слишком мала: {usable_width:.1f}x{usable_height:.1f} мм'
            }
        
        # Добавляем листы (неограниченное количество)
        # Используем bid для идентификации листов (как в старом проекте)
        MAX_SHEETS = 100
        logger.info(f"[NESTING] Добавляю листы (макс. {MAX_SHEETS})...")
        logger.info(f"[NESTING] Размер листа: {sheet_width}x{sheet_height} мм")
        logger.info(f"[NESTING] Рабочая область: {usable_width}x{usable_height} мм")
        for i in range(MAX_SHEETS):
            packer.add_bin(usable_width, usable_height, bid=i+1)
        logger.info("[NESTING] Листы добавлены")
        
        # Добавляем детали с учетом зазоров
        # Создаем карту позиций для нумерации (по имени детали)
        position_map = {}  # name -> position_number
        position_counter = 1
        total_rects = 0
        logger.info("[NESTING] Добавляю детали с зазорами...")
        for part in parts:
            quantity = part.get('quantity', 1)
            width = part.get('width', 0)
            height = part.get('height', 0)
            name = part.get('name', 'unknown')
            
            logger.info(f"   {name}: {width}x{height} мм x {quantity} шт.")
            
            if width <= 0 or height <= 0:
                logger.warning(f"   [WARN] Пропущена деталь с некорректными размерами: {name}")
                continue
            
            # Проверяем, помещается ли деталь в рабочую область (с учетом зазора)
            # Учитываем возможность поворота: деталь может поместиться, если повернуть
            width_with_gap = width + cut_gap
            height_with_gap = height + cut_gap
            
            # Проверяем оба варианта: обычный и повернутый
            fits_normal = width_with_gap <= usable_width and height_with_gap <= usable_height
            fits_rotated = height_with_gap <= usable_width and width_with_gap <= usable_height
            
            if not fits_normal and not fits_rotated:
                logger.warning(f"   [WARN] Деталь {name} ({width}x{height} мм) не помещается в рабочую область "
                             f"({usable_width}x{usable_height} мм) даже с учетом зазора и поворота")
                # Пропускаем эту деталь, но продолжаем обработку остальных
                continue
            elif not fits_normal and fits_rotated:
                logger.info(f"   [INFO] Деталь {name} поместится только при повороте (будет {height}x{width} мм)")
            
            # Присваиваем номер позиции для этой детали (если еще не присвоен)
            if name not in position_map:
                position_map[name] = position_counter
                position_counter += 1
            
            for i in range(quantity):
                rid = f"{name}_{i}"
                packer.add_rect(
                    width_with_gap, 
                    height_with_gap,
                    rid=rid
                )
                total_rects += 1
        
        logger.info(f"[NESTING] Добавлено {total_rects} прямоугольников")
        
        # Выполняем раскрой
        logger.info("[NESTING] Выполняю упаковку...")
        try:
            packer.pack()
            logger.info("[NESTING] Упаковка завершена")
        except Exception as pack_error:
            logger.error(f"[ERROR] Ошибка выполнения упаковки: {pack_error}", exc_info=True)
            return {
                'success': False,
                'error': f'Ошибка упаковки: {str(pack_error)}'
            }
        
        # Собираем результаты
        logger.info("[NESTING] Собираю результаты...")
        sheets = []
        sheet_area = sheet_width * sheet_height
        total_parts_area = 0
        
        bin_count = 0
        for bin_idx, bin_obj in enumerate(packer, 1):
            bin_count += 1
            sheet_parts = []
            sheet_used_area = 0
            
            try:
                # Преобразуем bin в list для безопасной итерации
                bin_list = list(bin_obj) if hasattr(bin_obj, '__iter__') else []
                logger.info(f"[NESTING] Bin {bin_idx}: {len(bin_list)} прямоугольников")
                
                if len(bin_list) == 0:
                    continue  # Пропускаем пустые листы
                
                for rect_idx, rect in enumerate(bin_list):
                    try:
                        # Используем атрибуты объекта Rectangle
                        # rect.x, rect.y - координаты левого верхнего угла детали С зазором
                        # rect.width, rect.height - размеры детали С зазором
                        x = float(rect.x)
                        y = float(rect.y)
                        width = float(rect.width)  # Размер с зазором
                        height = float(rect.height)  # Размер с зазором
                        rid = getattr(rect, 'rid', None)
                        
                        logger.debug(f"[NESTING] Rect из packer: rid={rid}, x={x:.1f}, y={y:.1f}, w={width:.1f}, h={height:.1f}")
                        
                        if rid is None:
                            logger.warning(f"[NESTING] Rect без rid, пропускаю")
                            continue
                        
                        # Преобразуем rid в строку
                        if not isinstance(rid, str):
                            rid = str(rid)
                        
                        # Находим оригинальную деталь по rid
                        # rid в формате "name_0", "name_1" и т.д.
                        part_name = rid
                        if '_' in rid:
                            # Извлекаем имя детали (убираем последний индекс)
                            potential_name = rid.rsplit('_', 1)[0]
                            # Проверяем, есть ли такая деталь в списке
                            for p in parts:
                                if p.get('name') == potential_name:
                                    part_name = potential_name
                                    break
                        
                        # Ищем оригинальную деталь
                        original_part = None
                        for p in parts:
                            if p.get('name') == part_name:
                                original_part = p
                                break
                        
                        # Используем оригинальные размеры (без зазора)
                        if original_part:
                            orig_width = float(original_part.get('width', 0))
                            orig_height = float(original_part.get('height', 0))
                        else:
                            # Если не нашли оригинальную деталь, вычитаем зазор из размеров rectpack
                            orig_width = width - cut_gap
                            orig_height = height - cut_gap
                        
                        # Определяем поворот (как в старом проекте)
                        # Сравниваем ширину из rectpack (с зазором) с ожидаемой шириной (оригинал + зазор)
                        # Если ширина не совпадает, значит деталь повернута
                        rotated = False
                        if original_part:
                            expected_width_with_gap = orig_width + cut_gap
                            expected_height_with_gap = orig_height + cut_gap
                            
                            # Проверяем, совпадает ли ширина ИЛИ высота (если повернута, то размеры поменяются местами)
                            width_matches = abs(width - expected_width_with_gap) <= 1.0
                            height_matches = abs(height - expected_height_with_gap) <= 1.0
                            
                            # Если НЕ совпадают ни ширина, ни высота, значит повернута
                            # Или если совпадает высота с ожидаемой шириной
                            if not width_matches and not height_matches:
                                # Проверяем, не поменялись ли размеры местами
                                if abs(width - expected_height_with_gap) <= 1.0 and abs(height - expected_width_with_gap) <= 1.0:
                                    rotated = True
                            elif height_matches and not width_matches:
                                # Высота совпадает с ожидаемой шириной - значит повернута
                                rotated = True
                            
                            logger.info(f"[NESTING] {part_name}: rectpack {width:.1f}x{height:.1f}, "
                                       f"оригинал {orig_width:.1f}x{orig_height:.1f}, "
                                       f"ожидалось {expected_width_with_gap:.1f}x{expected_height_with_gap:.1f}, "
                                       f"повернута: {rotated}")
                        
                        # Если деталь повернута, меняем местами размеры для правильного размещения
                        if rotated:
                            # При повороте на 90° ширина становится высотой и наоборот
                            final_width = orig_height
                            final_height = orig_width
                        else:
                            final_width = orig_width
                            final_height = orig_height
                        
                        # Получаем номер позиции по имени детали
                        position_number = position_map.get(part_name, 0)
                        
                        # КРИТИЧЕСКИ ВАЖНО: Правильный расчет координат с учетом разделения зазора пополам
                        # rectpack разместил деталь размером (width + cut_gap) x (height + cut_gap) в координатах (x, y)
                        # Это координаты левого верхнего угла области с зазором
                        # 
                        # Реальная деталь должна быть смещена на cut_gap/2 от координат rectpack
                        # чтобы создать зазор cut_gap/2 слева/сверху и cut_gap/2 справа/снизу
                        # Между двумя деталями будет зазор cut_gap (2.5мм + 2.5мм = 5мм)
                        # 
                        # Добавляем edge_margin для перехода к координатам полного листа
                        # edge_margin - это отступ от края листа (5мм со всех сторон)
                        final_x = x + edge_margin + (cut_gap / 2.0)
                        final_y = y + edge_margin + (cut_gap / 2.0)
                        
                        # ВАЖНО: Проверяем, что координаты и размеры правильные
                        # rectpack разместил деталь с зазором в (x, y) размером (width, height) где width и height уже включают зазор
                        # Мы используем оригинальные размеры (orig_width, orig_height) в тех же координатах
                        # Это правильно, так как зазор уже учтен при размещении
                        
                        # Проверяем пересечения с другими деталями на этом листе
                        for existing_part in sheet_parts:
                            # Проверяем, не пересекается ли новая деталь с уже размещенной
                            if not (final_x + final_width <= existing_part['x'] or 
                                   existing_part['x'] + existing_part['width'] <= final_x or
                                   final_y + final_height <= existing_part['y'] or 
                                   existing_part['y'] + existing_part['height'] <= final_y):
                                logger.warning(f"[NESTING] Пересечение деталей: {part_name} с {existing_part['name']}")
                                logger.warning(f"  {part_name}: x={final_x:.1f}, y={final_y:.1f}, w={final_width:.1f}, h={final_height:.1f} (повернута: {rotated})")
                                logger.warning(f"  {existing_part['name']}: x={existing_part['x']:.1f}, y={existing_part['y']:.1f}, w={existing_part['width']:.1f}, h={existing_part['height']:.1f}")
                        
                        # Проверяем, что деталь не выходит за границы листа
                        # Учитываем, что справа и снизу должен остаться зазор cut_gap/2
                        max_x = sheet_width - (cut_gap / 2.0)
                        max_y = sheet_height - (cut_gap / 2.0)
                        
                        x2 = final_x + final_width
                        y2 = final_y + final_height
                        
                        if x2 > max_x or y2 > max_y:
                            logger.error(f"[ERROR] Деталь {part_name} ВЫХОДИТ за границы листа!")
                            logger.error(f"  Координаты: x={final_x:.1f}, y={final_y:.1f}, x2={x2:.1f}, y2={y2:.1f}")
                            logger.error(f"  Размеры: {orig_width:.1f}x{orig_height:.1f} мм")
                            logger.error(f"  Границы листа: {sheet_width}x{sheet_height} мм, максимум: x2<={max_x:.1f}, y2<={max_y:.1f}")
                            logger.error(f"  Рабочая область была: {usable_width}x{usable_height} мм")
                            logger.error(f"  rectpack координаты: x={x:.1f}, y={y:.1f}, размер с зазором: {width:.1f}x{height:.1f}")
                            # Не добавляем деталь, которая выходит за границы
                            continue
                        
                        sheet_parts.append({
                            'name': part_name,
                            'width': final_width,
                            'height': final_height,
                            'x': final_x,
                            'y': final_y,
                            'rotated': rotated,
                            'position_number': position_number,
                            'area_m2': (final_width * final_height) / 1_000_000
                        })
                        
                        # Используем финальные размеры для расчета площади (уже с учетом поворота)
                        part_area = final_width * final_height
                        sheet_used_area += part_area
                        total_parts_area += part_area
                        
                    except Exception as rect_error:
                        logger.error(f"[ERROR] Ошибка обработки rect: {rect_error}", exc_info=True)
                        logger.error(f"[ERROR] Rect: {rect}, тип: {type(rect)}")
                        continue
                        
            except Exception as bin_error:
                logger.error(f"[ERROR] Ошибка обработки bin {bin_idx}: {bin_error}", exc_info=True)
                continue
            
            if sheet_parts:  # Только заполненные листы
                utilization = (sheet_used_area / sheet_area) * 100
                waste = sheet_area - sheet_used_area
                
                sheets.append({
                    'sheet_number': bin_idx,
                    'parts_count': len(sheet_parts),
                    'parts': sheet_parts,
                    'used_area_m2': sheet_used_area / 1_000_000,
                    'waste_area_m2': waste / 1_000_000,
                    'utilization_percent': round(utilization, 2)
                })
        
        sheets_needed = len(sheets)
        total_sheet_area = sheets_needed * sheet_area
        overall_utilization = (total_parts_area / total_sheet_area) * 100 if total_sheet_area > 0 else 0
        total_waste = total_sheet_area - total_parts_area
        
        logger.info(f"[NESTING] Статистика: {bin_count} бинов обработано, {sheets_needed} листов заполнено")
        logger.info(f"   Площадь деталей: {total_parts_area / 1_000_000:.4f} м²")
        logger.info(f"   Площадь листов: {total_sheet_area / 1_000_000:.4f} м²")
        logger.info(f"   Использование: {overall_utilization:.2f}%")
        
        # Создаем сводную таблицу позиций
        positions_summary = []
        position_data = {}  # position_number -> {name, width, height, area_m2, quantity, total_area_m2}
        
        for sheet in sheets:
            for part in sheet['parts']:
                pos_num = part.get('position_number', 0)
                if pos_num > 0:
                    if pos_num not in position_data:
                        position_data[pos_num] = {
                            'position_number': pos_num,
                            'name': part['name'],
                            'width': part.get('width', 0),
                            'height': part.get('height', 0),
                            'area_m2': part.get('area_m2', 0),
                            'quantity': 0,
                            'total_area_m2': 0
                        }
                    position_data[pos_num]['quantity'] += 1
                    position_data[pos_num]['total_area_m2'] += part.get('area_m2', 0)
        
        # Преобразуем в список и сортируем по номеру позиции
        positions_summary = sorted(position_data.values(), key=lambda x: x['position_number'])
        
        result = {
            'success': True,
            'sheets_needed': sheets_needed,
            'utilization_percent': round(overall_utilization, 2),
            'waste_percent': round(100 - overall_utilization, 2),
            'total_parts_area_m2': round(total_parts_area / 1_000_000, 4),
            'total_sheet_area_m2': round(total_sheet_area / 1_000_000, 4),
            'total_waste_area_m2': round(total_waste / 1_000_000, 4),
            'sheets': sheets,
            'sheet_width': sheet_width,
            'sheet_height': sheet_height,
            'positions_summary': positions_summary
        }
        
        logger.info(f"[OK] Раскрой оптимизирован: {sheets_needed} листов, "
                   f"использование {overall_utilization:.1f}%")
        
        return result
        
    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"[ERROR] КРИТИЧЕСКАЯ ОШИБКА оптимизации раскроя: {e}", exc_info=True)
        logger.error(f"Тип ошибки: {type(e).__name__}")
        logger.error(f"Аргументы: parts={len(parts) if parts else 0}, sheet={sheet_width}x{sheet_height}")
        logger.error("=" * 50)
        return {
            'success': False,
            'error': str(e)
        }

