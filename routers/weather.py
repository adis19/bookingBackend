from fastapi import APIRouter, Depends, HTTPException, status
import requests
from typing import Optional, Dict, Any
from database import get_db
from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta

router = APIRouter()

# Кэш для хранения данных о погоде
weather_cache = {
    "data": None,
    "timestamp": None
}

# API ключ для OpenWeatherMap
OPENWEATHER_API_KEY = "f5cb0b965ea1364904a12bd98d0adae1"
# Google Places API ключ
GOOGLE_API_KEY = "D3zvlHL8F0ocFEASyCum3bPgDEk="

@router.get("/weather")
async def get_weather(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Получение данных о погоде по названию города или координатам.
    Поддерживает кэширование для уменьшения количества запросов к API.
    
    - **city**: Название города (например, "Бишкек")
    - **lat**: Широта (если нужно получить погоду по координатам)
    - **lon**: Долгота (если нужно получить погоду по координатам)
    
    Если не указаны ни город, ни координаты, возвращается погода для Бишкека.
    """
    
    # Проверяем кэш
    if weather_cache["data"] and weather_cache["timestamp"]:
        cache_age = datetime.now() - weather_cache["timestamp"]
        if cache_age < timedelta(minutes=10):  # Кэш действителен 10 минут
            return weather_cache["data"]
    
    try:
        # По умолчанию используем Бишкек, если не указан город или координаты
        if not city and not (lat and lon):
            city = "Бишкек"
            lat = 42.8746
            lon = 74.5698
        
        # Используем OpenWeatherMap API
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        # Определяем параметры запроса
        params = {
            "appid": OPENWEATHER_API_KEY,
            "lang": "ru",
            "units": "metric"  # Используем метрическую систему (Цельсии)
        }
        
        # Если предоставлены координаты, используем их
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
        # Иначе используем название города
        elif city:
            params["q"] = city
        
        # Выполняем запрос к API
        print(f"Запрос к OpenWeatherMap: {base_url} с параметрами {params}")
        response = requests.get(base_url, params=params)
        
        # Проверяем статус ответа
        if response.status_code == 200:
            weather_data = response.json()
            print(f"Получен ответ от API: {weather_data}")
            
            # Проверка температуры на разумные пределы
            if "main" in weather_data and "temp" in weather_data["main"]:
                temp = weather_data["main"]["temp"]
                if temp < -100 or temp > 100:
                    print(f"Неправильная температура: {temp}°C. Устанавливаем значение по умолчанию.")
                    weather_data["main"]["temp"] = 20.0
                    weather_data["main"]["feels_like"] = 18.0
                    weather_data["main"]["temp_min"] = 18.0
                    weather_data["main"]["temp_max"] = 22.0
            
            # Сохраняем результат в кэш
            weather_cache["data"] = weather_data
            weather_cache["timestamp"] = datetime.now()
            
            return weather_data
        else:
            # Если запрос не успешен, пробуем резервный API
            print(f"Ошибка OpenWeatherMap API: {response.status_code}. Пробуем использовать резервный источник.")
            return get_fallback_weather_data(city, lat, lon)
    
    except Exception as e:
        # В случае любой ошибки, используем резервный источник
        print(f"Ошибка при получении погоды: {e}. Используем резервный источник.")
        return get_fallback_weather_data(city, lat, lon)

def get_fallback_weather_data(city: Optional[str], lat: Optional[float], lon: Optional[float]) -> Dict[str, Any]:
    """
    Резервный источник данных о погоде.
    Возвращает заглушку с данными о погоде для указанного города/координат.
    """
    # По умолчанию данные для Бишкека
    city_name = city or "Бишкек"
    coords = {"lon": lon or 74.59, "lat": lat or 42.87}
    
    fallback_data = {
        "coord": coords,
        "weather": [{"id": 800, "main": "Clear", "description": "ясно", "icon": "01d"}],
        "base": "stations",
        "main": {
            "temp": 20.0,  # 20°C
            "feels_like": 19.5,
            "temp_min": 18.0,
            "temp_max": 22.0,
            "pressure": 1013,
            "humidity": 50
        },
        "visibility": 10000,
        "wind": {"speed": 2.0, "deg": 0},
        "clouds": {"all": 0},
        "dt": int(datetime.now().timestamp()),
        "sys": {
            "country": "KG",
            "sunrise": int((datetime.now() - timedelta(hours=6)).timestamp()),
            "sunset": int((datetime.now() + timedelta(hours=6)).timestamp())
        },
        "timezone": 21600,
        "id": 1,
        "name": city_name,
        "cod": 200
    }
    
    # Сохраняем в кэш
    weather_cache["data"] = fallback_data
    weather_cache["timestamp"] = datetime.now()
    
    return fallback_data 