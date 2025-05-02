import unittest
import json
import os
from unittest.mock import patch
from user.user import User  # Импортируем ваш класс User


class TestUser(unittest.TestCase):
    TEST_FILE_PATH = "./test_users.json"

    def setUp(self):
        """Этот метод выполняется перед каждым тестом."""
        # Создаем тестовый файл с пользователями
        self.test_users = [
            {
                "id": 1,
                "name": "Alice",
                "like_categories": ["sports", "music"],
                "dislike_categories": ["politics"],
                "viewed": [122]
            },
            {
                "id": 2,
                "name": "Bob",
                "like_categories": ["travel", "reading"],
                "dislike_categories": ["fast food"],
                "viewed": [359, 860]
            }
        ]
        with open(self.TEST_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.test_users, f, indent=4, ensure_ascii=False)

        # Переопределяем путь к файлу в классе User
        User.FILE_PATH = self.TEST_FILE_PATH  # Используем временный файл

    def tearDown(self):
        """Этот метод выполняется после каждого теста."""
        # Удаляем тестовый файл
        if os.path.exists(self.TEST_FILE_PATH):
            os.remove(self.TEST_FILE_PATH)

    def test_read_file(self):
        """Тестируем метод read_file."""
        # Тестируем нормальное чтение файла
        users = User._User__read_file()
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].get_name(), "Alice")
        self.assertEqual(users[1].get_likes(), ["travel", "reading"])

        # Тестируем обработку FileNotFoundError
        with patch("user.user.User.FILE_PATH", "./non_existent_file.json"):
            users = User._User__read_file()
            self.assertEqual(users, [])  # Ожидаем, что вернется пустой список, если файл отсутствует

    def test_add_user(self):
        """Тестируем метод add_user."""
        # Считываем текущее состояние файла
        users_before = User._User__read_file()
        initial_count = len(users_before)

        print(initial_count)
        # Добавляем нового пользователя
        new_user = User(User.get_uniq_id(), "Charlie", ["gaming"], ["spicy food"], [43])
        User.add_user(new_user)

        # Считываем обновлённый список пользователей
        users_after = User._User__read_file()

        # Проверяем, что количество пользователей увеличилось на 1
        self.assertEqual(len(users_after), initial_count + 1)

        # Проверяем, что последний пользователь — это добавленный пользователь
        last_user = users_after[-1]
        self.assertEqual(last_user.get_name(), "Charlie")
        self.assertEqual(last_user.get_likes(), ["gaming"])
        self.assertEqual(last_user.get_dislikes(), ["spicy food"])
        self.assertEqual(last_user.get_viewed(), [43])

    def test_get_uniq_id(self):
        """Тестируем метод get_uniq_id."""
        uniq_id = User.get_uniq_id()
        self.assertEqual(uniq_id, len(User._User__read_file()) + 1)  # Следующий ID после существующих пользователей

    def test_get_user_by_id(self):
        """Тестируем метод get_user_by_id."""
        user = User.get_user_by_id(1)
        self.assertIsNotNone(user)
        self.assertEqual(user.get_name(), User._User__read_file()[0].get_name())

        with self.assertRaises(ValueError):
            User.get_user_by_id(99)  # Проверяем, что ошибка возникает для несуществующего ID

    def test_to_dict(self):
        """Тестируем метод to_dict."""
        user = User(1, "Alice", ["sports", "music"], ["politics"], [22])
        user_dict = user._User__to_dict()
        expected_dict = {
            "id": 1,
            "name": "Alice",
            "like_categories": ["sports", "music"],
            "dislike_categories": ["politics"],
            "viewed": [22]
        }
        self.assertEqual(user_dict, expected_dict)

    def test_str(self):
        """Тестируем метод __str__."""
        user = User(1, "Alice", ["sports", "music"], ["politics"], [22])
        user_str = str(user)
        expected_str = "1  Alice ['sports', 'music'] ['politics'] [22]"  # Ожидаемый формат
        self.assertEqual(user_str, expected_str)

    @patch('items.position.Position.get_position_by_id')
    def test_add_viewed_item_success(self, mock_get_position):
        """Тестируем методм add_viewed_item - положительный сценарий"""
        mock_get_position.return_value = {
            "id": 122,
            "position_name": "MaxiGear Chair",
            "tag": [
                "politics",
                "music"
            ]
        }

        User.add_viewed_item(1, 42)
        self.assertEqual(User.get_user_by_id(1).get_viewed(), [122, 42])

    @patch('items.position.Position.get_position_by_id')
    def test_add_viewed_item_already_added(self, mock_get_position):
        """Тестируем методм add_viewed_item - Позиция уже была добавлена"""
        mock_get_position.return_value = {
            "id": 122,
            "position_name": "MaxiGear Chair",
            "tag": [
                "politics",
                "music"
            ]
        }

        with self.assertRaises(ValueError) as context:
            User.add_viewed_item(1, 122)

        self.assertEqual(str(context.exception), "Позиция 122 уже была добавлена")

    def test_add_viewed_item_position_doesnt_exist(self):
        """Тестируем методм add_viewed_item - Позиция не существуют"""
        with self.assertRaises(ValueError) as context:
            User.add_viewed_item(1, 55)

        self.assertEqual(str(context.exception), "Позиция не найдена")

    @patch('items.position.Position.get_position_by_id')
    def test_add_viewed_item_user_not_found(self, mock_get_position):
        """Тестируем методм add_viewed_item - Пользователь не существуют"""
        mock_get_position.return_value = {
            "id": 122,
            "position_name": "MaxiGear Chair",
            "tag": [
                "politics",
                "music"
            ]
        }

        with self.assertRaises(ValueError) as context:
            User.add_viewed_item(445, 55)

        self.assertEqual(str(context.exception), "Пользователь с id 445 не найден")


if __name__ == "__main__":
    unittest.main()
