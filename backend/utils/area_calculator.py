#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расчет площадей с зазорами
"""

def calculate_total_area(parts, cut_gap=5, edge_margin=10):
    """
    Рассчитать итоговую площадь с зазорами
    
    Args:
        parts: список деталей [{'width': float, 'height': float, 'quantity': int}]
        cut_gap: зазор резки (мм)
        edge_margin: отступ от края (мм)
    
    Returns:
        {
            'total_area_m2': float,  # Чистая площадь
            'total_area_with_gaps_m2': float,  # С зазорами
            'parts_count': int,  # Количество деталей
            'parts': [...]  # Детали с расчетами
        }
    """
    
    results = []
    total_area = 0
    total_area_with_gaps = 0
    total_parts_count = 0
    
    for part in parts:
        width = part['width']
        height = part['height']
        quantity = part.get('quantity', 1)
        
        # Чистая площадь одной детали
        area_one = (width * height) / 1_000_000
        
        # Площадь с зазорами
        width_with_gap = width + 2 * cut_gap
        height_with_gap = height + 2 * edge_margin
        area_with_gap_one = (width_with_gap * height_with_gap) / 1_000_000
        
        # Итого
        area_total = area_one * quantity
        area_with_gap_total = area_with_gap_one * quantity
        
        total_area += area_total
        total_area_with_gaps += area_with_gap_total
        total_parts_count += quantity
        
        results.append({
            'name': part.get('name', ''),
            'width': width,
            'height': height,
            'quantity': quantity,
            'area_one_m2': round(area_one, 4),
            'area_total_m2': round(area_total, 4),
            'area_with_gap_m2': round(area_with_gap_total, 4)
        })
    
    return {
        'success': True,
        'total_area_m2': round(total_area, 4),
        'total_area_with_gaps_m2': round(total_area_with_gaps, 4),
        'parts_count': total_parts_count,
        'parts': results
    }

