import sqlite3
import os

# Файл для записи результатов
output_file = 'admin_check_results.txt'

with open(output_file, 'w') as f:
    # Проверка существования файла базы данных
    db_path = 'lastbooking.db'
    if not os.path.exists(db_path):
        f.write(f"Файл базы данных {db_path} не найден!\n")
        exit(1)
    else:
        f.write(f"Файл базы данных {db_path} найден.\n")

    try:
        # Подключение к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверка структуры таблицы users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        f.write("\nСтруктура таблицы users:\n")
        for col in columns:
            f.write(f"  {col[1]} ({col[2]})\n")
        
        # Проверка наличия пользователя admin
        cursor.execute("SELECT id, username, email, is_admin, is_active, hashed_password FROM users WHERE username = ?", ('admin',))
        user = cursor.fetchone()
        
        if user:
            f.write(f"\nПользователь admin найден:\n")
            f.write(f"  ID: {user[0]}\n")
            f.write(f"  Username: {user[1]}\n")
            f.write(f"  Email: {user[2]}\n")
            f.write(f"  Is Admin: {user[3]}\n")
            f.write(f"  Is Active: {user[4]}\n")
            f.write(f"  Password Hash: {user[5][:20]}...\n")
        else:
            f.write("\nПользователь admin НЕ найден в базе данных!\n")
        
        # Проверка всех пользователей
        cursor.execute("SELECT id, username, email, is_admin, is_active FROM users")
        users = cursor.fetchall()
        
        f.write(f"\nВсего пользователей в базе: {len(users)}\n")
        for user in users:
            f.write(f"  {user[0]}: {user[1]} ({user[2]}) - Admin: {user[3]}, Active: {user[4]}\n")
        
        # Закрываем соединение
        conn.close()
        
    except Exception as e:
        f.write(f"\nОшибка при работе с базой данных: {e}\n")

print(f"Результаты проверки записаны в файл {output_file}") 