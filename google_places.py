import httpx
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
import requests

# Загрузка переменных окружения
load_dotenv()

# API ключ из переменных окружения или напрямую (для разработки)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyD7vOGtJpBivX2YTbZC63lBi5XDYmbfM8o")

# Базовые URL для Google Places API
PLACES_API_BASE_URL = "https://maps.googleapis.com/maps/api/place"
PLACE_SEARCH_URL = f"{PLACES_API_BASE_URL}/textsearch/json"
PLACE_DETAILS_URL = f"{PLACES_API_BASE_URL}/details/json"
PLACE_PHOTO_URL = f"{PLACES_API_BASE_URL}/photo"

def search_hotels(
    query: Optional[str] = None,
    location: Optional[str] = None,
    radius: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Поиск отелей с использованием Google Places API
    """
    params = {
        "key": GOOGLE_API_KEY,
        "type": "lodging",  # Тип места - отель
    }
    
    # Добавляем параметры, если они указаны
    if query:
        params["query"] = query
    
    if location and radius:
        params["location"] = location
        params["radius"] = radius
    
    try:
        response = requests.get(PLACE_SEARCH_URL, params=params)
        data = response.json()
        
        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')}, {data.get('error_message', '')}")
            return []
        
        results = data.get("results", [])
        print(f"Found {len(results)} hotels in search results")
        
        # Фильтрация по рейтингу, если указан
        if min_rating is not None:
            results = [r for r in results if r.get("rating", 0) >= min_rating]
            print(f"{len(results)} hotels meet the minimum rating criteria")
            
        # Преобразование результатов в нужный формат
        hotels = []
        for i, place in enumerate(results):
            print(f"Processing hotel {i+1}: {place.get('name')}")
            photos_data = place.get("photos", [])
            print(f"Hotel {i+1} has {len(photos_data)} photos in API response")
            
            # Получаем URL фотографий
            photo_urls = get_place_photos(photos_data)
            print(f"Got {len(photo_urls)} photo URLs for hotel {i+1}")
            
            # Обрабатываем адрес
            address = place.get("formatted_address")
            if address is None:
                # Если formatted_address отсутствует, используем vicinity или имя отеля
                address = place.get("vicinity") or place.get("name", "Unknown Address")
                print(f"Missing formatted_address for hotel {i+1}, using fallback: {address}")
            
            # Обрабатываем название
            name = place.get("name")
            if name is None:
                name = "Unknown Hotel"
                print(f"Missing name for hotel {i+1}, using fallback: {name}")
            
            hotel = {
                "place_id": place.get("place_id", ""),
                "name": name,
                "address": address,
                "vicinity": place.get("vicinity") or address,
                "latitude": place.get("geometry", {}).get("location", {}).get("lat", 0.0),
                "longitude": place.get("geometry", {}).get("location", {}).get("lng", 0.0),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total"),
                "photos": photo_urls,
                "details": {
                    "price_level": place.get("price_level"),
                    "types": place.get("types"),
                    "icon": place.get("icon"),
                    "icon_background_color": place.get("icon_background_color"),
                    "business_status": place.get("business_status"),
                    "plus_code": place.get("plus_code"),
                }
            }
            hotels.append(hotel)
            
        print(f"Returning {len(hotels)} processed hotels")
        return hotels
    except Exception as e:
        print(f"Error searching hotels: {e}")
        return []

def get_hotel_details(place_id: str) -> Optional[Dict[str, Any]]:
    """
    Получение детальной информации об отеле по его place_id
    """
    # Расширенный список полей для запроса
    fields = [
        "name", "formatted_address", "geometry", "rating", "photos", "price_level", 
        "formatted_phone_number", "international_phone_number", "website", "opening_hours", 
        "reviews", "types", "user_ratings_total", "icon", "icon_background_color", "url", 
        "vicinity", "address_components", "adr_address", "business_status", "current_opening_hours",
        "editorial_summary", "plus_code", "utc_offset", "wheelchair_accessible_entrance"
    ]
    
    params = {
        "key": GOOGLE_API_KEY,
        "place_id": place_id,
        "fields": ",".join(fields)
    }
    
    try:
        print(f"Getting details for place_id: {place_id}")
        response = requests.get(PLACE_DETAILS_URL, params=params)
        data = response.json()
        
        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')}, {data.get('error_message', '')}")
            return None
        
        place = data.get("result", {})
        photos_data = place.get("photos", [])
        print(f"Hotel has {len(photos_data)} photos in API response")
        
        # Получаем URL фотографий
        photo_urls = get_place_photos(photos_data)
        print(f"Got {len(photo_urls)} photo URLs for hotel details")
        
        # Обработка отзывов
        reviews = place.get("reviews", [])
        print(f"Hotel has {len(reviews)} reviews in API response")
        
        # Убедимся, что отзывы - это список
        if reviews and not isinstance(reviews, list):
            print(f"Reviews is not a list, but {type(reviews)}")
            reviews = []
        
        # Проверим структуру отзывов
        if reviews:
            print(f"First review structure: {reviews[0].keys() if reviews[0] else 'None'}")
            
            # Проверка на наличие необходимых полей
            for i, review in enumerate(reviews):
                if not isinstance(review, dict):
                    print(f"Review {i} is not a dict, but {type(review)}")
                    continue
                    
                # Проверяем наличие обязательных полей
                required_fields = ["author_name", "rating", "text"]
                for field in required_fields:
                    if field not in review:
                        print(f"Review {i} is missing required field: {field}")
                        review[field] = "N/A" if field != "rating" else 0
        
        # Обрабатываем адрес
        address = place.get("formatted_address")
        if address is None:
            # Если formatted_address отсутствует, используем vicinity или имя отеля
            address = place.get("vicinity") or place.get("name", "Unknown Address")
            print(f"Missing formatted_address for hotel, using fallback: {address}")
        
        # Обрабатываем название
        name = place.get("name")
        if name is None:
            name = "Unknown Hotel"
            print(f"Missing name for hotel, using fallback: {name}")
        
        # Извлекаем текстовое описание из editorial_summary, если оно есть
        editorial_summary = None
        if place.get("editorial_summary") and isinstance(place.get("editorial_summary"), dict):
            editorial_summary = place.get("editorial_summary").get("overview")
        
        # Создаем структуру с детальной информацией
        hotel_details = {
            "place_id": place_id,
            "name": name,
            "address": address,
            "vicinity": place.get("vicinity") or address,
            "latitude": place.get("geometry", {}).get("location", {}).get("lat", 0.0),
            "longitude": place.get("geometry", {}).get("location", {}).get("lng", 0.0),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "photos": photo_urls,
            "details": {
                "price_level": place.get("price_level"),
                "phone": place.get("formatted_phone_number"),
                "international_phone": place.get("international_phone_number"),
                "website": place.get("website"),
                "opening_hours": place.get("opening_hours"),
                "current_opening_hours": place.get("current_opening_hours"),
                "types": place.get("types"),
                "icon": place.get("icon"),
                "icon_background_color": place.get("icon_background_color"),
                "google_maps_url": place.get("url"),
                "business_status": place.get("business_status"),
                "address_components": place.get("address_components"),
                "adr_address": place.get("adr_address"),
                "plus_code": place.get("plus_code"),
                "utc_offset": place.get("utc_offset"),
                "wheelchair_accessible": place.get("wheelchair_accessible_entrance"),
                "editorial_summary": editorial_summary,
                "reviews": reviews
            }
        }
        
        # Проверка структуры результата
        print(f"Hotel details structure: {hotel_details.keys()}")
        print(f"Hotel details['details'] structure: {hotel_details['details'].keys()}")
        print(f"Reviews count in result: {len(hotel_details['details']['reviews'])}")
        
        return hotel_details
    except Exception as e:
        print(f"Error getting hotel details: {e}")
        return None

def get_place_photos(photos: List[Dict[str, Any]], max_photos: int = 5) -> List[str]:
    """
    Получение URL фотографий места
    """
    photo_urls = []
    
    # Если фотографий нет, возвращаем заглушки
    if not photos:
        print("No photos available, returning placeholder")
        return ["https://via.placeholder.com/800x600?text=No+Image+Available"]
    
    # Проверяем, что photos - это список
    if not isinstance(photos, list):
        print(f"Photos is not a list but {type(photos)}")
        return ["https://via.placeholder.com/800x600?text=Invalid+Photos+Format"]
    
    # Ограничиваем количество фотографий
    photos = photos[:max_photos]
    print(f"Processing {len(photos)} photos")
    
    for i, photo in enumerate(photos):
        try:
            if not isinstance(photo, dict):
                print(f"Photo {i} is not a dict but {type(photo)}")
                photo_urls.append(f"https://via.placeholder.com/800x600?text=Invalid+Photo+{i}+Format")
                continue
                
            photo_reference = photo.get("photo_reference")
            if not photo_reference:
                print(f"Photo {i} has no photo_reference")
                photo_urls.append(f"https://via.placeholder.com/800x600?text=No+Reference+Photo+{i}")
                continue
                
            # Создаем URL для фотографии
            photo_url = f"{PLACE_PHOTO_URL}?maxwidth=800&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
            print(f"Photo {i+1}: Getting URL for reference {photo_reference[:10]}...")
            
            # Выполняем запрос для получения прямого URL (через редирект)
            response = requests.get(photo_url, allow_redirects=False)
            print(f"Photo {i+1}: Response status code: {response.status_code}")
            
            if response.status_code == 302 and 'Location' in response.headers:
                direct_url = response.headers['Location']
                print(f"Photo {i+1}: Got direct URL: {direct_url[:50]}...")
                photo_urls.append(direct_url)
            else:
                # Если не удалось получить прямой URL через редирект, используем оригинальный URL
                print(f"Photo {i+1}: No redirect, using original URL")
                photo_urls.append(photo_url)
        except Exception as e:
            print(f"Error getting photo URL for photo {i+1}: {e}")
            # В случае ошибки используем заглушку
            photo_urls.append(f"https://via.placeholder.com/800x600?text=Error+Photo+{i+1}")
    
    # Если не удалось получить ни одной фотографии, возвращаем заглушку
    if not photo_urls:
        print("No photo URLs were obtained, returning placeholder")
        return ["https://via.placeholder.com/800x600?text=No+Image+Available"]
    
    print(f"Returning {len(photo_urls)} photo URLs")
    # Проверяем, что все URL не пустые
    for i, url in enumerate(photo_urls):
        if not url or not isinstance(url, str):
            print(f"Photo URL {i} is invalid: {url}")
            photo_urls[i] = f"https://via.placeholder.com/800x600?text=Invalid+URL+{i}"
    
    return photo_urls

def search_places_by_type(
    place_type: str = "lodging",  # По умолчанию ищем отели, но можно указать "restaurant"
    query: Optional[str] = None,
    location: Optional[str] = None,
    radius: Optional[int] = None,
    min_rating: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Поиск мест по типу (отели, рестораны) с использованием Google Places API
    """
    params = {
        "key": GOOGLE_API_KEY,
        "type": place_type,  # Тип места - отель или ресторан
    }
    
    # Добавляем параметры, если они указаны
    if query:
        params["query"] = query
    
    if location and radius:
        params["location"] = location
        params["radius"] = radius
    
    try:
        response = requests.get(PLACE_SEARCH_URL, params=params)
        data = response.json()
        
        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')}, {data.get('error_message', '')}")
            return []
        
        results = data.get("results", [])
        print(f"Found {len(results)} {place_type}s in search results")
        
        # Фильтрация по рейтингу, если указан
        if min_rating is not None:
            results = [r for r in results if r.get("rating", 0) >= min_rating]
            print(f"{len(results)} {place_type}s meet the minimum rating criteria")
            
        # Преобразование результатов в нужный формат
        places = []
        for i, place in enumerate(results):
            print(f"Processing {place_type} {i+1}: {place.get('name')}")
            photos_data = place.get("photos", [])
            print(f"{place_type} {i+1} has {len(photos_data)} photos in API response")
            
            # Получаем URL фотографий
            photo_urls = get_place_photos(photos_data)
            print(f"Got {len(photo_urls)} photo URLs for {place_type} {i+1}")
            
            # Обрабатываем адрес
            address = place.get("formatted_address")
            if address is None:
                # Если formatted_address отсутствует, используем vicinity или имя места
                address = place.get("vicinity") or place.get("name", "Unknown Address")
                print(f"Missing formatted_address for {place_type} {i+1}, using fallback: {address}")
            
            # Обрабатываем название
            name = place.get("name")
            if name is None:
                name = f"Unknown {place_type.capitalize()}"
                print(f"Missing name for {place_type} {i+1}, using fallback: {name}")
            
            place_data = {
                "place_id": place.get("place_id", ""),
                "name": name,
                "address": address,
                "vicinity": place.get("vicinity") or address,
                "latitude": place.get("geometry", {}).get("location", {}).get("lat", 0.0),
                "longitude": place.get("geometry", {}).get("location", {}).get("lng", 0.0),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total"),
                "photos": photo_urls,
                "details": {
                    "price_level": place.get("price_level"),
                    "types": place.get("types"),
                    "icon": place.get("icon"),
                    "icon_background_color": place.get("icon_background_color"),
                    "business_status": place.get("business_status"),
                    "plus_code": place.get("plus_code"),
                },
                "place_type": place_type  # Добавляем тип места
            }
            places.append(place_data)
            
        print(f"Returning {len(places)} processed {place_type}s")
        return places
    except Exception as e:
        print(f"Error searching {place_type}s: {e}")
        return []

def get_place_details(place_id: str) -> Optional[Dict[str, Any]]:
    """
    Получение детальной информации о месте по его place_id
    """
    # Расширенный список полей для запроса
    fields = [
        "name", "formatted_address", "geometry", "rating", "photos", "price_level", 
        "formatted_phone_number", "international_phone_number", "website", "opening_hours", 
        "reviews", "types", "user_ratings_total", "icon", "icon_background_color", "url", 
        "vicinity", "address_components", "adr_address", "business_status", "current_opening_hours",
        "editorial_summary", "plus_code", "utc_offset", "wheelchair_accessible_entrance"
    ]
    
    params = {
        "key": GOOGLE_API_KEY,
        "place_id": place_id,
        "fields": ",".join(fields)
    }
    
    try:
        print(f"Getting details for place_id: {place_id}")
        response = requests.get(PLACE_DETAILS_URL, params=params)
        data = response.json()
        
        if data.get("status") != "OK":
            print(f"API Error: {data.get('status')}, {data.get('error_message', '')}")
            return None
        
        place = data.get("result", {})
        photos_data = place.get("photos", [])
        print(f"Place has {len(photos_data)} photos in API response")
        
        # Получаем URL фотографий
        photo_urls = get_place_photos(photos_data)
        print(f"Got {len(photo_urls)} photo URLs for place details")
        
        # Обработка отзывов
        reviews = place.get("reviews", [])
        print(f"Place has {len(reviews)} reviews in API response")
        
        # Убедимся, что отзывы - это список
        if reviews and not isinstance(reviews, list):
            print(f"Reviews is not a list, but {type(reviews)}")
            reviews = []
        
        # Проверим структуру отзывов
        if reviews:
            print(f"First review structure: {reviews[0].keys() if reviews[0] else 'None'}")
            
            # Проверка на наличие необходимых полей
            for i, review in enumerate(reviews):
                if not isinstance(review, dict):
                    print(f"Review {i} is not a dict, but {type(review)}")
                    continue
                    
                # Проверяем наличие обязательных полей
                required_fields = ["author_name", "rating", "text"]
                for field in required_fields:
                    if field not in review:
                        print(f"Review {i} is missing required field: {field}")
                        review[field] = "N/A" if field != "rating" else 0
        
        # Обрабатываем адрес
        address = place.get("formatted_address")
        if address is None:
            # Если formatted_address отсутствует, используем vicinity или имя места
            address = place.get("vicinity") or place.get("name", "Unknown Address")
            print(f"Missing formatted_address for place, using fallback: {address}")
        
        # Обрабатываем название
        name = place.get("name")
        if name is None:
            name = "Unknown Place"
            print(f"Missing name for place, using fallback: {name}")
        
        # Извлекаем текстовое описание из editorial_summary, если оно есть
        editorial_summary = None
        if place.get("editorial_summary") and isinstance(place.get("editorial_summary"), dict):
            editorial_summary = place.get("editorial_summary").get("overview")
        
        # Определяем тип места
        place_type = "unknown"
        types = place.get("types", [])
        if "lodging" in types:
            place_type = "hotel"
        elif "restaurant" in types:
            place_type = "restaurant"
        
        # Создаем структуру с детальной информацией
        place_details = {
            "place_id": place_id,
            "name": name,
            "address": address,
            "vicinity": place.get("vicinity") or address,
            "latitude": place.get("geometry", {}).get("location", {}).get("lat", 0.0),
            "longitude": place.get("geometry", {}).get("location", {}).get("lng", 0.0),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "photos": photo_urls,
            "place_type": place_type,  # Добавляем тип места
            "details": {
                "price_level": place.get("price_level"),
                "phone": place.get("formatted_phone_number"),
                "international_phone": place.get("international_phone_number"),
                "website": place.get("website"),
                "opening_hours": place.get("opening_hours"),
                "current_opening_hours": place.get("current_opening_hours"),
                "types": place.get("types"),
                "icon": place.get("icon"),
                "icon_background_color": place.get("icon_background_color"),
                "google_maps_url": place.get("url"),
                "business_status": place.get("business_status"),
                "address_components": place.get("address_components"),
                "adr_address": place.get("adr_address"),
                "plus_code": place.get("plus_code"),
                "utc_offset": place.get("utc_offset"),
                "wheelchair_accessible": place.get("wheelchair_accessible_entrance"),
                "editorial_summary": editorial_summary,
                "reviews": reviews
            }
        }
        
        # Проверка структуры результата
        print(f"Place details structure: {place_details.keys()}")
        print(f"Place details['details'] structure: {place_details['details'].keys()}")
        print(f"Reviews count in result: {len(place_details['details']['reviews'])}")
        
        return place_details
    except Exception as e:
        print(f"Error getting place details: {e}")
        return None 