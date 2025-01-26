from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import json
import time
import requests

# Создаем экземпляр FastAPI
app = FastAPI()

# Файл для хранения данных
DB_FILE = "db.json"

CAR_FILE = "cars.json"

CREDIT_FILE = "credit.json"

BOT_TOKEN = "7395802028:AAE-uAzLVP-0O0nNI9-cQ-5AgI2U6-uS08o"

ADMIN_TG_ID = 1958259113

# Проверяем наличие файла базы данных, если его нет — создаем пустой JSON-файл
try:
    with open(DB_FILE, "r") as f:
        users_db = json.load(f)
except FileNotFoundError:
    with open(DB_FILE, "w") as f:
        json.dump([], f)
    users_db = []

try:
    with open(CAR_FILE, "r") as f:
        cars_db = json.load(f)
except FileNotFoundError:
    with open(CAR_FILE, "w") as f:
        json.dump([], f)
    cars_db = []

try:
    with open(CREDIT_FILE, "r") as f:
        credit_db = json.load(f)
except FileNotFoundError:
    with open(CREDIT_FILE, "w") as f:
        json.dump([], f)
    credit_db = []

# Модели данных для POST-запросов
class User(BaseModel):
    name: str
    age: int
    user_id: int
    balance: int
    password: str
    login: str
    subscriptions: bool = False
    expired_date: datetime
    tg_id: int

class Message(BaseModel):
    sender: str
    recipient: str
    content: str

class Car(BaseModel):
    name: str
    price: int
    year: int
    color: str
    list_founder: List[str] = []
    vin: int

class Credit(BaseModel):
    user_id: int
    car_vin: int
    count_payment: int
    percent: int
    id: int
    status: bool = False
    remaining_balance: int


# Функция для сохранения пользователей в JSON-файл
def save_users_to_file():
    with open(DB_FILE, "w") as f:
        json.dump(users_db, f, default=str, indent=4)

def save_cars_to_file():
    with open(CAR_FILE, "w") as f:
        json.dump(cars_db, f, default=str, indent=4)

def save_credit_to_file():
    with open(CREDIT_FILE, "w") as f:
        json.dump(credit_db, f, default=str, indent=4)

# Функция для создания нового пользователя
def create_user(user: User) -> User:
    users_db.append(user.dict())
    save_users_to_file()
    return user

def create_car(car: Car) -> Car:
    cars_db.append(car.dict())
    save_cars_to_file()
    return car

def create_credit(credit: Credit) -> Credit:
    credit_db.append(credit.dict())
    save_credit_to_file()
    return credit

# Функция для получения пользователя по user_id
def get_user_from_id(user_id: int) -> User:
    for user_data in users_db:
        if user_data["user_id"] == user_id:
            return User(**user_data)
    return None 

def get_car_from_vin(car_vin: int) -> Car:
    for car_data in cars_db:
        if car_data["vin"] == car_vin:
            return Car(**car_data)
    return None

def get_credit_from_id(credit_id: int) -> Credit:
    print(credit_db)
    for credit_data in credit_db:
        if credit_data["id"] == credit_id:
            return Credit(**credit_data)
    return None

def send_message(user_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    params = {
        'chat_id': user_id,
        'text': text
    }
    response = requests.get(url, params=params)
    return response.json()


def credit_scalper(
        user:User,
        credit:Credit,  
        car:Car
    ) -> None:
    for _ in range(credit.count_payment):
        percent = (car.price/credit.count_payment)/100*credit.percent
        percent += car.price/credit.count_payment
        time.sleep(5)
        msg_admin = f"User:{user.name}😏 dont have money"
        for user_data in users_db:
            if user_data["user_id"] == user.user_id:
                user_data["balance"] -= percent
                if user_data["balance"] < 0:
                    send_message(msg_admin,ADMIN_TG_ID)
                break

        save_users_to_file()
    for car_data in cars_db:
        if car_data["vin"] == car.vin:
            if car_data.get("list_founder") is None:  # Проверяем, если поле пустое или не инициализировано
                car_data["list_founder"] = []  # Инициализируем его как пустой список
            car_data["list_founder"].append(user.name)  # Добавляем имя пользователя
            break
    save_cars_to_file()
    
# Определяем GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# GET endpoint для получения пользователя по ID
@app.get("/user/{user_id}")
def read_user(user_id: int):
    user = get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# POST endpoint для создания пользователя
@app.post("/users")
def create_user_endpoint(user: User):
    existing_user = get_user_from_id(user.user_id)
    if existing_user:
        raise HTTPException(status_code=400, detail=f"User with ID {user.user_id} already exists!")
    new_user = create_user(user)
    return {"message": f"User {new_user.login} created successfully!"}

# POST endpoint для отправки сообщения
@app.post("/message")
def send_message(message: Message):
    return {"message": f"Message from {message.sender} to {message.recipient}: {message.content}"}

# POST endpoint для подписок
@app.post("/subscriptions")
def get_subscriptions(user_id: int, price: int):
    user = get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.age < 30:
        price *= 0.9

    return {
        "user": user,
        "price": price
    }

# POST endpoint для обновления баланса пользователя
@app.post("/update_balance")
def update_user_balance(user_id: int, new_balance: int):
    user = get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем баланс пользователя
    for user_data in users_db:
        if user_data["user_id"] == user_id:
            user_data["balance"] = new_balance
            break

    save_users_to_file()

    return {"message": f"Balance for user {user.login} updated to {new_balance}"}


@app.post("/popup_balance")
def popup_user_balance(user_id: int, new_balance: int):
    user = get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем баланс пользователя
    for user_data in users_db:
        if user_data["user_id"] == user_id:
            user_data["balance"] += new_balance
            break

    save_users_to_file()

    return {"message": f"Balance for user {user.login} updated to {new_balance}"}



@app.get("/cars")
def get_all_cars():
    return cars_db

@app.get("/car_by_vin/{vin}")
def get_car_by_vin(vin: int):
    car = get_car_from_vin(vin)
    return car


@app.post("/sale_car")
def sale_car(user_id: int, vin: int):
    car = get_car_from_vin(vin)
    user = get_user_from_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_balance = user.balance - car.price

    if new_balance < 0:
        return f"Ты пидор у тебя шекелей нету"

    # Обновляем баланс пользователя
    for user_data in users_db:
        if user_data["user_id"] == user_id:
            user_data["balance"] = new_balance
            break
    for car_data in cars_db:
        if car_data["vin"] == vin:
            if car_data.get("list_founder") is None:  # Проверяем, если поле пустое или не инициализировано
                car_data["list_founder"] = []  # Инициализируем его как пустой список
            car_data["list_founder"].append(user.name)  # Добавляем имя пользователя
            break



    save_users_to_file()
    save_cars_to_file()
    return f"{user.name} buy car:{car.name} with price:{car.price} new user balance:{new_balance} old balance:{user.balance}"

@app.post("/new_car")
def new_car(car:Car):
    existing_car = get_car_from_vin(car.vin)
    if existing_car:
        raise HTTPException(status_code=400, detail=f"Car with vin {car.vin} already exists!")
    new_car = create_car(car)
    return {"message": f"Car {new_car.name} created successfully!"}

@app.post("/new_credit")
def new_credit(credit:Credit):
    try:
        existing_car = get_car_from_vin(credit.car_vin)
    except Exception as e:
        existing_car = None
    if not existing_car:
        raise HTTPException(status_code=404, detail=f"Car with vin {credit.car_vin} NOT FOUND!")
    
    try:
        existing_user = get_user_from_id(credit.user_id)
    except Exception as e:
        existing_user = None
    if not existing_user:
        raise HTTPException(status_code=404, detail=f"User with id {credit.user_id} not found!")

    try:
        existing_credit = get_credit_from_id(credit.id)
    except Exception as e:
        existing_credit = None
    if existing_credit:
        raise HTTPException(status_code=400, detail=f"Credit with id {credit.id} already exists!")
    new_credit = create_credit(credit)

    credit_scalper(user=existing_user, credit=new_credit, car=existing_car)

    return {"message": f"Credit{new_credit.id} created successfully!"}
