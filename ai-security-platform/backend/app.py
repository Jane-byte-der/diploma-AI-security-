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

def save_charts_to_image():
    """Сохраняет текущие графики во временный файл и возвращает путь"""
    if current_results is None:
        return None
    
    img_path = f"/tmp/charts_{datetime.now().timestamp()}.png"
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#f5f5f5')
    
    # 1. Столбчатая диаграмма по пользователям
    user_counts = current_results['user_id'].value_counts()
    bars = ax1.bar(user_counts.index, user_counts.values, color='#3498db', edgecolor='white', linewidth=1)
    ax1.set_title('Events by User', fontsize=14, fontweight='bold', color='#2c3e50')
    ax1.set_ylabel('Number of events', fontsize=11, color='#333')
    ax1.tick_params(axis='x', rotation=45, colors='#333')
    ax1.tick_params(axis='y', colors='#333')
    ax1.set_facecolor('#ffffff')
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 2. Круговая диаграмма по типам аномалий
    all_types = []
    for types in current_results['anomaly_types']:
        if types != 'none':
            all_types.extend([t.strip() for t in types.split(',')])
    
    if all_types:
        type_counts = Counter(all_types)
        
        color_map = {
            'temporal': '#ff6b6b',
            'spatial': '#f39c12',
            'intensity': '#3498db',
            'resource': '#2ecc71',
            'behavioral': '#9b59b6'
        }
        
        colors_list = [color_map.get(t, '#95a5a6') for t in type_counts.keys()]
        
        wedges, texts, autotexts = ax2.pie(
            type_counts.values(),
            labels=type_counts.keys(),
            autopct='%1.1f%%',
            colors=colors_list,
            textprops={'fontsize': 10, 'fontweight': 'bold', 'color': '#2c3e50'},
            pctdistance=0.85
        )
        ax2.set_title('Anomaly Types', fontsize=14, fontweight='bold', color='#2c3e50')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    else:
        ax2.text(0.5, 0.5, 'No anomalies', ha='center', va='center', fontsize=14, color='#666')
        ax2.set_title('Anomaly Types', fontsize=14, fontweight='bold', color='#2c3e50')
    
    plt.tight_layout()
    plt.savefig(img_path, dpi=120, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    
    return img_path

@app.route('/download_pdf')
def download_pdf():
    global current_results
    if current_results is None:
        return jsonify({'error': 'No results to export'}), 404
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Заголовок
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20
    )
    story.append(Paragraph("Anomaly Detection Report", title_style))
    
    # Статистика
    stats_style = ParagraphStyle(
        'Stats',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#333'),
        spaceAfter=6
    )
    
    total = len(current_results)
    anomalies = len(current_results[current_results['is_anomaly'] == True])
    normal = total - anomalies
    
    story.append(Paragraph(f"Total events: {total}", stats_style))
    story.append(Paragraph(f"Anomalies detected: {anomalies}", stats_style))
    story.append(Paragraph(f"Normal events: {normal}", stats_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Таблица
    table_data = [['Timestamp', 'User', 'Event', 'Anomaly Types', 'Severity']]
    for _, row in current_results.head(20).iterrows():
        severity = row['severity']
        severity_display = severity
            
        table_data.append([
            row['timestamp'],
            row['user_id'],
            row['event_type'],
            row['anomaly_types'],
            severity_display
        ])
    
    table = Table(table_data)
    
    # Сначала стиль для заголовка
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ]))
    
    # Цвета для строк с данными
    for i, row in enumerate(table_data):
        if i == 0:  # пропускаем заголовок
            continue
        severity = row[4]  # столбец Severity
        if '🔴' in severity:
            bg_color = colors.HexColor('#ffebee')
        elif '🟡' in severity:
            bg_color = colors.HexColor('#fff3e0')
        elif '🟢' in severity:
            bg_color = colors.HexColor('#e8f5e9')
        else:
            bg_color = colors.white
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,i), (-1,i), bg_color)
        ]))
    
    # Сетка
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    story.append(table)
    
    # # Графики
    # img_path = save_charts_to_image()
    # if img_path and os.path.exists(img_path):
    #     story.append(Spacer(1, 0.3*inch))
    #     story.append(Paragraph("📈 Analytics Charts", styles['Heading2']))
    #     story.append(Spacer(1, 0.1*inch))
    #     img = Image(img_path, width=6*inch, height=2.5*inch)
    #     story.append(img)
    #     try:
    #         os.remove(img_path)
    #     except:
    #         pass
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='anomaly_report.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
