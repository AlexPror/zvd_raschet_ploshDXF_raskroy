#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
База данных обрезков (SQLite)
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class WasteDatabase:
    """Управление базой данных обрезков"""
    
    def __init__(self, db_path: str = 'wastes.db'):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wastes (
                id TEXT PRIMARY KEY,
                width REAL NOT NULL,
                height REAL NOT NULL,
                area_m2 REAL NOT NULL,
                material TEXT NOT NULL,
                project TEXT,
                order_number TEXT,
                date_created TEXT NOT NULL,
                location TEXT,
                status TEXT DEFAULT 'available',
                used_in TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"База данных инициализирована: {self.db_path}")
    
    def get_all(self, status_filter: Optional[str] = None) -> List[Dict]:
        """Получить все обрезки"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute('SELECT * FROM wastes WHERE status = ?', (status_filter,))
        else:
            cursor.execute('SELECT * FROM wastes')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_by_id(self, waste_id: str) -> Optional[Dict]:
        """Получить обрезок по ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM wastes WHERE id = ?', (waste_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def find_suitable(self, width: float, height: float, 
                     material: str = 'Оцинковка 1.5мм') -> Optional[Dict]:
        """Найти подходящий обрезок"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        gap = 10  # Зазор резки
        
        cursor.execute('''
            SELECT * FROM wastes 
            WHERE status = 'available' 
            AND material = ?
            AND (
                (width >= ? AND height >= ?) OR
                (width >= ? AND height >= ?)
            )
            ORDER BY area_m2 ASC
            LIMIT 1
        ''', (material, width + gap, height + gap, height + gap, width + gap))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            # Расчет экономии
            part_area_m2 = (width * height) / 1_000_000
            result['economy_rub'] = round(part_area_m2 * 3500, 2)
            return result
        
        return None
    
    def add(self, waste_data: Dict) -> str:
        """Добавить новый обрезок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Генерируем ID
        cursor.execute('SELECT COUNT(*) FROM wastes')
        count = cursor.fetchone()[0]
        waste_id = f"W-{count + 1:03d}"
        
        cursor.execute('''
            INSERT INTO wastes (
                id, width, height, area_m2, material, project, 
                order_number, date_created, location, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            waste_id,
            waste_data['width'],
            waste_data['height'],
            waste_data.get('area_m2', (waste_data['width'] * waste_data['height']) / 1_000_000),
            waste_data.get('material', 'Оцинковка 1.5мм'),
            waste_data.get('project'),
            waste_data.get('order'),
            datetime.now().isoformat(),
            waste_data.get('location', ''),
            'available'
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Добавлен обрезок {waste_id}")
        
        return waste_id
    
    def update(self, waste_id: str, updates: Dict) -> bool:
        """Обновить обрезок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем существование
        cursor.execute('SELECT id FROM wastes WHERE id = ?', (waste_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Обновляем
        update_fields = []
        values = []
        
        for field in ['status', 'location', 'used_in', 'notes']:
            if field in updates:
                update_fields.append(f'{field} = ?')
                values.append(updates[field])
        
        if update_fields:
            values.append(waste_id)
            query = f"UPDATE wastes SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
        
        logger.info(f"Обновлен обрезок {waste_id}")
        
        return True
    
    def delete(self, waste_id: str) -> bool:
        """Удалить обрезок"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM wastes WHERE id = ?', (waste_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        if deleted:
            logger.info(f"Удален обрезок {waste_id}")
        
        return deleted
    
    def get_statistics(self) -> Dict:
        """Получить статистику"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM wastes')
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM wastes WHERE status = 'available'")
        available = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM wastes WHERE status = 'used'")
        used = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(area_m2) FROM wastes WHERE status = 'available'")
        total_area = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total': total,
            'available': available,
            'used': used,
            'total_area_m2': round(total_area, 4),
            'total_value_rub': round(total_area * 3500, 2),
            'reuse_percent': round((used / total * 100) if total > 0 else 0, 2)
        }

