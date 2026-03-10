"""
Profile Generator Module for Role-Based Clustering
Author: Evgeniia Vorobeva
Based on observation from thesis (Section 3.3.1): correlation between role and behavior
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class ProfileGenerator:
    """
    Генератор типовых профилей на основе кластеризации
    Реализует наблюдение из диплома о корреляции роли и поведения
    """
    
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.profiles = {}
        self.cluster_labels = None
    
    def extract_features(self, df):
        """
        Извлекает признаки для каждого пользователя
        
        Args:
            df: DataFrame с данными
            
        Returns:
            features: массив признаков
            user_names: список пользователей
        """
        user_features = []
        user_names = []
        
        for user in df['User_ID'].unique():
            user_data = df[df['User_ID'] == user]
            
            if len(user_data) < 5:
                continue
            
            # Признаки для кластеризации
            features = [
                user_data['Hour'].mean(),  # среднее время входа
                user_data['Hour'].std(),   # вариативность времени
                user_data['Data_Size_KB'].mean() if 'Data_Size_KB' in user_data else 0,
                user_data['Data_Size_KB'].std() if 'Data_Size_KB' in user_data else 0,
                len(user_data['IP_Address'].unique()),  # количество уникальных IP
                user_data['Event_Type'].nunique(),  # разнообразие действий
                len(user_data),  # общая активность
                user_data['Resource'].nunique(),  # разнообразие ресурсов
            ]
            
            user_features.append(features)
            user_names.append(user)
        
        return np.array(user_features), user_names
    
    def generate_profiles(self, df):
        """
        Генерирует типовые профили на основе кластеризации
        
        Args:
            df: DataFrame с данными
            
        Returns:
            profiles: словарь с типовыми профилями
        """
        features, user_names = self.extract_features(df)
        
        if len(features) < self.n_clusters:
            logger.warning("Недостаточно данных для кластеризации")
            return {}
        
        # Нормализация признаков
        features_scaled = self.scaler.fit_transform(features)
        
        # Кластеризация
        self.cluster_labels = self.kmeans.fit_predict(features_scaled)
        
        # Формируем профили по кластерам
        profiles = {}
        for cluster_id in range(self.n_clusters):
            cluster_users = [user_names[i] for i in range(len(user_names)) 
                           if self.cluster_labels[i] == cluster_id]
            
            if not cluster_users:
                continue
            
            cluster_data = df[df['User_ID'].isin(cluster_users)]
            
            # Определяем типовые характеристики кластера
            profiles[f'Role_{cluster_id+1}'] = {
                'users': cluster_users,
                'size': len(cluster_users),
                'avg_hour': float(cluster_data['Hour'].mean()),
                'avg_data_size': float(cluster_data['Data_Size_KB'].mean()) if 'Data_Size_KB' in cluster_data else 0,
                'typical_hours': self._get_hour_range(cluster_data),
                'typical_events': cluster_data['Event_Type'].value_counts().head(3).index.tolist(),
                'typical_resources': cluster_data['Resource'].value_counts().head(5).index.tolist(),
                'ip_diversity': len(cluster_data['IP_Address'].unique()),
                'total_events': len(cluster_data),
            }
            
            # Пытаемся определить реальную роль по пользователям
            roles_in_cluster = cluster_data['User_Role'].value_counts()
            if not roles_in_cluster.empty:
                profiles[f'Role_{cluster_id+1}']['suggested_role'] = roles_in_cluster.index[0]
        
        self.profiles = profiles
        logger.info(f"Сгенерировано {len(profiles)} типовых профилей")
        return profiles
    
    def _get_hour_range(self, data):
        """Определяет типичный диапазон рабочего времени"""
        hours = data['Hour'].value_counts().sort_index()
        if len(hours) < 2:
            return "Unknown"
        
        # Берем часы с наибольшей активностью
        peak_hours = hours[hours > hours.quantile(0.7)].index.tolist()
        if peak_hours:
            return f"{min(peak_hours)}-{max(peak_hours)}"
        return "Unknown"
    
    def suggest_role(self, user_data, threshold=0.7):
        """
        Определяет, к какому типовому профилю относится пользователь
        
        Args:
            user_data: данные конкретного пользователя
            threshold: порог уверенности
            
        Returns:
            suggested_role: предполагаемая роль
            confidence: уверенность (0-1)
        """
        if not self.profiles:
            return None, 0
        
        # Извлекаем признаки пользователя
        features = np.array([[
            user_data['Hour'].mean(),
            user_data['Hour'].std(),
            user_data['Data_Size_KB'].mean() if 'Data_Size_KB' in user_data else 0,
            user_data['Data_Size_KB'].std() if 'Data_Size_KB' in user_data else 0,
            len(user_data['IP_Address'].unique()),
            user_data['Event_Type'].nunique(),
            len(user_data),
            user_data['Resource'].nunique(),
        ]])
        
        # Нормализуем
        features_scaled = self.scaler.transform(features)
        
        # Предсказываем кластер
        cluster = self.kmeans.predict(features_scaled)[0]
        
        # Определяем уверенность (расстояние до центроида)
        distances = self.kmeans.transform(features_scaled)[0]
        confidence = 1 - (distances[cluster] / distances.sum())
        
        role_key = f'Role_{cluster+1}'
        if role_key in self.profiles and confidence >= threshold:
            return self.profiles[role_key].get('suggested_role', role_key), confidence
        
        return None, confidence
    
    def get_profile_statistics(self):
        """Возвращает статистику по профилям"""
        stats = {
            'total_profiles': len(self.profiles),
            'users_covered': sum(p['size'] for p in self.profiles.values()),
            'profiles': self.profiles
        }
        return stats
