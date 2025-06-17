from pymongo import MongoClient

class User:
    users_collection = None
    positions_collection = None

    @staticmethod
    def add_user(user_dict):
        # Проверить обязательные поля кроме id
        required_fields = {'name', 'like_categories', 'dislike_categories', 'viewed'}
        if not required_fields.issubset(user_dict):
            return {'error': 'Отсутствуют обязательные поля'}, 400

        # name должен быть строкой
        if not isinstance(user_dict['name'], str):
            return {'error': 'Неверный тип для имени'}, 400

        # id: если нет — сгенерировать
        if "id" not in user_dict or user_dict["id"] is None:
            user_dict["id"] = User.get_uniq_id()
        else:
            # Проверить уникальность
            if User.users_collection.find_one({"id": user_dict["id"]}):
                return {'error': 'Пользователь уже существует'}, 400

        User.users_collection.insert_one(user_dict)
        return {'message': 'Пользователь создан', 'id': user_dict["id"]}, 201
    
    @staticmethod
    def get_uniq_id():
        """Ищет уникальный id (максимальный + 1)"""
        last = User.users_collection.find_one(sort=[("id", -1)])
        return (last["id"] + 1) if last else 1

    @staticmethod
    def get_user_by_id(user_id):
        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")
        user.pop('_id', None)
        return user

    @staticmethod
    def add_like_to_user(user_id, position_id):
        # Найти позицию по id
        pos = User.positions_collection.find_one({"id": position_id}) or \
            User.positions_collection.find_one({"id": str(position_id)})
        if not pos:
            raise ValueError("Позиция не найдена")
        tags = pos.get("tag", [])

        # Получить пользователя
        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")

        like_categories = set(user.get("like_categories", []))
        dislike_categories = set(user.get("dislike_categories", []))

        # Собрать новые категории для лайка (только если их нет ни в like, ни в dislike)
        to_add = [tag for tag in tags if tag not in like_categories and tag not in dislike_categories]

        if to_add:
            User.users_collection.update_one(
                {"id": user_id},
                {"$addToSet": {"like_categories": {"$each": to_add}}}
            )

    @staticmethod
    def add_dislike_to_user(user_id, position_id):
        # Найти позицию по id (учитываем int и str)
        pos = User.positions_collection.find_one({"id": position_id}) or \
            User.positions_collection.find_one({"id": str(position_id)})
        if not pos:
            raise ValueError("Позиция не найдена")
        categories = pos.get("categories", [])

        # Получить пользователя
        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")

        like_categories = set(user.get("like_categories", []))
        dislike_categories = set(user.get("dislike_categories", []))

        # Оставляем только те категории, которых нет ни в like, ни в dislike
        to_add = [cat for cat in categories if cat not in like_categories and cat not in dislike_categories]

        if to_add:
            User.users_collection.update_one(
                {"id": user_id},
                {"$addToSet": {"dislike_categories": {"$each": to_add}}}
            )

    @staticmethod
    def add_viewed_item(user_id, item_id):
        # Проверяем, что позиция существует
        pos = User.positions_collection.find_one({"id": item_id}) or \
            User.positions_collection.find_one({"id": str(item_id)})
        if not pos:
            raise ValueError("Позиция не найдена")

        # Проверяем, что пользователь существует
        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")

        # Проверяем, что item ещё не был просмотрен
        if item_id in user.get("viewed", []):
            raise ValueError(f"Позиция {item_id} уже была добавлена")

        # Добавляем item в просмотренные
        User.users_collection.update_one(
            {"id": user_id},
            {"$addToSet": {"viewed": item_id}}
        )

# Инициализация боевых коллекций (если не подменены тестами)
if User.users_collection is None:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["recommendation_system"]
    User.users_collection = db["users"]
    User.positions_collection = db["positions"]
