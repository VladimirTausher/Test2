import json

# Данные о машинах и их ценах
cars_data = [
    {"name": "Toyota Camry", "price": 30000},
    {"name": "Honda Accord", "price": 28000},
    {"name": "Ford Mustang", "price": 45000},
    {"name": "Tesla Model 3", "price": 40000},
    {"name": "BMW 3 Series", "price": 42000},
]

# Создаем JSON-файл
with open("cars.json", "w") as json_file:
    json.dump(cars_data, json_file, indent=4, ensure_ascii=False)

print("JSON с машинами и их ценами успешно создан.")
