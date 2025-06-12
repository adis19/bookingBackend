from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

# Схемы пользователей
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Схемы отелей
class HotelBase(BaseModel):
    place_id: str
    name: str
    address: str
    vicinity: Optional[str] = None
    latitude: float
    longitude: float
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    photos: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None
    place_type: Optional[str] = "hotel"  # Тип места: hotel, restaurant, etc.

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    vicinity: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    photos: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None
    place_type: Optional[str] = None

class HotelResponse(HotelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Схемы бронирований
class BookingBase(BaseModel):
    hotel_id: int
    check_in_date: datetime
    check_out_date: datetime
    guests: int = Field(ge=1)
    notes: Optional[str] = None

    @validator('check_out_date')
    def check_dates(cls, v, values):
        if 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('Дата выезда должна быть позже даты заезда')
        return v

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    guests: Optional[int] = Field(None, ge=1)
    status: Optional[str] = None
    notes: Optional[str] = None

class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    hotel: HotelResponse

    class Config:
        from_attributes = True

# Схемы избранного
class FavoriteBase(BaseModel):
    hotel_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteResponse(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime
    hotel: HotelResponse

    class Config:
        from_attributes = True

class FavoriteCheck(BaseModel):
    is_favorite: bool

# Схемы аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: Optional[bool] = False

# Схемы для Google Places API
class PlaceSearchParams(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None  # формат "latitude,longitude"
    radius: Optional[int] = Field(None, ge=1, le=50000)  # в метрах, максимум 50км
    type: Optional[str] = "lodging"  # тип места (отель или ресторан)
    min_rating: Optional[float] = Field(None, ge=1, le=5)

class PlaceDetails(BaseModel):
    place_id: str 