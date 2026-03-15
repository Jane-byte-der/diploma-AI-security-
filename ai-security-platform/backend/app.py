"""
Flask web application for Anomaly Detection System
Author: Evgeniia Vorobeva
Part of Bachelor's Thesis
"""

from flask import Flask, request, jsonify, render_template, send_file
from .anomaly_detector import AnomalyDetector
import pandas as pd
import os
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
from collections import Counter
import io
import os

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Глобальный детектор (для простоты)
detector = AnomalyDetector()
current_results = None

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Загрузка и анализ файла"""
    global current_results
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не загружен'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        # Сохраняем временно
        temp_path = f"/tmp/{datetime.now().timestamp()}.csv"
        file.save(temp_path)
        
        # Загружаем данные
        df = detector.load_data(temp_path)
        
        # Строим профили
        profiles = detector.build_profiles(df)
        
        # Обнаруживаем аномалии
        results = detector.detect_anomalies(df)
        current_results = results
        
        # Получаем статистику
        stats = detector.get_statistics(results)
        
        # Матрица ошибок (если есть ground truth)
        confusion = {}
        if 'Is_Anomaly' in df.columns:
            confusion = detector.get_confusion_matrix(results)
        
        # Очищаем временный файл
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'confusion_matrix': confusion,
            'results': results.head(20).to_dict('records'),  # первые 20 для预览
            'total_results': len(results),
            'profiles': profiles
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_results')
def get_results():
    """Получить полные результаты"""
    global current_results
    if current_results is not None:
        return jsonify(current_results.to_dict('records'))
    return jsonify({'error': 'Нет результатов'}), 404

@app.route('/download_results')
def download_results():
    """Скачать результаты как CSV"""
    global current_results
    if current_results is not None:
        path = f"/tmp/results_{datetime.now().timestamp()}.csv"
        current_results.to_csv(path, index=False)
        return send_file(path, as_attachment=True, download_name='anomaly_results.csv')
    return jsonify({'error': 'Нет результатов'}), 404

@app.route('/api/stats')
def get_stats():
    """Получить только статистику"""
    global current_results
    if current_results is not None:
        return jsonify(detector.get_statistics(current_results))
    return jsonify({'error': 'Нет результатов'}), 404

@app.route('/health')
def health():
    """Проверка работоспособности"""
    return jsonify({'status': 'ok', 'message': 'Anomaly Detector is running'})

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io

@app.route('/download_pdf')
def download_pdf():
    global current_results
    if current_results is None:
        return jsonify({'error': 'No results to export'}), 404
    
    # Создаём PDF в памяти
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Заголовок
    story.append(Paragraph("Anomaly Detection Report", styles['Title']))
    story.append(Spacer(1, 0.2*inch))
    
    # Статистика
    stats = current_results['is_anomaly'].value_counts()
    story.append(Paragraph(f"Total events: {len(current_results)}", styles['Normal']))
    story.append(Paragraph(f"Anomalies detected: {stats.get(True, 0)}", styles['Normal']))
    story.append(Paragraph(f"Normal events: {stats.get(False, 0)}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Таблица
    table_data = [['Timestamp', 'User', 'Event', 'Anomaly Types', 'Severity']]
    for _, row in current_results.head(20).iterrows():
        table_data.append([
            row['timestamp'],
            row['user_id'],
            row['event_type'],
            row['anomaly_types'],
            row['severity']
        ])
    
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='anomaly_report.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
