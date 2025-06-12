import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Импортируем настройки базы данных
from database import DATABASE_URL

def run_migration():
    """Выполняет миграцию базы данных для добавления новых полей в таблицу hotels"""
    engine = create_engine(DATABASE_URL)
    
    # Проверяем существование колонок
    try:
        with engine.connect() as connection:
            # Проверяем наличие колонки vicinity
            result = connection.execute(text("PRAGMA table_info(hotels)"))
            columns = [row[1] for row in result]
            
            # Список миграций для выполнения
            migrations = []
            
            # Добавляем колонку vicinity, если её нет
            if "vicinity" not in columns:
                migrations.append("ALTER TABLE hotels ADD COLUMN vicinity TEXT;")
                print("Добавление колонки vicinity...")
            
            # Добавляем колонку user_ratings_total, если её нет
            if "user_ratings_total" not in columns:
                migrations.append("ALTER TABLE hotels ADD COLUMN user_ratings_total INTEGER;")
                print("Добавление колонки user_ratings_total...")
            
            # Добавляем колонку place_type, если её нет
            if "place_type" not in columns:
                migrations.append("ALTER TABLE hotels ADD COLUMN place_type TEXT DEFAULT 'hotel';")
                print("Добавление колонки place_type...")
            
            # Выполняем миграции
            for migration in migrations:
                connection.execute(text(migration))
                connection.commit()
            
            if migrations:
                print("Миграция успешно выполнена!")
            else:
                print("Миграция не требуется, все колонки уже существуют.")
                
    except OperationalError as e:
        print(f"Ошибка при выполнении миграции: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 