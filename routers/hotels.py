from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, select

from database import get_db
from models import Hotel, User
from schemas import HotelCreate, HotelResponse, PlaceSearchParams, PlaceDetails
from google_places import search_hotels, get_hotel_details
from security import get_current_active_user, get_admin_user

router = APIRouter(prefix="/hotels", tags=["Отели"])

@router.get("/search", response_model=List[HotelResponse])
def search_hotels_endpoint(
    query: Optional[str] = None,
    location: Optional[str] = None,
    radius: Optional[int] = Query(None, ge=1, le=50000),
    min_rating: Optional[float] = Query(None, ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    Поиск отелей с использованием Google Places API.
    Результаты сохраняются в базу данных.
    """
    # Поиск отелей через Google Places API
    hotels_data = search_hotels(
        query=query,
        location=location,
        radius=radius,
        min_rating=min_rating
    )
    
    if not hotels_data:
        return []
    
    # Сохраняем результаты в базу данных и возвращаем их
    saved_hotels = []
    for hotel_data in hotels_data:
        # Проверяем, существует ли отель в базе данных
        existing_hotel = db.query(Hotel).filter(Hotel.place_id == hotel_data["place_id"]).first()
        
        # Удаляем поля, которых может не быть в модели
        hotel_data_filtered = {
            "place_id": hotel_data.get("place_id"),
            "name": hotel_data.get("name"),
            "address": hotel_data.get("address"),
            "vicinity": hotel_data.get("vicinity"),
            "latitude": hotel_data.get("latitude"),
            "longitude": hotel_data.get("longitude"),
            "rating": hotel_data.get("rating"),
            "user_ratings_total": hotel_data.get("user_ratings_total"),
            "photos": hotel_data.get("photos"),
            "details": hotel_data.get("details")
        }
        
        if existing_hotel:
            # Обновляем существующий отель
            for key, value in hotel_data_filtered.items():
                setattr(existing_hotel, key, value)
            hotel = existing_hotel
        else:
            # Создаем новый отель
            hotel = Hotel(**hotel_data_filtered)
            db.add(hotel)
        
        db.commit()
        db.refresh(hotel)
        saved_hotels.append(hotel)
    
    return saved_hotels

@router.get("/details/{place_id}", response_model=HotelResponse)
def get_hotel_details_endpoint(
    place_id: str,
    db: Session = Depends(get_db)
):
    """
    Получение детальной информации об отеле по его place_id.
    Информация сохраняется в базу данных.
    """
    # Проверяем, есть ли отель в базе данных
    existing_hotel = db.query(Hotel).filter(Hotel.place_id == place_id).first()
    
    # Получаем актуальные данные из API
    hotel_data = get_hotel_details(place_id)
    
    if not hotel_data:
        if existing_hotel:
            return existing_hotel
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель не найден"
        )
    
    # Удаляем поля, которых может не быть в модели
    hotel_data_filtered = {
        "place_id": hotel_data.get("place_id"),
        "name": hotel_data.get("name"),
        "address": hotel_data.get("address"),
        "vicinity": hotel_data.get("vicinity"),
        "latitude": hotel_data.get("latitude"),
        "longitude": hotel_data.get("longitude"),
        "rating": hotel_data.get("rating"),
        "user_ratings_total": hotel_data.get("user_ratings_total"),
        "photos": hotel_data.get("photos"),
        "details": hotel_data.get("details")
    }
    
    if existing_hotel:
        # Обновляем существующий отель
        for key, value in hotel_data_filtered.items():
            setattr(existing_hotel, key, value)
        hotel = existing_hotel
    else:
        # Создаем новый отель
        hotel = Hotel(**hotel_data_filtered)
        db.add(hotel)
    
    db.commit()
    db.refresh(hotel)
    
    return hotel

@router.get("/", response_model=List[HotelResponse])
def get_hotels(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получение списка отелей из базы данных с возможностью поиска.
    """
    query = db.query(Hotel)
    
    if search:
        query = query.filter(
            or_(
                Hotel.name.ilike(f"%{search}%"),
                Hotel.address.ilike(f"%{search}%")
            )
        )
    
    hotels = query.offset(skip).limit(limit).all()
    
    return hotels

@router.get("/{hotel_id}", response_model=HotelResponse)
def get_hotel(
    hotel_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение информации об отеле по его ID из базы данных.
    """
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    
    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель не найден"
        )
    
    return hotel 