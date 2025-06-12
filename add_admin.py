import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('lastbooking.db')
cursor = conn.cursor()

# Хешированный пароль 'admin123'
hashed_password = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'

# Проверка, существует ли пользователь
cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
user = cursor.fetchone()

if user:
    # Обновляем существующего пользователя
    cursor.execute('''
        UPDATE users 
        SET is_admin = 1, is_active = 1, hashed_password = ?
        WHERE username = ?
    ''', (hashed_password, 'admin'))
    print("Пользователь admin обновлен и теперь является администратором")
else:
    # Создаем нового пользователя-администратора
    cursor.execute('''
        INSERT INTO users (username, email, hashed_password, is_admin, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', 'admin@example.com', hashed_password, 1, 1))
    print("Пользователь admin создан с правами администратора")

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Готово! Используйте логин: admin, пароль: admin123") 