from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["recommendation_system"]  # Имя базы данных
users_collection = db["users"]
positions_collection = db["positions"]

def import_json_to_collection(json_path, collection_name):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
        # Если данные — список документов
        if isinstance(data, list):
            db[collection_name].insert_many(data)
        else:
            db[collection_name].insert_one(data)
    print(f"Данные из {json_path} импортированы в коллекцию {collection_name}")

if __name__ == "__main__":
    # Импортируем users.json и positions.json
    import_json_to_collection("users.json", "users")
    import_json_to_collection("positions.json", "positions")
