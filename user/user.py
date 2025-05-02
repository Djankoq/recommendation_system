import json


class User:
    FILE_PATH = "./users.json"  # Приватный атрибут для хранения пути к файлу

    def __init__(self, id, name, likes, dislikes, viewed):
        self.__id = id  # Приватные атрибуты экземпляра
        self.__name = name
        self.__likes = likes
        self.__dislikes = dislikes
        self.__viewed = viewed

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_likes(self):
        return self.__likes

    def get_dislikes(self):
        return self.__dislikes

    def get_viewed(self):
        return self.__viewed

    def __to_dict(self):
        """Конвертирует объект User в словарь для сериализации в JSON"""
        return {
            "id": self.__id,
            "name": self.__name,
            "like_categories": self.__likes,
            "dislike_categories": self.__dislikes,
            "viewed": self.__viewed
        }

    @staticmethod
    def __read_file():
        """Считывает пользователей из файла и возвращает список объектов User"""
        users = []
        try:
            with open(User.FILE_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                temp = json.loads(content) if content else []
            for item in temp:
                user = User(item["id"], item["name"], item["like_categories"], item["dislike_categories"],
                            item["viewed"])
                users.append(user)
        except FileNotFoundError:
            return []
        return users

    @staticmethod
    def add_user(user):
        """Добавляет нового пользователя в файл users.json"""
        users = User.__read_file()
        users.append(user)
        with open(User.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([u.__to_dict() for u in users], f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_uniq_id():
        """Ищет уникальный id"""
        users = User.__read_file()
        existing_ids = {user.__id for user in users}
        new_id = 1
        while new_id in existing_ids:
            new_id += 1
        return new_id

    @staticmethod
    def add_viewed_item(user_id, item):
        """Добавляет элемент в список viewed пользователя с заданным id"""
        from items.position import Position
        if Position.get_position_by_id(item) == "Позиция не найдена":
            raise ValueError("Позиция не найдена")
        users = User.__read_file()
        found = False
        for user in users:
            if user.__id == user_id:
                if item in user.__viewed:
                    raise ValueError(f"Позиция {item} уже была добавлена")
                else:
                    user.__viewed.append(item)
                    found = True
                    break
        if not found:
            raise ValueError(f"Пользователь с id {user_id} не найден")

        with open(User.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([u.__to_dict() for u in users], f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_user_by_id(id):
        """Возвращает пользователя по id"""
        users = User.__read_file()
        for user in users:
            if user.__id == id:
                return user
        raise ValueError(f"Пользователь с id {id} не найден")

    def __str__(self):
        return f"{self.__id}  {self.__name} {self.__likes} {self.__dislikes} {self.__viewed}"
