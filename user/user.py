import json


class User:
    __FILE_PATH = "./users.json"  # Приватный атрибут для хранения пути к файлу

    def __init__(self, id, name, likes, dislikes, viewed):
        self.__id = id  # Приватные атрибуты экземпляра
        self.__name = name
        self.__likes = likes
        self.__dislikes = dislikes
        self.__viewed = viewed

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
            with open(User.__FILE_PATH, "r", encoding="utf-8") as f:
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
        with open(User.__FILE_PATH, "w", encoding="utf-8") as f:
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
    def get_user_by_id(id):
        """Возвращает пользователя по id"""
        users = User.__read_file()
        for user in users:
            if user.__id == id:
                return user
        raise ValueError(f"Пользователь с id {id} не найден")

    def __str__(self):
        return f"{self.__id}  {self.__name} {self.__likes} {self.__dislikes} {self.__viewed}"
