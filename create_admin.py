from database import get_db, engine
from models import Base, User
from security import get_password_hash
from sqlalchemy.orm import Session

def create_admin(username: str, email: str, password: str):
    # Создаем таблицы, если они не существуют
    Base.metadata.create_all(bind=engine)
    
    # Получаем соединение с базой данных
    db = next(get_db())
    
    try:
        # Проверяем, существует ли пользователь с таким именем
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"Пользователь с именем {username} уже существует.")
            
            # Если пользователь существует, но не админ, делаем его админом
            if not existing_user.is_admin:
                existing_user.is_admin = True
                db.commit()
                print(f"Пользователь {username} теперь администратор.")
            else:
                print(f"Пользователь {username} уже является администратором.")
                
            return
        
        # Создаем нового пользователя-администратора
        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_admin=True,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        print(f"Администратор создан: {username} / {password}")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при создании администратора: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin("admin", "admin@example.com", "admin123") 