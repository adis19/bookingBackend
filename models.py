from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    bookings = relationship("Booking", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String, unique=True, index=True)  # ID из Google Places API
    name = Column(String)
    address = Column(String)
    vicinity = Column(String, nullable=True)  # Короткий адрес
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float, nullable=True)
    user_ratings_total = Column(Integer, nullable=True)  # Количество оценок
    photos = Column(JSON, nullable=True)  # JSON массив URL фотографий
    details = Column(JSON, nullable=True)  # Дополнительные детали в JSON
    place_type = Column(String, nullable=True, default="hotel")  # Тип места: hotel, restaurant, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    bookings = relationship("Booking", back_populates="hotel")
    favorites = relationship("Favorite", back_populates="hotel")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    guests = Column(Integer)
    status = Column(String, default="pending")  # pending, confirmed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    user = relationship("User", back_populates="bookings")
    hotel = relationship("Hotel", back_populates="bookings")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    user = relationship("User", back_populates="favorites")
    hotel = relationship("Hotel", back_populates="favorites") 