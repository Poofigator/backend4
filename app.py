from flask import Flask, request, jsonify, render_template
import sqlite3
from threading import Lock

app = Flask(__name__) # Создаем экземпляр приложения Flask

# Подключение БД
db_path = 'applications.db'
db_lock = Lock()
# Функция для получения подключения к базе данных
def get_db_connection():
    with db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        return conn, cursor

@app.route('/') # Декоратор для маршрута главной страницы
def index():
    return render_template('index.html') # Возвращаем HTML-шаблон формы

@app.route('/submit', methods=['POST']) # Декоратор для маршрута отправки формы/сообщения
def submit_application(): # Получаем данные из формы
    conn, cursor = get_db_connection() 
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    attachment = request.files.getlist('attachment')[0] # Получить вложение
    # Сохраняем заявку в базу данных
    cursor.execute("""
    INSERT INTO applications (name, email, message, attachment_filename) VALUES (?, ?, ?, ?);""",
    (name, email, message, attachment.filename))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    # Создание таблицы "applications" (если она не существует)
    conn, cursor = get_db_connection()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    attachment_filename TEXT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    app.run(debug=True, host='0.0.0.0', port=81) # Запуск сервера на порту 81 с отладкой
