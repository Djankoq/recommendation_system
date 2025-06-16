from pymongo import MongoClient
from user.user import User

client = MongoClient("mongodb://localhost:27017/")
db = client["recommendation_service"]
positions_collection = db["positions"]
users_collection = db["users"]

class Position:
    @staticmethod
    def get_category_by_position_id(position_id):
        pos = positions_collection.find_one({"id": position_id})
        if not pos:
            return "Позиция не найдена"
        return pos.get("categories", [])

    @staticmethod
    def get_position_by_id(position_id):
        pos = positions_collection.find_one({"id": position_id})
        if not pos:
            return "Позиция не найдена"
        pos.pop('_id', None)
        return pos

    @staticmethod
    def get_recommend_position(user_id):
        try:
            user = users_collection.find_one({"id": user_id})
            if not user:
                return "Пользователь не найден"
            likes = user.get("like_categories", [])
            dislikes = user.get("dislike_categories", [])
            viewed = user.get("viewed", [])
            # Рекомендуем позиции, которые не в viewed и не содержат disliked категорий, но содержат liked
            recommend_positions = []
            for pos in positions_collection.find():
                if pos["id"] in viewed:
                    continue
                if any(tag in dislikes for tag in pos.get("categories", [])):
                    continue
                if any(tag in likes for tag in pos.get("categories", [])):
                    pos.pop('_id', None)
                    recommend_positions.append(pos)
            return recommend_positions
        except Exception as e:
            return f"Ошибка: {str(e)}"
