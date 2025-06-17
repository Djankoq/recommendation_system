from pymongo import MongoClient


class User:
    users_collection = None
    positions_collection = None

    @staticmethod
    def add_user(user_dict):
        '''Добавляет нового пользователя'''
        required_fields = {'name', 'like_categories', 'dislike_categories', 'viewed'}
        if not required_fields.issubset(user_dict):
            return {'error': 'Отсутствуют обязательные поля'}, 400

        if not isinstance(user_dict['name'], str):
            return {'error': 'Неверный тип для имени'}, 400

        if "id" not in user_dict or user_dict["id"] is None:
            user_dict["id"] = User.get_uniq_id()
        else:
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
        '''Возвращает пользователя по id'''
        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")
        user.pop('_id', None)
        return user

    @staticmethod
    def add_like_to_user(user_id, position_id):
        '''Добавляет пользователю понравившеюся категорию выбранного фильма'''
        pos = User.positions_collection.find_one({"id": position_id}) or \
              User.positions_collection.find_one({"id": str(position_id)})
        if not pos:
            raise ValueError("Позиция не найдена")
        tags = pos.get("tag", [])

        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")

        like_categories = set(user.get("like_categories", []))
        dislike_categories = set(user.get("dislike_categories", []))

        to_add = [tag for tag in tags if tag not in like_categories and tag not in dislike_categories]

        if to_add:
            User.users_collection.update_one(
                {"id": user_id},
                {"$addToSet": {"like_categories": {"$each": to_add}}}
            )

    @staticmethod
    def add_dislike_to_user(user_id, position_id):
        '''Добавляет пользователю непонравившеюся категорию выбранного фильма'''
        pos = User.positions_collection.find_one({"id": position_id}) or \
              User.positions_collection.find_one({"id": str(position_id)})
        if not pos:
            raise ValueError("Позиция не найдена")
        categories = pos.get("categories", [])

        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")

        like_categories = set(user.get("like_categories", []))
        dislike_categories = set(user.get("dislike_categories", []))

        to_add = [cat for cat in categories if cat not in like_categories and cat not in dislike_categories]

        if to_add:
            User.users_collection.update_one(
                {"id": user_id},
                {"$addToSet": {"dislike_categories": {"$each": to_add}}}
            )

    @staticmethod
    def add_viewed_item(user_id, item_id):
        '''Добавляет пользователю id просмотренного фильма'''
        pos = User.positions_collection.find_one({"id": item_id}) or \
              User.positions_collection.find_one({"id": str(item_id)})
        if not pos:
            raise ValueError("Позиция не найдена")

        user = User.users_collection.find_one({"id": user_id})
        if not user:
            raise ValueError(f"Пользователь с id {user_id} не найден")

        if item_id in user.get("viewed", []):
            raise ValueError(f"Позиция {item_id} уже была добавлена")

        User.users_collection.update_one(
            {"id": user_id},
            {"$addToSet": {"viewed": item_id}}
        )


if User.users_collection is None:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["recommendation_system"]
    User.users_collection = db["users"]
    User.positions_collection = db["positions"]
