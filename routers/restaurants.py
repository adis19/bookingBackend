from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, select

from database import get_db
from models import Hotel, User
from schemas import HotelResponse, PlaceSearchParams, PlaceDetails
from google_places import search_places_by_type, get_place_details
from security import get_current_active_user, get_admin_user

router = APIRouter(prefix="/restaurants", tags=["Рестораны"])

@router.get("/search", response_model=List[HotelResponse])
def search_restaurants_endpoint(
    query: Optional[str] = None,
    location: Optional[str] = None,
    radius: Optional[int] = Query(None, ge=1, le=50000),
    min_rating: Optional[float] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    Поиск ресторанов с использованием Google Places API.
    Результаты сохраняются в базу данных.
    """
    # Поиск ресторанов через Google Places API
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

@router.get("/details/{place_id}", response_model=HotelResponse)
def get_restaurant_details_endpoint(
    place_id: str,
    db: Session = Depends(get_db)
):
    """
    Получение детальной информации о ресторане по его place_id.
    Информация сохраняется в базу данных.
    """
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