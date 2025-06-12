import requests
import json

# URL API для регистрации
url = "http://127.0.0.1:8000/api/auth/register"

# Данные для регистрации администратора
admin_data = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Administrator",
    "phone": None
}

try:
    # Отправляем запрос на регистрацию
    response = requests.post(url, json=admin_data)
    
    # Проверяем статус ответа
    if response.status_code == 200:
        print("Администратор успешно зарегистрирован!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Ошибка при регистрации: {response.status_code}")
        print(response.text)
        
        # Если пользователь уже существует, попробуем обновить его права через базу данных
        if response.status_code == 400 and "уже существует" in response.text:
            print("Пользователь уже существует. Попытка обновить права...")
            
            import sqlite3
            conn = sqlite3.connect('lastbooking.db')
            cursor = conn.cursor()
            
            # Обновляем права пользователя
            cursor.execute('''
                UPDATE users 
                SET is_admin = 1, is_active = 1
                WHERE username = ?
            ''', ('admin',))
            
            # Проверяем, были ли внесены изменения
            if cursor.rowcount > 0:
                print("Права пользователя обновлены. Теперь admin имеет права администратора.")
            else:
                print("Не удалось обновить права пользователя.")
            
            conn.commit()
            conn.close()
except Exception as e:
    print(f"Произошла ошибка: {e}")

print("\nДля входа используйте:")
print("Логин: admin")
print("Пароль: admin123") 