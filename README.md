# 🚀 LastBooking API Backend

**FastAPI backend для Flutter приложения бронирования отелей**

Это серверная часть приложения bookingFlutter, предоставляющая REST API для мобильного Flutter приложения `booking`. Backend построен на FastAPI и обеспечивает полный функционал для поиска отелей, системы бронирования и управления пользователями.

## 🔗 Связанные проекты

- **Frontend**: `lastbooking` - Flutter мобильное приложение (ОБЯЗАТЕЛЬНО для полного функционала)

## ⚡ Основные возможности

- 🔐 **JWT аутентификация** с регистрацией и авторизацией
- 🏨 **Управление отелями** с интеграцией Google Places API
- 📅 **Система бронирования** с проверкой доступности
- ⭐ **Избранное** для сохранения понравившихся мест
- 👤 **Профили пользователей** с возможностью редактирования
- 🌍 **Поиск по локации** с радиусом и фильтрами
- 🌤️ **Погодная информация** для выбранных городов
- 🍽️ **Поддержка ресторанов** (дополнительный функционал)
- 👨‍💼 **Административная панель** для управления системой

## 🏗️ Архитектура

```
back/
├── main.py                 # Главное приложение FastAPI
├── database.py            # Настройки базы данных
├── models.py              # SQLAlchemy модели
├── schemas.py             # Pydantic схемы для API
├── security.py            # JWT аутентификация
├── google_places.py       # Интеграция с Google Places API
├── routers/               # API маршруты
│   ├── auth.py           # Аутентификация
│   ├── hotels.py         # Управление отелями
│   ├── bookings.py       # Бронирования
│   ├── users.py          # Пользователи
│   ├── favorites.py      # Избранное
│   ├── restaurants.py    # Рестораны
│   └── weather.py        # Погода
├── lastbooking.db        # SQLite база данных
└── admin scripts/        # Скрипты управления админами
```

## 🛠️ Технологический стек

- **FastAPI** 0.110.0 - современный веб-фреймворк для API
- **SQLAlchemy** 2.0.28 - ORM для работы с базой данных
- **SQLite** - легковесная база данных для разработки
- **Pydantic** 2.6.3 - валидация данных и сериализация
- **JWT** - безопасная аутентификация
- **bcrypt** - хеширование паролей
- **HTTPX** - асинхронные HTTP запросы
- **Uvicorn** - ASGI сервер для production

## 📋 API Endpoints

### 🔐 Аутентификация
- `POST /api/register` - Регистрация нового пользователя
- `POST /api/login` - Вход в систему
- `POST /api/refresh` - Обновление токена

### 🏨 Отели
- `GET /api/hotels/search` - Поиск отелей по параметрам
- `GET /api/hotels/{hotel_id}` - Получение деталей отеля
- `GET /api/hotels/details/{place_id}` - Детали отеля по Place ID
- `POST /api/hotels` - Создание отеля (админ)
- `PUT /api/hotels/{hotel_id}` - Обновление отеля (админ)
- `DELETE /api/hotels/{hotel_id}` - Удаление отеля (админ)

### 📅 Бронирования
- `GET /api/bookings` - Список бронирований пользователя
- `POST /api/bookings` - Создание нового бронирования
- `GET /api/bookings/{booking_id}` - Детали бронирования
- `PUT /api/bookings/{booking_id}` - Изменение бронирования
- `DELETE /api/bookings/{booking_id}` - Отмена бронирования

### ⭐ Избранное
- `GET /favorites` - Список избранных отелей
- `POST /favorites` - Добавление в избранное
- `DELETE /favorites/{hotel_id}` - Удаление из избранного

### 👤 Пользователи
- `GET /api/users/me` - Профиль текущего пользователя
- `PUT /api/users/me` - Обновление профиля
- `GET /api/users/{user_id}` - Профиль пользователя (админ)

### 🍽️ Рестораны
- `GET /api/restaurants/search` - Поиск ресторанов
- `GET /api/restaurants/details/{place_id}` - Детали ресторана

## ⚙️ Установка и запуск

### Предварительные требования

- **Python** 3.8+ 
- **pip** или **poetry** для управления зависимостями
- **Google Places API ключ** (необходим для поиска отелей)

### Быстрый старт

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd back
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
Создайте файл `.env` в корне проекта:
```env
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_PLACES_API_KEY=your-google-places-api-key
WEATHER_API_KEY=your-weather-api-key
DATABASE_URL=sqlite:///./lastbooking.db
```

5. **Запустите сервер разработки:**
```bash
python main.py
```

Или используйте uvicorn напрямую:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

🎉 **API будет доступно по адресу**: http://localhost:8000

📚 **Интерактивная документация**: http://localhost:8000/docs

## 🔧 Конфигурация

### База данных
По умолчанию используется SQLite для простоты разработки. База данных создается автоматически при первом запуске.

### Google Places API
Для работы поиска отелей необходим API ключ Google Places:
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект или выберите существующий
3. Включите Places API
4. Создайте API ключ
5. Добавьте ключ в `.env` файл

### Администраторы
Для создания администратора используйте один из скриптов:
```bash
python create_admin_simple.py
```

## 🚀 Развертывание

### Production с Docker
```bash
# Создайте Dockerfile (пример)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Heroku
```bash
# Создайте Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Переменные окружения для production
```env
SECRET_KEY=very-secure-production-key
DATABASE_URL=postgresql://user:password@host:port/database
GOOGLE_PLACES_API_KEY=production-api-key
CORS_ORIGINS=https://yourdomain.com,https://yourapp.com
```

## 🔒 Безопасность

- **JWT токены** для аутентификации
- **bcrypt** хеширование паролей
- **CORS** настройки для фронтенда
- **Валидация данных** через Pydantic
- **SQL injection** защита через SQLAlchemy ORM

## 🧪 Тестирование

Запуск тестов аутентификации:
```bash
python test_auth.py
```

### Примеры использования API

**Регистрация пользователя:**
```bash
curl -X POST "http://localhost:8000/api/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "secure_password",
       "full_name": "John Doe"
     }'
```

**Поиск отелей:**
```bash
curl -X GET "http://localhost:8000/api/hotels/search?location=Moscow&radius=5000" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Создание бронирования:**
```bash
curl -X POST "http://localhost:8000/api/bookings" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "hotel_id": 1,
       "check_in": "2024-07-01",
       "check_out": "2024-07-05",
       "guests": 2
     }'
```

## 📊 Мониторинг

API предоставляет эндпоинты для мониторинга:
- `GET /` - Проверка работоспособности
- `GET /docs` - Swagger документация
- `GET /redoc` - ReDoc документация

## 🤝 Интеграция с Flutter

Этот backend специально разработан для работы с Flutter приложением `lastbooking`. 

**Важные моменты интеграции:**
- CORS настроен для работы с мобильными приложениями
- JWT токены совместимы с Flutter Secure Storage
- JSON API полностью совместимо с Dart/Flutter HTTP клиентами
- Обработка ошибок следует стандартам HTTP

## 📝 Разработка

### Добавление новых эндпоинтов
1. Создайте новую модель в `models.py`
2. Добавьте схемы в `schemas.py`
3. Создайте роутер в `routers/`
4. Подключите роутер в `main.py`

### Структура ответов API
```json
{
  "success": true,
  "data": {},
  "message": "Успех",
  "errors": null
}
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь, что все переменные окружения настроены
3. Проверьте подключение к базе данных
4. Убедитесь, что Google Places API ключ активен

---

**⚠️ Важно**: Этот backend разработан для работы в паре с Flutter приложением `lastbooking`. Для полного функционала убедитесь, что оба проекта настроены и запущены.

🚀 **Готово к работе!** Ваш LastBooking API backend готов обслуживать мобильное приложение.
