import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('lastbooking.db')
cursor = conn.cursor()

# Проверка, существует ли пользователь admin
cursor.execute('SELECT id, username, email, is_admin, is_active FROM users WHERE username = ?', ('admin',))
user = cursor.fetchone()

if user:
    print(f"Пользователь найден: ID={user[0]}, Username={user[1]}, Email={user[2]}, Is Admin={user[3]}, Is Active={user[4]}")
else:
    print("Пользователь admin не найден в базе данных")

# Закрываем соединение
conn.close() 