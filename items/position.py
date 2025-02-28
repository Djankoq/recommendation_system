import json
from user.user import User


class Position:
    def __init__(self, id, name, tags):
        self.id = id
        self.name = name
        self.tags = tags

    @staticmethod
    def read_file():
        """Считывает позиции из файла и возвращает список объектов Position"""
        positions = []
        try:
            with open('./positions.json', 'r', encoding='utf-8') as f:
                content = f.read()
                temp = json.loads(content) if content else []
            for item in temp:
                position = Position(item['id'], item['position_name'], item['tag'])
                positions.append(position)
        except FileNotFoundError:
            return []
        return positions

    def __str__(self):
        return f"{self.id}  {self.name} {self.tags}"

    @staticmethod
    def get_position_by_id(id):
        """Возращает позицию по id"""
        positions = Position.read_file()
        for position in positions:
            if position.id == id:
                return position
        return "Позиция не найдена"

    @staticmethod
    def get_recommend_position(user_id):
        try:
            likes = User.get_user_by_id(user_id).likes
            dislikes = User.get_user_by_id(user_id).dislikes
            positions = Position.read_file()
            recommend_positions = []
            for position in positions:
                in_dislikes = False
                for tag in position.tags:
                    if tag in dislikes:
                        in_dislikes = True
                        break

                if not in_dislikes and tag in likes:
                    recommend_positions.append(position)

            return recommend_positions
        except TypeError:
            return "Пользователь не найден"
