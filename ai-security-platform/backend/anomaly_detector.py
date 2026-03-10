"""
Anomaly Detection Module for Information Security
Author: Evgeniia Vorobeva
Part of Bachelor's Thesis: AI Integration into Information Security Management Systems
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Класс для обнаружения аномалий в действиях пользователей
    Основан на методике из дипломной работы (Глава 3)
    
    Поддерживает обнаружение:
    - Временных аномалий (temporal)
    - Пространственных аномалий (spatial)
    - Ресурсных аномалий (resource)
    - Интенсивностных аномалий (intensity)
    - Поведенческих аномалий (behavioral)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Инициализация детектора аномалий
        
        Args:
            config: Словарь с параметрами конфигурации
        """
        self.profiles = {}  # профили пользователей
        self.anomaly_history = []  # история обнаружений для обучения
        
        # Типы аномалий (Таблица 3.5 из диплома)
        self.anomaly_types = {
            'temporal': 'Временная аномалия',
            'spatial': 'Пространственная аномалия',
            'resource': 'Ресурсная аномалия',
            'intensity': 'Интенсивностная аномалия',
            'behavioral': 'Поведенческая аномалия'
        }
        
        # Конфигурация с значениями по умолчанию
        self.config = {
            'threshold_multiplier': 2.0,  # множитель для объема данных
            'time_window_start': 8,        # начало рабочего дня (по умолчанию)
            'time_window_end': 19,         # конец рабочего дня
            'internal_ip_prefix': '10.',   # префикс внутренних IP
            'max_data_size_kb': 100000,    # макс размер данных для анализа
            'enable_logging': True,
            'min_history_days': 30,        # мин дней для построения профиля
        }
        
        if config:
            self.config.update(config)
            
        logger.info(f"AnomalyDetector инициализирован с конфигурацией: {self.config}")
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Загрузка данных из CSV с обработкой ошибок
        
        Args:
            file_path: путь к CSV файлу
            
        Returns:
            DataFrame с загруженными данными
            
        Raises:
            FileNotFoundError: если файл не найден
            ValueError: если данные некорректны
        """
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Загружено {len(df)} записей из {file_path}")
        except FileNotFoundError:
            logger.error(f"Файл {file_path} не найден")
            raise
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            raise ValueError(f"Некорректный формат данных: {e}")
        
        # Проверка обязательных колонок
        required_columns = ['Timestamp', 'User_ID', 'User_Role', 'Event_Type', 
                           'Resource', 'IP_Address']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing}")
        
        # Преобразование timestamp с обработкой ошибок
        try:
            df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'], 
                                                format='%d.%m.%Y %H:%M', 
                                                errors='coerce')
            # Удаляем строки с некорректным временем
            df = df.dropna(subset=['Timestamp_dt'])
            df['Hour'] = df['Timestamp_dt'].dt.hour
            df['Day'] = df['Timestamp_dt'].dt.day
            df['Month'] = df['Timestamp_dt'].dt.month
        except Exception as e:
            logger.error(f"Ошибка парсинга timestamp: {e}")
            raise
        
        # Определение типа IP
        df['IP_Type'] = df['IP_Address'].apply(
            lambda x: 'Internal' if str(x).startswith(self.config['internal_ip_prefix']) else 'External'
        )
        
        # Обработка пропусков в Data_Size_KB
        if 'Data_Size_KB' in df.columns:
            df['Data_Size_KB'] = pd.to_numeric(df['Data_Size_KB'], errors='coerce').fillna(0)
        else:
            df['Data_Size_KB'] = 0
        
        logger.info(f"После обработки: {len(df)} записей")
        return df
    
    def build_profiles(self, df: pd.DataFrame) -> Dict:
        """
        Построение профилей пользователей (Таблица 3.4 из диплома)
        
        Args:
            df: DataFrame с историческими данными
            
        Returns:
            Словарь с профилями пользователей
        """
        profiles = {}
        
        for user in df['User_ID'].unique():
            user_data = df[df['User_ID'] == user]
            
            if len(user_data) < 10:  # Минимум данных для профиля
                logger.warning(f"Мало данных для пользователя {user}, пропускаем")
                continue
            
            try:
                # Определяем типичные параметры
                work_hour_mode = user_data['Hour'].mode()
                work_hour = int(work_hour_mode[0]) if not work_hour_mode.empty else 9
                
                ip_mode = user_data['IP_Address'].mode()
                typical_ip = ip_mode[0] if not ip_mode.empty else '10.10.1.1'
                
                profiles[user] = {
                    'role': user_data['User_Role'].iloc[0] if not user_data.empty else 'Unknown',
                    'work_hours_start': work_hour,
                    'work_hours_end': work_hour + 8,  # Предполагаем 8-часовой рабочий день
                    'internal_ip_prefix': self._extract_ip_prefix(typical_ip),
                    'avg_data_size': float(user_data['Data_Size_KB'].mean()),
                    'std_data_size': float(user_data['Data_Size_KB'].std()),
                    'typical_resources': user_data['Resource'].value_counts().head(5).index.tolist(),
                    'total_events': len(user_data),
                    'unique_days': user_data['Day'].nunique(),
                }
                
                logger.debug(f"Построен профиль для {user}: работа с {profiles[user]['work_hours_start']}:00")
                
            except Exception as e:
                logger.error(f"Ошибка построения профиля для {user}: {e}")
                continue
        
        self.profiles = profiles
        logger.info(f"Построено профилей: {len(profiles)}")
        return profiles
    
    def _extract_ip_prefix(self, ip: str) -> str:
        """Извлекает префикс IP (первые 3 октета)"""
        try:
            parts = str(ip).split('.')
            if len(parts) >= 3:
                return f"{parts[0]}.{parts[1]}.{parts[2]}."
        except:
            pass
        return self.config['internal_ip_prefix']
    
    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Обнаружение аномалий (основной метод)
        
        Args:
            df: DataFrame с данными для анализа
            
        Returns:
            DataFrame с помеченными аномалиями
        """
        if not self.profiles:
            logger.warning("Профили не построены, запустите build_profiles()")
            return pd.DataFrame()
        
        results = []
        
        for idx, event in df.iterrows():
            user = event['User_ID']
            profile = self.profiles.get(user)
            
            if not profile:
                # Для неизвестных пользователей - помечаем как потенциальные аномалии
                results.append(self._create_result_row(event, ['unknown_user'], 'medium', idx))
                continue
            
            anomalies_found = []
            severity = 'low'
            details = {}
            
            # Проверка времени (temporal anomaly)
            hour = event['Hour']
            if hour < profile['work_hours_start'] or hour > profile['work_hours_end']:
                anomalies_found.append('temporal')
                details['expected_hours'] = f"{profile['work_hours_start']}-{profile['work_hours_end']}"
                severity = 'medium'
            
            # Проверка IP (spatial anomaly)
            ip = str(event['IP_Address'])
            if not ip.startswith(profile['internal_ip_prefix']):
                anomalies_found.append('spatial')
                details['expected_ip_prefix'] = profile['internal_ip_prefix']
                severity = 'high' if 'temporal' in anomalies_found else 'medium'
            
            # Проверка объема данных (intensity anomaly)
            volume = event.get('Data_Size_KB', 0)
            if volume > 0:
                threshold = profile['avg_data_size'] * self.config['threshold_multiplier']
                if volume > threshold:
                    anomalies_found.append('intensity')
                    details['avg_volume'] = round(profile['avg_data_size'], 2)
                    details['threshold'] = round(threshold, 2)
                    severity = 'high'
            
            # Проверка ресурсов (resource anomaly)
            resource = str(event['Resource'])
            if profile['typical_resources'] and resource not in profile['typical_resources']:
                if len(anomalies_found) >= 1:  # Только если уже есть другие аномалии
                    anomalies_found.append('resource')
                    severity = 'high' if severity == 'high' else 'medium'
            
            # Формируем результат
            result = self._create_result_row(
                event, anomalies_found, severity, idx, details
            )
            results.append(result)
            
            # Сохраняем в историю для дальнейшего обучения
            if anomalies_found:
                self.anomaly_history.append(result)
        
        results_df = pd.DataFrame(results)
        logger.info(f"Обнаружено аномалий: {len(results_df[results_df['is_anomaly']])}")
        
        return results_df
    
    def _create_result_row(self, event: pd.Series, anomalies: List[str], 
                          severity: str, idx: int, details: Optional[Dict] = None) -> Dict:
        """Создает строку результата для события"""
        return {
            'id': idx,
            'timestamp': event['Timestamp'],
            'user_id': event['User_ID'],
            'user_role': event['User_Role'],
            'event_type': event['Event_Type'],
            'resource': event['Resource'],
            'ip_address': event['IP_Address'],
            'ip_type': event.get('IP_Type', 'Unknown'),
            'data_size_kb': event.get('Data_Size_KB', 0),
            'anomaly_types': ','.join(anomalies) if anomalies else 'none',
            'severity': severity if anomalies else 'normal',
            'is_anomaly': len(anomalies) > 0,
            'details': str(details) if details else ''
        }
    
    def get_statistics(self, results_df: pd.DataFrame) -> Dict:
        """
        Возвращает статистику обнаружения
        
        Returns:
            Словарь со статистикой:
            - total_events: всего событий
            - total_anomalies: всего аномалий
            - anomaly_rate: процент аномалий
            - by_severity: распределение по критичности
            - by_user: распределение по пользователям
            - by_type: распределение по типам
        """
        if results_df.empty:
            return {'error': 'Нет данных для анализа'}
        
        anomalies = results_df[results_df['is_anomaly']]
        
        # Распределение по типам аномалий
        type_counts = {}
        for types in anomalies['anomaly_types']:
            for t in str(types).split(','):
                if t != 'none':
                    type_counts[t] = type_counts.get(t, 0) + 1
        
        stats = {
            'total_events': len(results_df),
            'total_anomalies': len(anomalies),
            'anomaly_rate': round(len(anomalies) / len(results_df) * 100, 2),
            'by_severity': anomalies['severity'].value_counts().to_dict(),
            'by_user': anomalies['user_id'].value_counts().head(10).to_dict(),
            'by_type': type_counts,
            'false_positive_candidates': len(anomalies[anomalies['severity'] == 'low'])
        }
        
        return stats
    
    def save_results(self, results_df: pd.DataFrame, output_path: str):
        """Сохраняет результаты в CSV"""
        results_df.to_csv(output_path, index=False)
        logger.info(f"Результаты сохранены в {output_path}")
    
    def get_confusion_matrix(self, results_df: pd.DataFrame, ground_truth_col: str = 'Is_Anomaly') -> Dict:
        """
        Вычисляет матрицу ошибок для оценки качества (Таблица 3.6 из диплома)
        """
        if ground_truth_col not in results_df.columns:
            return {'error': f'Колонка {ground_truth_col} не найдена'}
        
        tp = len(results_df[(results_df['is_anomaly']) & (results_df[ground_truth_col] == 1)])
        fp = len(results_df[(results_df['is_anomaly']) & (results_df[ground_truth_col] == 0)])
        fn = len(results_df[(~results_df['is_anomaly']) & (results_df[ground_truth_col] == 1)])
        tn = len(results_df[(~results_df['is_anomaly']) & (results_df[ground_truth_col] == 0)])
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'precision': round(precision * 100, 2),
            'recall': round(recall * 100, 2),
            'f1_score': round(f1 * 100, 2),
            'accuracy': round((tp + tn) / (tp + tn + fp + fn) * 100, 2)
        }
