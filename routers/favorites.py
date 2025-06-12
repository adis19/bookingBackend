from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Favorite, User
from schemas import FavoriteResponse, FavoriteCreate, FavoriteCheck
from database import get_db
from security import get_current_user

router = APIRouter(
    prefix="/api/favorites",
    tags=["favorites"],
)

@router.get("", response_model=List[FavoriteResponse])
def get_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Получение всех избранных отелей пользователя"""
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return favorites

@router.post("", status_code=status.HTTP_201_CREATED)
def add_to_favorites(favorite: FavoriteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Добавление отеля в избранное"""
    # Проверяем, существует ли уже такая запись
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.hotel_id == favorite.hotel_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отель уже добавлен в избранное"
        )
    
    # Создаем запись в избранном
    db_favorite = Favorite(
        user_id=current_user.id,
        hotel_id=favorite.hotel_id
    )
    
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    
    return {"message": "Отель успешно добавлен в избранное", "favorite_id": db_favorite.id}

@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_favorites(favorite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Удаление отеля из избранного"""
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись в избранном не найдена"
        )
    
    # Проверяем, принадлежит ли запись текущему пользователю
    if favorite.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для удаления этой записи"
        )
    
    db.delete(favorite)
    db.commit()
    
    return None

@router.get("/check/{hotel_id}", response_model=FavoriteCheck)
def check_if_favorite(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Проверка, добавлен ли отель в избранное"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.hotel_id == hotel_id
    ).first()
    
    return {"is_favorite": favorite is not None} 