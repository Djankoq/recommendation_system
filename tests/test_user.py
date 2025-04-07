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
                "dislike_categories": ["politics"]
            },
            {
                "id": 2,
                "name": "Bob",
                "like_categories": ["travel", "reading"],
                "dislike_categories": ["fast food"]
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
        users = User.read_file()
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].name, "Alice")
        self.assertEqual(users[1].likes, ["travel", "reading"])

        # Тестируем обработку FileNotFoundError
        with patch("user.user.User.FILE_PATH", "./non_existent_file.json"):
            users = User.read_file()
            self.assertEqual(users, [])  # Ожидаем, что вернется пустой список, если файл отсутствует

    def test_add_user(self):
        """Тестируем метод add_user."""
        # Считываем текущее состояние файла
        users_before = User.read_file()
        initial_count = len(users_before)

        print(initial_count)
        # Добавляем нового пользователя
        new_user = User(User.get_uniq_id(), "Charlie", ["gaming"], ["spicy food"])
        User.add_user(new_user)

        # Считываем обновлённый список пользователей
        users_after = User.read_file()

        # Проверяем, что количество пользователей увеличилось на 1
        self.assertEqual(len(users_after), initial_count + 1)

        # Проверяем, что последний пользователь — это добавленный пользователь
        last_user = users_after[-1]
        self.assertEqual(last_user.name, "Charlie")
        self.assertEqual(last_user.likes, ["gaming"])
        self.assertEqual(last_user.dislikes, ["spicy food"])

    def test_get_uniq_id(self):
        """Тестируем метод get_uniq_id."""
        uniq_id = User.get_uniq_id()
        self.assertEqual(uniq_id, 3)  # Следующий ID после существующих пользователей

    def test_get_user_by_id(self):
        """Тестируем метод get_user_by_id."""
        user = User.get_user_by_id(1)
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Alice")

        with self.assertRaises(ValueError):
            User.get_user_by_id(99)  # Проверяем, что ошибка возникает для несуществующего ID

    def test_to_dict(self):
        """Тестируем метод to_dict."""
        user = User(1, "Alice", ["sports", "music"], ["politics"])
        user_dict = user.to_dict()
        expected_dict = {
            "id": 1,
            "name": "Alice",
            "like_categories": ["sports", "music"],
            "dislike_categories": ["politics"]
        }
        self.assertEqual(user_dict, expected_dict)

    def test_str(self):
        """Тестируем метод __str__."""
        user = User(1, "Alice", ["sports", "music"], ["politics"])
        user_str = str(user)
        expected_str = "1  Alice ['sports', 'music'] ['politics']"  # Ожидаемый формат
        self.assertEqual(user_str, expected_str)

if __name__ == "__main__":
    unittest.main()
