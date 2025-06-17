from pymongo import MongoClient
from user.user import User

client = MongoClient("mongodb://localhost:27017/")
db = client["recommendation_system"]
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
    def get_recommendations_for_user(user_id, limit=5):
        user = users_collection.find_one({"id": user_id})
        if not user:
            return "Пользователь не найден"

        viewed_ids = set(user.get('viewed', []))

        # Собираем все уникальные категории
        all_categories = set()
        for u in users_collection.find():
            all_categories.update(u.get('like_categories', []))
            all_categories.update(u.get('dislike_categories', []))
        all_categories = list(all_categories)

        def user_to_vector(user, categories):
            return [
                1 if cat in user.get('like_categories', []) else
            -1 if cat in user.get('dislike_categories', []) else
                0
                for cat in categories
            ]

        def cosine_similarity(a, b):
            dot = sum(x*y for x, y in zip(a, b))
            norm_a = sum(x**2 for x in a) ** 0.5
            norm_b = sum(y**2 for y in b) ** 0.5
            if norm_a == 0 or norm_b == 0:
                return 0
            return dot / (norm_a * norm_b)

        target_vec = user_to_vector(user, all_categories)

        # Для каждого другого пользователя считаем похожесть
        position_scores = dict()
        for other in users_collection.find({"id": {"$ne": user_id}}):
            sim = cosine_similarity(target_vec, user_to_vector(other, all_categories))
            if sim <= 0:
                continue  # не учитываем совсем непохожих

            # Для всех позиций, которые нравятся этому пользователю
            liked_cats = set(other.get('like_categories', []))
            for pos in positions_collection.find({"tag": {"$in": list(liked_cats)}, "id": {"$nin": list(viewed_ids)}}):
                pid = pos['id']
                position_scores[pid] = position_scores.get(pid, 0) + sim

        # Сортируем позиции по убыванию "рейтинга"
        top_ids = [pid for pid, _ in sorted(position_scores.items(), key=lambda x: x[1], reverse=True)][:limit]

        recommended = list(positions_collection.find({"id": {"$in": top_ids}}))
        for rec in recommended:
            rec.pop('_id', None)
        # Можно отсортировать вручную по top_ids, если порядок важен
        recommended.sort(key=lambda r: top_ids.index(r['id']))
        return recommended

