import logging
import requests  # Для HTTP-запитів до app1
import time
import os
from datetime import datetime
from flask import Flask  # Можна використовувати Flask для HTTP-запитів

def create_alert(error_type, message):
    # Створюємо папку для алертів, якщо її немає
    if not os.path.exists('error_reports'):
        os.makedirs('error_reports')
    
    # Генеруємо ім'я файлу з поточною датою та часом
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"error_reports/alert_{timestamp}.txt"
    
    # Записуємо звіт про помилку
    with open(filename, 'w') as f:
        f.write(f"Time: {datetime.now()}\n")
        f.write(f"Type: {error_type}\n")
        f.write(f"Description: {message}\n")
app = Flask(__name__)

# Налаштування логування (аналогічно до app1)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/app.log'
)

@app.route('/receive_message')
def receive_message():
    response = requests.get('http://localhost:5000/send_message')  # Працює локально    logging.info(f"Received message: {response.text}")  # Логуємо відповідь
    return response.text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)