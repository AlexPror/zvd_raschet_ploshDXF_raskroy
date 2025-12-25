#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсинг размеров из DXF файлов
"""

import ezdxf
import logging

logger = logging.getLogger(__name__)


def parse_dxf_dimensions(dxf_path: str):
    """
    Получить габариты из DXF файла
    
    Returns:
        (width, height) в мм
    """
    try:
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        # Находим габариты
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for entity in msp:
            try:
                # Линия
                if entity.dxftype() == 'LINE':
                    min_x = min(min_x, entity.dxf.start.x, entity.dxf.end.x)
                    max_x = max(max_x, entity.dxf.start.x, entity.dxf.end.x)
                    min_y = min(min_y, entity.dxf.start.y, entity.dxf.end.y)
                    max_y = max(max_y, entity.dxf.start.y, entity.dxf.end.y)
                
                # Полилиния
                elif entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                    points = entity.get_points('xy') if hasattr(entity, 'get_points') else []
                    for point in points:
                        min_x = min(min_x, point[0])
                        max_x = max(max_x, point[0])
                        min_y = min(min_y, point[1])
                        max_y = max(max_y, point[1])
                
                # Окружность
                elif entity.dxftype() == 'CIRCLE':
                    center = entity.dxf.center
                    radius = entity.dxf.radius
                    min_x = min(min_x, center.x - radius)
                    max_x = max(max_x, center.x + radius)
                    min_y = min(min_y, center.y - radius)
                    max_y = max(max_y, center.y + radius)
                
                # Дуга
                elif entity.dxftype() == 'ARC':
                    center = entity.dxf.center
                    radius = entity.dxf.radius
                    min_x = min(min_x, center.x - radius)
                    max_x = max(max_x, center.x + radius)
                    min_y = min(min_y, center.y - radius)
                    max_y = max(max_y, center.y + radius)
                
            except:
                pass
        
        if min_x != float('inf'):
            width = abs(max_x - min_x)
            height = abs(max_y - min_y)
            return (width, height)
        
        return (None, None)
        
    except Exception as e:
        logger.error(f"Ошибка чтения DXF: {e}")
        return (None, None)

