from database import get_db, engine
from models import Base, User
from security import get_password_hash

# Создаем таблицы, если они не существуют
Base.metadata.create_all(bind=engine)

# Получаем соединение с базой данных
db = next(get_db())

# Данные для администратора
username = "admin"
email = "admin@example.com"
password = "admin123"
hashed_password = get_password_hash(password)

# Проверяем, существует ли пользователь
existing_user = db.query(User).filter(User.username == username).first()

if existing_user:
    # Обновляем существующего пользователя
    existing_user.is_admin = True
    existing_user.is_active = True
    existing_user.hashed_password = hashed_password
    print(f"Пользователь {username} обновлен и теперь является администратором")
else:
    # Создаем нового пользователя-администратора
    new_admin = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=True,
        is_active=True
    )
    db.add(new_admin)
    print(f"Администратор {username} создан")

# Сохраняем изменения
db.commit()
db.close()

print(f"Готово! Используйте логин: {username}, пароль: {password}") 