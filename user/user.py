import json


class User:
    FILE_PATH = "./users.json"

    def __init__(self, id, name, likes, dislikes):
        self.id = id
        self.name = name
        self.likes = likes
        self.dislikes = dislikes

    def to_dict(self):
        """Конвертирует объект User в словарь для сериализации в JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "like_categories": self.likes,
            "dislike_categories": self.dislikes,
        }

    @staticmethod
    def read_file():
        """Считывает пользователей из файла и возвращает список объектов User"""
        users = []
        try:
            with open(User.FILE_PATH, "r", encoding="utf-8") as f:  # Используем динамический путь
                content = f.read()
                temp = json.loads(content) if content else []
            for item in temp:
                user = User(item["id"], item["name"], item["like_categories"], item["dislike_categories"])
                users.append(user)
        except FileNotFoundError:
            return []
        return users


    @staticmethod
    def add_user(user):
        """Добавляет нового пользователя в файл users.json"""
        users = User.read_file()
        users.append(user)
        with open(User.FILE_PATH, "w", encoding="utf-8") as f:  # Используем динамический путь к файлу
            json.dump([u.to_dict() for u in users], f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_uniq_id():
        """Ищет уникальный id"""
        users = User.read_file()
        existing_ids = {user.id for user in users}
new_id = 1
while new_id in existing_ids:
    new_id += 1
return new_id


    @staticmethod
    def get_user_by_id(id):
        """Возвращает пользователя по id"""
        users = User.read_file()
        for user in users:
            if user.id == id:
                return user
        raise ValueError(f"Пользователь с id {id} не найден")

    def __str__(self):
        return f"{self.id}  {self.name} {self.likes} {self.dislikes}"
