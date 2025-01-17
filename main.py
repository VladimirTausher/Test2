# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Создаем экземпляр FastAPI
app = FastAPI()

# Модели данных для POST-запросов
class User(BaseModel):
    name: str
    age: int
    user_id: int
    balance: int
    password: str
    login: str


class Message(BaseModel):
    sender: str
    recipient: str
    content: str

# Статическая переменная для хранения пользователей
users_db: List[User] = []

def get_user_from_id(user_id: int) -> User:
    with open("db.txt","r") as f:
        our_db = f.readline()
    for data in our_db:
        user_data_list = data.split('|')
        user: User = User(
            user_id = int(user_data_list[0]),
            name = user_data_list[1],
            password = user_data_list[4],
            balance = int(user_data_list[-1]),
            login = user_data_list[3],
            age = int(user_data_list[2]),
        )
        if user_id == user.user_id:
            return user
    return {}


# Определяем GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# GET endpoint для получения пользователя по ID
@app.get("/user/{user_id}")
def read_user(user_id: int):
    get_user_from_id(user_id)
    return {}

# POST endpoint для создания пользователя
@app.post("/users")
def create_user(user: User):
    old_user = get_user_from_id(user.user_id)
    if old_user.login == user.login:
        return {
            'message': f"User {user.login} already exists!"
        }
    result = f"{user.user_id}|{user.name}|{user.age}|{user.login}|{user.password}|{user.balance}\n"
    with open("db.txt", "a") as f:
        f.write(result)
    return {"message": f"User {user.login} created successfully!"}

# POST endpoint для отправки сообщения
@app.post("/message")
def send_message(message: Message):
    return {"message": f"Message from {message.sender} to {message.recipient}: {message.content}"}


@app.post("/subscriptions")
def get_subscriptions(user_id: int , price: int):
    user = get_user_from_id(user_id)
    if user.age < 30:
        price *= 0.9
    return {
        "user":user,
        "price":price
    }


