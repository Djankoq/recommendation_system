import json


class User:

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
            with open("./users.json", "r", encoding="utf-8") as f:
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
        with open("../users.json", "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in users], f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_uniq_id():
        """Ищет уникальный id"""
        users = User.read_file()
        id = len(users) + 1
        return id

    @staticmethod
    def get_user_by_id(id):
        """Возвращает пользователя по id"""
        users = User.read_file()
        for user in users:
            if user.id == id:
                return user

    def __str__(self):
        return f"{self.id}  {self.name} {self.likes} {self.dislikes}"

# user = User(User.get_uniq_id(), 'Test test', ['sports', 'travel'], ['fast food', 'politics'])
# User.add_user(user)
#
# users = User.read_file()
# for user in users:
#     print(user)