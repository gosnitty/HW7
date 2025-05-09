from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime
from celery import Celery
import time

app = Flask(__name__)

# Налаштування Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Налаштування логів
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/app.log'
)

def create_alert_file(alert_type, description):
    """Створює файл звіту про помилку"""
    if not os.path.exists('error_reports'):
        os.makedirs('error_reports')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"error_reports/alert_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"Time: {datetime.now()}\n")
        f.write(f"Type: {alert_type}\n")
        f.write(f"Description: {description}\n")
    
    logging.error(f"Alert generated: {alert_type} - {description}")

@celery.task(bind=True)
def long_running_task(self, data):
    """Приклад довгої асинхронної задачі"""
    try:
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100})
        
        # Імітація довгої операції
        for i in range(1, 4):
            time.sleep(1)
            self.update_state(state='PROGRESS', meta={'current': i*33, 'total': 100})
        
        # Перевірка на помилки в процесі виконання
        if data == 'error':
            create_alert_file("TASK_ERROR", "Error occurred during task processing")
            raise ValueError("Simulated processing error")
            
        return {'result': f'Processed: {data}', 'status': 'COMPLETED'}
    except Exception as e:
        create_alert_file("TASK_FAILURE", str(e))
        raise

# Існуючі маршрути для логування та алертів
@app.route('/process')
def process_data():
    # Перевірка на некоректний ввід
    if request.args.get('error') == '1':
        create_alert_file(
            "INPUT_ERROR", 
            "Invalid input parameter received"
        )
        return "Error: Invalid input", 400
    
    # Перевірка на спробу шахрайства
    if request.args.get('fraud') == '1':
        create_alert_file(
            "FRAUD_ATTEMPT", 
            "User tried to submit suspicious data"
        )
        return "Fraud attempt detected", 403
    
    # Перевірка на персональні дані
    if request.args.get('data') == 'personal':
        create_alert_file(
            "PERSONAL_DATA", 
            "User attempted to send personal information"
        )
        return "Personal data not allowed", 406

    logging.info("Processing successful request")
    return "OK", 200

# Нові маршрути для Celery
@app.route('/start_task/<data>')
def start_task(data):
    """Запуск асинхронної задачі"""
    task = long_running_task.delay(data)
    return jsonify({'task_id': task.id}), 202

@app.route('/task_status/<task_id>')
def task_status(task_id):
    """Перевірка статусу задачі"""
    task = long_running_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': 'In progress',
            'progress': task.info.get('current', 0),
            'total': task.info.get('total', 100)
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.info.get('result', ''),
            'status': 'Task completed'
        }
    else:
        # Помилка виконання
        response = {
            'state': task.state,
            'status': str(task.info),  # повідомлення про помилку
            'error': True
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)  # Змініть на вільний порт (наприклад 5005)