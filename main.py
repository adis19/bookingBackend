from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from database import get_db, engine
from routers import auth, hotels, users, bookings, favorites
from models import Base
from migrate_db import run_migration

app = FastAPI(title="LastBooking API", description="API для бронирования отелей")

# Настройка CORS для взаимодействия с Flutter-приложением
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/api", tags=["Аутентификация"])
app.include_router(hotels.router, prefix="/api", tags=["Отели"])
app.include_router(users.router, prefix="/api", tags=["Пользователи"])
app.include_router(bookings.router, prefix="/api", tags=["Бронирования"])
app.include_router(favorites.router, tags=["Избранное"])

# Добавляем перенаправление запросов к ресторанам на hotels.router
@app.get("/api/restaurants/search")
def redirect_restaurant_search(
    query: str = None,
    location: str = None,
    radius: int = None,
    min_rating: float = None,
    type: str = None,
    db = Depends(get_db)
):
    """
    Перенаправление запросов поиска ресторанов на функцию поиска отелей с типом restaurant
    """
    from google_places import search_places_by_type
    from schemas import HotelResponse
    
    # Поиск ресторанов
    restaurants_data = search_places_by_type(
        place_type="restaurant",
        query=query,
        location=location,
        radius=radius,
        min_rating=min_rating
    )
    
    if not restaurants_data:
        return []
    
    # Сохраняем результаты в базу данных и возвращаем их
    from models import Hotel
    
    saved_restaurants = []
    for restaurant_data in restaurants_data:
        # Проверяем, существует ли ресторан в базе данных
        existing_restaurant = db.query(Hotel).filter(Hotel.place_id == restaurant_data["place_id"]).first()
        
        # Удаляем поля, которых может не быть в модели
        restaurant_data_filtered = {
            "place_id": restaurant_data.get("place_id"),
            "name": restaurant_data.get("name"),
            "address": restaurant_data.get("address"),
            "vicinity": restaurant_data.get("vicinity"),
            "latitude": restaurant_data.get("latitude"),
            "longitude": restaurant_data.get("longitude"),
            "rating": restaurant_data.get("rating"),
            "user_ratings_total": restaurant_data.get("user_ratings_total"),
            "photos": restaurant_data.get("photos"),
            "details": restaurant_data.get("details"),
            "place_type": "restaurant"  # Указываем тип места
        }
        
        if existing_restaurant:
            # Обновляем существующий ресторан
            for key, value in restaurant_data_filtered.items():
                setattr(existing_restaurant, key, value)
            restaurant = existing_restaurant
        else:
            # Создаем новый ресторан
            restaurant = Hotel(**restaurant_data_filtered)
            db.add(restaurant)
        
        db.commit()
        db.refresh(restaurant)
        saved_restaurants.append(restaurant)
    
    return saved_restaurants

@app.get("/api/restaurants/details/{place_id}")
def redirect_restaurant_details(
    place_id: str,
    db = Depends(get_db)
):
    """
    Перенаправление запросов получения деталей ресторана
    """
    from google_places import get_place_details
    from models import Hotel
    
    # Проверяем, есть ли ресторан в базе данных
    existing_restaurant = db.query(Hotel).filter(Hotel.place_id == place_id).first()
    
    # Получаем актуальные данные из API
    restaurant_data = get_place_details(place_id)
    
    if not restaurant_data:
        if existing_restaurant:
            return existing_restaurant
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ресторан не найден"
        )
    
    # Удаляем поля, которых может не быть в модели
    restaurant_data_filtered = {
        "place_id": restaurant_data.get("place_id"),
        "name": restaurant_data.get("name"),
        "address": restaurant_data.get("address"),
        "vicinity": restaurant_data.get("vicinity"),
        "latitude": restaurant_data.get("latitude"),
        "longitude": restaurant_data.get("longitude"),
        "rating": restaurant_data.get("rating"),
        "user_ratings_total": restaurant_data.get("user_ratings_total"),
        "photos": restaurant_data.get("photos"),
        "details": restaurant_data.get("details"),
        "place_type": "restaurant"  # Указываем тип места
    }
    
    if existing_restaurant:
        # Обновляем существующий ресторан
        for key, value in restaurant_data_filtered.items():
            setattr(existing_restaurant, key, value)
        restaurant = existing_restaurant
    else:
        # Создаем новый ресторан
        restaurant = Hotel(**restaurant_data_filtered)
        db.add(restaurant)
    
    db.commit()
    db.refresh(restaurant)
    
    return restaurant

@app.on_event("startup")
def startup():
    # Создание таблиц в базе данных при запуске
    Base.metadata.create_all(bind=engine)
    # Запуск миграции для добавления новых полей
    try:
        run_migration()
    except Exception as e:
        print(f"Ошибка при выполнении миграции: {e}")

@app.get("/")
def root():
    return {"message": "LastBooking API работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 