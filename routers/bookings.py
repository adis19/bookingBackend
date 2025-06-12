from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Booking, Hotel, User, Favorite
from schemas import (
    BookingCreate, 
    BookingUpdate, 
    BookingResponse, 
    FavoriteCreate, 
    FavoriteResponse
)
from security import get_current_active_user, get_admin_user

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

# Эндпоинты для бронирований
@router.post("/", response_model=BookingResponse)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Создание нового бронирования.
    """
    # Проверка существования отеля
    hotel = db.query(Hotel).filter(Hotel.id == booking_data.hotel_id).first()
    
    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель не найден"
        )
    
    # Создание бронирования
    new_booking = Booking(
        user_id=current_user.id,
        hotel_id=booking_data.hotel_id,
        check_in_date=booking_data.check_in_date,
        check_out_date=booking_data.check_out_date,
        guests=booking_data.guests,
        notes=booking_data.notes
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    # Загрузка связанных данных для ответа
    booking_with_relations = db.query(Booking).filter(Booking.id == new_booking.id).options(joinedload(Booking.hotel)).first()
    
    return booking_with_relations

@router.get("/my", response_model=List[BookingResponse])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение списка бронирований текущего пользователя.
    """
    bookings = db.query(Booking).filter(Booking.user_id == current_user.id).options(joinedload(Booking.hotel)).all()
    
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение информации о конкретном бронировании.
    """
    # Обычные пользователи могут видеть только свои бронирования
    if not current_user.is_admin:
        booking = db.query(Booking).filter(
            Booking.id == booking_id, 
            Booking.user_id == current_user.id
        ).options(joinedload(Booking.hotel)).first()
    else:
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).options(joinedload(Booking.hotel)).first()
    
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновление информации о бронировании.
    """
    # Обычные пользователи могут обновлять только свои бронирования
    if not current_user.is_admin:
        booking = db.query(Booking).filter(
            Booking.id == booking_id, 
            Booking.user_id == current_user.id
        ).first()
    else:
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()
    
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    # Обновление полей
    if booking_data.check_in_date is not None:
        booking.check_in_date = booking_data.check_in_date
    
    if booking_data.check_out_date is not None:
        booking.check_out_date = booking_data.check_out_date
    
    if booking_data.guests is not None:
        booking.guests = booking_data.guests
    
    if booking_data.status is not None:
        booking.status = booking_data.status
    
    if booking_data.notes is not None:
        booking.notes = booking_data.notes
    
    db.commit()
    db.refresh(booking)
    
    # Загрузка связанных данных для ответа
    booking_with_relations = db.query(Booking).filter(
        Booking.id == booking.id
    ).options(joinedload(Booking.hotel)).first()
    
    return booking_with_relations

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удаление бронирования.
    """
    # Обычные пользователи могут удалять только свои бронирования
    if not current_user.is_admin:
        booking = db.query(Booking).filter(
            Booking.id == booking_id, 
            Booking.user_id == current_user.id
        ).first()
    else:
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()
    
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    db.delete(booking)
    db.commit()
    
    return None

# Эндпоинты для избранного
@router.post("/favorites", response_model=FavoriteResponse)
def add_to_favorites(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Добавление отеля в избранное.
    """
    # Проверка существования отеля
    hotel = db.query(Hotel).filter(Hotel.id == favorite_data.hotel_id).first()
    
    if hotel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель не найден"
        )
    
    # Проверка, что отель еще не в избранном
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.hotel_id == favorite_data.hotel_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отель уже в избранном"
        )
    
    # Добавление в избранное
    new_favorite = Favorite(
        user_id=current_user.id,
        hotel_id=favorite_data.hotel_id
    )
    
    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)
    
    # Загрузка связанных данных для ответа
    favorite_with_relations = db.query(Favorite).filter(
        Favorite.id == new_favorite.id
    ).options(joinedload(Favorite.hotel)).first()
    
    return favorite_with_relations

@router.get("/favorites", response_model=List[FavoriteResponse])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение списка избранных отелей.
    """
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).options(joinedload(Favorite.hotel)).all()
    
    return favorites

@router.delete("/favorites/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_favorites(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удаление отеля из избранного.
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.hotel_id == hotel_id
    ).first()
    
    if favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель не найден в избранном"
        )
    
    db.delete(favorite)
    db.commit()
    
    return None

# Административные эндпоинты
@router.get("/", response_model=List[BookingResponse])
def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Получение списка всех бронирований (только для админов).
    """
    bookings = db.query(Booking).options(joinedload(Booking.hotel)).offset(skip).limit(limit).all()
    
    return bookings 