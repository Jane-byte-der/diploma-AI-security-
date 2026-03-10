"""
Database module for storing feedback and retraining data
Author: Evgeniia Vorobeva
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class FeedbackDatabase:
    """Класс для работы с базой данных обратной связи"""
    
    def __init__(self, db_path='data/feedback.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Инициализация таблиц"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Таблица для обратной связи от аналитиков
        c.execute('''
            CREATE TABLE IF NOT EXISTS analyst_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                timestamp TEXT,
                user_id TEXT,
                verdict TEXT,
                comment TEXT,
                analyst_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для хранения всех обнаружений
        c.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id TEXT,
                timestamp TEXT,
                user_id TEXT,
                anomaly_types TEXT,
                severity TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для истории обучения
        c.execute('''
            CREATE TABLE IF NOT EXISTS training_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT,
                trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_size INTEGER,
                accuracy REAL,
                parameters TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def save_feedback(self, event_id, verdict, comment, analyst="system"):
        """Сохранить решение аналитика"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO analyst_feedback (event_id, verdict, comment, analyst_name)
            VALUES (?, ?, ?, ?)
        ''', (event_id, verdict, comment, analyst))
        conn.commit()
        conn.close()
        logger.info(f"Feedback saved for event {event_id}")
    
    def save_detection(self, detection):
        """Сохранить обнаружение аномалии"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO detections (detection_id, timestamp, user_id, anomaly_types, severity, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            detection.get('id'),
            detection.get('timestamp'),
            detection.get('user_id'),
            detection.get('anomaly_types'),
            detection.get('severity'),
            json.dumps(detection)
        ))
        conn.commit()
        conn.close()
    
    def get_training_data(self):
        """Получить все размеченные данные для обучения"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM analyst_feedback", conn)
        conn.close()
        return df
    
    def log_training(self, model_version, data_size, accuracy, parameters):
        """Записать историю обучения"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO training_history (model_version, data_size, accuracy, parameters)
            VALUES (?, ?, ?, ?)
        ''', (model_version, data_size, accuracy, json.dumps(parameters)))
        conn.commit()
        conn.close()
