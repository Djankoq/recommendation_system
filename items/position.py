import json
from user.user import User


class Position:
    __FILE_PATH = "./positions.json"  # Путь к файлу по умолчанию

    def __init__(self, id, name, tags):
        self.__id = id
        self.__name = name
        self.__tags = tags

    @staticmethod
    def __read_file():
        """Считывает позиции из файла и возвращает список объектов Position"""
        positions = []
        try:
            with open(Position.__FILE_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                temp = json.loads(content) if content else []
            for item in temp:
                position = Position(item['id'], item['position_name'], item['tag'])
                positions.append(position)
        except FileNotFoundError:
            return []
        return positions

    def __str__(self):
        return f"{self.__id}  {self.__name} {self.__tags}"

    @staticmethod
    def get_position_by_id(id):
        """Возвращает позицию по id"""
        positions = Position.__read_file()
        for position in positions:
            if position.__id == id:
                return position
        return "Позиция не найдена"

    @staticmethod
    def get_recommend_position(user_id):
        try:
            likes = User.get_user_by_id(user_id)._User__likes
            dislikes = User.get_user_by_id(user_id)._User__dislikes
            viewed = User.get_user_by_id(user_id)._User__viewed
            positions = Position.__read_file()
            recommend_positions = []
            for position in positions:
                in_dislikes = False
                in_viewed = False

                if position.__id in viewed:
                    in_viewed = True

                for tag in position.__tags:
                    if tag in dislikes:
                        in_dislikes = True
                        break

                if not in_dislikes and not in_viewed and tag in likes:
                    recommend_positions.append(position)

            return recommend_positions
        except AttributeError:
            return "Пользователь не найден"
        except TypeError:
            return "Пользователь не найден"
