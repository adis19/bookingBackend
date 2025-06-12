import sqlite3
import os
from passlib.context import CryptContext

# Инициализация контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для хеширования пароля
def get_password_hash(password):
    return pwd_context.hash(password)

# Данные для администратора
username = "admin"
email = "admin@example.com"
password = "admin123"
hashed_password = get_password_hash(password)

# Подключение к базе данных
conn = sqlite3.connect('lastbooking.db')
cursor = conn.cursor()

try:
    # Проверка существования таблицы users
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        # Создаем таблицу users, если она не существует
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Таблица users создана")
    
    # Проверка наличия пользователя admin
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        # Обновляем существующего пользователя
        cursor.execute('''
            UPDATE users 
            SET hashed_password = ?, is_admin = 1, is_active = 1
            WHERE username = ?
        ''', (hashed_password, username))
        print(f"Пользователь {username} обновлен и теперь является администратором")
    else:
        # Создаем нового пользователя-администратора
        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, is_admin, is_active)
            VALUES (?, ?, ?, 1, 1)
        ''', (username, email, hashed_password))
        print(f"Администратор {username} создан")
    
    # Сохраняем изменения
    conn.commit()
    
    # Проверяем, что пользователь создан
    cursor.execute("SELECT id, username, email, is_admin, is_active FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if user:
        print(f"\nПользователь admin успешно создан/обновлен:")
        print(f"  ID: {user[0]}")
        print(f"  Username: {user[1]}")
        print(f"  Email: {user[2]}")
        print(f"  Is Admin: {user[3]}")
        print(f"  Is Active: {user[4]}")
    
except Exception as e:
    conn.rollback()
    print(f"Ошибка: {e}")
finally:
    conn.close()

print(f"\nГотово! Используйте логин: {username}, пароль: {password}") 