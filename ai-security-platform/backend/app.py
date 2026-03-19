"""
Flask web application for Anomaly Detection System
Author: Evgeniia Vorobeva
Part of Bachelor's Thesis
"""

from flask import Flask, request, jsonify, render_template, send_file
# Absolute import for production (works with gunicorn)
from backend.anomaly_detector import AnomalyDetector
import pandas as pd
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import sqlite3

# Fix Python path for production
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Глобальный детектор (для простоты)
detector = AnomalyDetector()
current_results = None

# Function to add notifications to the database
def add_notification(level, user_id, message, details="", sequence=0):
    conn = sqlite3.connect('data/feedback.db')
    cursor = conn.cursor()
    
    # Generate timestamp with milliseconds for precise ordering
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Keep 3 decimal places for milliseconds
    
    # Insert new notification
    cursor.execute('''
        INSERT INTO notifications (timestamp, level, user_id, message, details, sequence)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, level, user_id, message, details, sequence))
    
    # Keep only last 100 notifications (delete oldest)
    # This prevents the database from growing infinitely
    cursor.execute('''
        DELETE FROM notifications 
        WHERE id NOT IN (
            SELECT id FROM notifications 
            ORDER BY sequence DESC, timestamp DESC, id DESC 
            LIMIT 100
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize notifications table
def init_notifications_table():
    conn = sqlite3.connect('data/feedback.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            level TEXT,
            user_id TEXT,
            message TEXT,
            details TEXT
        )
    ''')
    
    # Add sequence column if it doesn't exist
    try:
        cursor.execute('ALTER TABLE notifications ADD COLUMN sequence INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists - ignore
        pass
    
    conn.commit()
    conn.close()

# Call it when app starts
init_notifications_table()

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
        
# Add notifications for anomalies
        anomalies_df = results[results['is_anomaly'] == True]
        for _, row in anomalies_df.iterrows():
            level = row['severity']
            user = row['user_id']
            anom_types = row['anomaly_types']
            details = f"IP: {row['ip_address']}"
            add_notification(level, user, f"Anomaly: {anom_types}", details)
        
        # Add system notification
        add_notification('info', None, f"Analysis complete", 
                        f"{len(results)} events, {len(anomalies_df)} anomalies")

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
    for _, row in current_results.head(50).iterrows():
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
    
    ## Цвета для строк с данными
    for i, row in enumerate(table_data):
        if i == 0:  # пропускаем заголовок
            continue
        severity_value = row[4]  # столбец Severity
        if severity_value == 'high':
            bg_color = colors.HexColor('#ffebee')
        elif severity_value == 'medium':
            bg_color = colors.HexColor('#fff3e0')
        elif severity_value == 'normal':
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
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='anomaly_report.pdf', mimetype='application/pdf')

@app.route('/notifications')
def get_notifications():
    """Get recent notifications with proper ordering"""
    conn = sqlite3.connect('data/feedback.db')
    cursor = conn.cursor()
    # Order by: sequence first (groups attacks), then timestamp (milliseconds precision), then id (final tie-breaker)
    cursor.execute('''
        SELECT timestamp, level, user_id, message, details, sequence
        FROM notifications 
        ORDER BY sequence DESC, timestamp DESC, id DESC
        LIMIT 50
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    notifications = []
    for row in rows:
        notifications.append({
            'timestamp': row[0],
            'level': row[1],
            'user_id': row[2],
            'message': row[3],
            'details': row[4],
            'sequence': row[5]  # Include sequence in response for client-side sorting
        })
    
    return jsonify(notifications)

@app.route('/add_notification', methods=['POST'])
def add_notification_route():
    """Add a notification from the frontend with sequence"""
    data = request.json
    add_notification(
        data['level'], 
        data['user_id'], 
        data['message'], 
        data['details'],
        data.get('sequence', 0)  # Get sequence from request, default 0 if not present
    )
    return jsonify({'status': 'ok'})

@app.route('/generate_details', methods=['POST'])
def generate_details():
    """Generate anomaly details using the detector's logic"""
    data = request.json
    details = detector.generate_anomaly_details(
        data['anomaly_type'],
        data['user'],
        data['ip'],
        data['size']
    )
    return jsonify({'details': details})

@app.route('/clear_notifications', methods=['POST'])
def clear_notifications():
    conn = sqlite3.connect('data/feedback.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notifications')
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/update_results', methods=['POST'])
def update_results():
    """Update current_results from frontend"""
    global current_results
    data = request.json
    current_results = pd.DataFrame(data['results'])
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
