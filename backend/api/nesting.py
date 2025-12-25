#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API для раскроя деталей
"""

from flask import Blueprint, request, jsonify
import logging

from utils.rectpack_optimizer import optimize_nesting
from utils.waste_calculator import calculate_wastes

logger = logging.getLogger(__name__)

nesting_bp = Blueprint('nesting', __name__)


@nesting_bp.route('/calculate', methods=['POST'])
def calculate_nesting():
    """
    Рассчитать раскрой деталей
    
    POST /api/nesting/calculate
    {
        "parts": [
            {"name": "Корпус", "width": 1500, "height": 400, "quantity": 1},
            {"name": "Крышка", "width": 250, "height": 150, "quantity": 4}
        ],
        "sheet_width": 2500,
        "sheet_height": 1250,
        "allow_rotation": true
    }
    """
    try:
        logger.info("=" * 50)
        logger.info("[NESTING API] Получен запрос на расчет раскроя")
        logger.info(f"Headers: {dict(request.headers)}")
        
        data = request.get_json()
        logger.info(f"[NESTING API] Данные запроса: {data}")
        
        if not data:
            logger.error("❌ Пустой JSON в запросе")
            return jsonify({'error': 'Empty request body'}), 400
        
        parts = data.get('parts', [])
        sheet_width = data.get('sheet_width', 2500)
        sheet_height = data.get('sheet_height', 1250)
        allow_rotation = data.get('allow_rotation', True)
        
        logger.info(f"[NESTING API] Параметры: лист {sheet_width}x{sheet_height}, поворот: {allow_rotation}")
        logger.info(f"[NESTING API] Деталей получено: {len(parts)}")
        
        if not parts:
            logger.error("[ERROR] Список деталей пуст")
            return jsonify({'error': 'No parts provided'}), 400
        
        for i, part in enumerate(parts):
            logger.info(f"  Деталь {i+1}: {part.get('name')} - {part.get('width')}x{part.get('height')} (кол-во: {part.get('quantity', 1)})")
        
        logger.info("[NESTING API] Начинаю оптимизацию раскроя...")
        
        # Оптимизация раскроя
        result = optimize_nesting(
            parts=parts,
            sheet_width=sheet_width,
            sheet_height=sheet_height,
            allow_rotation=allow_rotation,
            cut_gap=5.0,  # Зазор между деталями 5мм (отступы накладываются)
            edge_margin=5.0  # Отступ от края листа 5мм со всех сторон
        )
        
        logger.info(f"[NESTING API] Результат оптимизации: success={result.get('success')}")
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"[ERROR] Ошибка оптимизации: {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        logger.info("[NESTING API] Вычисляю обрезки...")
        
        # Вычисляем обрезки
        wastes = calculate_wastes(result)
        result['wastes'] = wastes
        
        logger.info(f"[OK] Раскрой рассчитан: {result['sheets_needed']} листов, "
                   f"{len(wastes)} обрезков, использование {result['utilization_percent']}%")
        logger.info("=" * 50)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"[ERROR] КРИТИЧЕСКАЯ ОШИБКА расчета раскроя: {e}", exc_info=True)
        logger.error(f"Тип ошибки: {type(e).__name__}")
        logger.error("=" * 50)
        return jsonify({'error': str(e)}), 500


@nesting_bp.route('/optimize', methods=['POST'])
def optimize_with_wastes():
    """
    Оптимизировать раскрой с учетом существующих обрезков
    
    POST /api/nesting/optimize
    {
        "parts": [...],
        "use_wastes": true
    }
    """
    try:
        data = request.get_json()
        
        parts = data.get('parts', [])
        use_wastes = data.get('use_wastes', True)
        
        logger.info(f"Оптимизация раскроя (использовать обрезки: {use_wastes})")
        
        # TODO: Реализовать логику с проверкой базы обрезков
        
        result = optimize_nesting(parts=parts)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Ошибка оптимизации: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@nesting_bp.route('/sheets', methods=['GET'])
def get_sheet_sizes():
    """Получить стандартные размеры листов"""
    sheets = [
        {'width': 2500, 'height': 1250, 'name': 'Стандарт'},
        {'width': 3000, 'height': 1500, 'name': 'Большой'},
        {'width': 2000, 'height': 1000, 'name': 'Малый'}
    ]
    
    return jsonify(sheets)

