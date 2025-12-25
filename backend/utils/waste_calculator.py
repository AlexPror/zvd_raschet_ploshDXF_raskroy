#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Калькулятор обрезков из результата раскроя
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def calculate_wastes(nesting_result: Dict) -> List[Dict]:
    """
    Вычисляет обрезки из результата раскроя
    
    Args:
        nesting_result: результат от optimize_nesting()
    
    Returns:
        список обрезков с размерами и координатами
    """
    
    if not nesting_result.get('success'):
        return []
    
    wastes = []
    waste_counter = 0
    
    for sheet in nesting_result.get('sheets', []):
        sheet_number = sheet['sheet_number']
        
        # Упрощенный расчет: берем waste_area из листа
        # TODO: Реализовать точное определение геометрии обрезков
        
        waste_area_m2 = sheet.get('waste_area_m2', 0)
        
        if waste_area_m2 > 0.02:  # Минимум 200×200 мм = 0.04 м²
            waste_counter += 1
            
            # Примерные размеры обрезка (квадратный)
            waste_size_mm = int((waste_area_m2 * 1_000_000) ** 0.5)
            
            wastes.append({
                'id': f'W-{waste_counter:03d}',
                'sheet_number': sheet_number,
                'width': waste_size_mm,
                'height': waste_size_mm,
                'area_m2': waste_area_m2,
                'usable': waste_size_mm >= 300  # >= 300x300 мм
            })
    
    logger.info(f"Вычислено обрезков: {len(wastes)}")
    
    return wastes

