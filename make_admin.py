import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('lastbooking.db')
cursor = conn.cursor()

# Обновляем права пользователя
cursor.execute('''
    UPDATE users 
    SET is_admin = 1
    WHERE username = ?
''', ('admin',))

# Сохраняем изменения
conn.commit()

# Проверяем, были ли внесены изменения
if cursor.rowcount > 0:
    print("Права пользователя обновлены. Теперь admin имеет права администратора.")
else:
    print("Не удалось обновить права пользователя или пользователь уже является администратором.")

# Проверяем статус пользователя
cursor.execute('SELECT id, username, email, is_admin FROM users WHERE username = ?', ('admin',))
user = cursor.fetchone()
if user:
    print(f"Пользователь: ID={user[0]}, Username={user[1]}, Email={user[2]}, Is Admin={user[3]}")
else:
    print("Пользователь admin не найден в базе данных")

# Закрываем соединение
conn.close() 