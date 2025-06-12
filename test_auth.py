import requests
import json

# URL API для получения токена
url = "http://127.0.0.1:8000/api/auth/token"

# Данные для входа
login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    # Отправляем запрос на получение токена
    response = requests.post(
        url, 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Записываем результаты в файл
    with open("auth_test_results.txt", "w") as f:
        f.write(f"Статус ответа: {response.status_code}\n")
        f.write(f"Заголовки ответа: {json.dumps(dict(response.headers), indent=2)}\n")
        
        if response.status_code == 200:
            f.write("\nУспешная аутентификация!\n")
            f.write(f"Ответ: {json.dumps(response.json(), indent=2)}\n")
        else:
            f.write("\nОшибка аутентификации!\n")
            f.write(f"Ответ: {response.text}\n")
    
    print(f"Результаты теста аутентификации записаны в файл auth_test_results.txt")
    
except Exception as e:
    print(f"Произошла ошибка: {e}")
    with open("auth_test_results.txt", "w") as f:
        f.write(f"Произошла ошибка: {e}\n") 