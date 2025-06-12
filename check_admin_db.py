import sqlite3
import os

# Проверка существования файла базы данных
db_path = 'lastbooking.db'
if not os.path.exists(db_path):
    print(f"Файл базы данных {db_path} не найден!")
    exit(1)

# Подключение к базе данных
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Проверка структуры таблицы users
try:
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Структура таблицы users:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
except Exception as e:
    print(f"Ошибка при проверке структуры таблицы: {e}")

# Проверка наличия пользователя admin
try:
    cursor.execute("SELECT id, username, email, is_admin, is_active FROM users WHERE username = ?", ('admin',))
    user = cursor.fetchone()
    
    if user:
        print(f"\nПользователь admin найден:")
        print(f"  ID: {user[0]}")
        print(f"  Username: {user[1]}")
        print(f"  Email: {user[2]}")
        print(f"  Is Admin: {user[3]}")
        print(f"  Is Active: {user[4]}")
    else:
        print("\nПользователь admin НЕ найден в базе данных!")
except Exception as e:
    print(f"Ошибка при поиске пользователя: {e}")

# Проверка всех пользователей
try:
    cursor.execute("SELECT id, username, email, is_admin, is_active FROM users")
    users = cursor.fetchall()
    
    print(f"\nВсего пользователей в базе: {len(users)}")
    for user in users:
        print(f"  {user[0]}: {user[1]} ({user[2]}) - Admin: {user[3]}, Active: {user[4]}")
except Exception as e:
    print(f"Ошибка при получении списка пользователей: {e}")

# Закрываем соединение
conn.close() 