#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API для управления обрезками
"""

from flask import Blueprint, request, jsonify
import logging

from utils.waste_database import WasteDatabase

logger = logging.getLogger(__name__)

wastes_bp = Blueprint('wastes', __name__)
db = WasteDatabase()


@wastes_bp.route('/', methods=['GET'])
def get_all_wastes():
    """
    Получить все обрезки
    
    GET /api/wastes?status=available
    """
    status = request.args.get('status')
    
    wastes = db.get_all(status_filter=status)
    
    return jsonify({
        'success': True,
        'count': len(wastes),
        'wastes': wastes
    })


@wastes_bp.route('/<waste_id>', methods=['GET'])
def get_waste(waste_id):
    """Получить обрезок по ID"""
    waste = db.get_by_id(waste_id)
    
    if not waste:
        return jsonify({'error': 'Waste not found'}), 404
    
    return jsonify(waste)


@wastes_bp.route('/search', methods=['POST'])
def search_suitable_wastes():
    """
    Поиск подходящих обрезков для деталей
    
    POST /api/wastes/search
    {
        "parts": [
            {"name": "Распорка", "width": 298, "height": 122}
        ],
        "material": "Оцинковка 1.5мм"
    }
    """
    try:
        data = request.get_json()
        
        parts = data.get('parts', [])
        material = data.get('material', 'Оцинковка 1.5мм')
        
        if not parts:
            return jsonify({'error': 'No parts provided'}), 400
        
        logger.info(f"Поиск обрезков для {len(parts)} деталей")
        
        matches = []
        
        for part in parts:
            suitable = db.find_suitable(
                width=part['width'],
                height=part['height'],
                material=material
            )
            
            if suitable:
                matches.append({
                    'part': part,
                    'waste': suitable,
                    'economy_rub': suitable.get('economy_rub', 0)
                })
        
        total_economy = sum(m['economy_rub'] for m in matches)
        
        return jsonify({
            'success': True,
            'found': len(matches) > 0,
            'matches': matches,
            'total_economy': total_economy
        })
        
    except Exception as e:
        logger.error(f"Ошибка поиска обрезков: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@wastes_bp.route('/', methods=['POST'])
def add_waste():
    """
    Добавить новый обрезок
    
    POST /api/wastes
    {
        "width": 710,
        "height": 710,
        "material": "Оцинковка 1.5мм",
        "project": "LITE.154.160.1400",
        "order": "А-12158-1544"
    }
    """
    try:
        data = request.get_json()
        
        waste_id = db.add(data)
        
        return jsonify({
            'success': True,
            'waste_id': waste_id
        })
        
    except Exception as e:
        logger.error(f"Ошибка добавления обрезка: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@wastes_bp.route('/<waste_id>', methods=['PUT'])
def update_waste(waste_id):
    """Обновить обрезок"""
    try:
        data = request.get_json()
        
        success = db.update(waste_id, data)
        
        if not success:
            return jsonify({'error': 'Waste not found'}), 404
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Ошибка обновления обрезка: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@wastes_bp.route('/<waste_id>', methods=['DELETE'])
def delete_waste(waste_id):
    """Удалить обрезок"""
    try:
        success = db.delete(waste_id)
        
        if not success:
            return jsonify({'error': 'Waste not found'}), 404
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Ошибка удаления обрезка: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@wastes_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Получить статистику по обрезкам"""
    stats = db.get_statistics()
    
    return jsonify(stats)

