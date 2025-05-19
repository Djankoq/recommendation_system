import unittest
import json
import os
from unittest.mock import patch
from items.position import Position
from user.user import User


class TestPosition(unittest.TestCase):
    TEST_POSITION_FILE_PATH = "./test_positions.json"
    TEST_USER_FILE_PATH = "./test_users.json"

    def setUp(self):
        """Этот метод выполняется перед каждым тестом."""
        # Создаем тестовый файл с позициями
        self.test_positions = [
            {"id": 1, "position_name": "Gin - Gilbeys London, Dry", "tag": ["sports"]},
            {"id": 2, "position_name": "Shrimp - 100 / 200 Cold Water", "tag": ["horror movies", "music"]}
        ]
        with open(self.TEST_POSITION_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.test_positions, f, indent=4, ensure_ascii=False)

        # Создаем тестовый файл с пользователями
        self.test_users = [
            {
                "id": 1,
                "name": "Rosalia Losebie",
                "like_categories": ["sports", "music"],
                "dislike_categories": ["fast food", "horror movies"],
                "viewed": [
                    122,
                    135,
                    640,
                    133
                ]
            },
            {
                "id": 2,
                "name": "Alexandre Moorman",
                "like_categories": ["music"],
                "dislike_categories": ["horror movies"],
                "viewed": [
                    640,
                    133
                ]
            }
        ]
        with open(self.TEST_USER_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.test_users, f, indent=4, ensure_ascii=False)

        # Переопределяем пути к файлам
        Position.FILE_PATH = self.TEST_POSITION_FILE_PATH  # Динамический путь для позиций
        User.FILE_PATH = self.TEST_USER_FILE_PATH  # Динамический путь для пользователей

    def tearDown(self):
        """Этот метод выполняется после каждого теста."""
        # Удаляем тестовые файлы
        if os.path.exists(self.TEST_POSITION_FILE_PATH):
            os.remove(self.TEST_POSITION_FILE_PATH)
        if os.path.exists(self.TEST_USER_FILE_PATH):
            os.remove(self.TEST_USER_FILE_PATH)

    def test_read_file(self):
        """Тестируем метод read_file."""
        # Тестируем нормальное чтение файла
        positions = Position.read_file()
        self.assertEqual(len(positions), 2)  # Проверяем количество позиций
        self.assertEqual(positions[0].get_name(), "Gin - Gilbeys London, Dry")  # Проверяем имя первой позиции
        self.assertEqual(positions[1].get_tags(), ["horror movies", "music"])  # Проверяем теги второй позиции

        # Тестируем обработку FileNotFoundError
        with patch("items.position.Position.FILE_PATH", "./non_existent_file.json"):  # Указываем правильный путь
            positions = Position.read_file()
            self.assertEqual(positions, [])  # Ожидаем пустой список, если файл отсутствует

    def test_get_position_by_id(self):
        """Тестируем метод get_position_by_id."""
        position = Position.get_position_by_id(1)
        self.assertIsNotNone(position)
        self.assertNotEqual(position, "Позиция не найдена")
        self.assertEqual(position.get_name(), "Gin - Gilbeys London, Dry")  # Проверка существующей позиции

        position = Position.get_position_by_id(2)
        self.assertIsNotNone(position)
        self.assertEqual(position.get_name(), "Shrimp - 100 / 200 Cold Water")  # Проверка второй позиции

        position = Position.get_position_by_id(999)  # Проверка несуществующего ID
        self.assertEqual(position, "Позиция не найдена")  # Проверка строки вместо None

    def test_get_recommend_position(self):
        """Тестируем метод get_recommend_position."""

        # Рекомендации для пользователя с id=1
        recommended_positions = Position.get_recommend_position(1)
        self.assertEqual(len(recommended_positions), 1)
        self.assertEqual(recommended_positions[0].get_name(), "Gin - Gilbeys London, Dry")

        # Рекомендации для пользователя с id=2
        recommended_positions = Position.get_recommend_position(2)
        self.assertEqual(len(recommended_positions), 0)

        # Тестируем обработку случая, когда пользователь не найден (TypeError)
        with patch("user.user.User.get_user_by_id", return_value=None):
            result = Position.get_recommend_position(99)  # ID пользователя, который не существует
            self.assertEqual(result, "Пользователь не найден")  # Ожидаем строку "Пользователь не найден"

    def test_str(self):
        """Тестируем метод __str__."""
        position = Position(1, "Developer", ["coding", "teamwork"])
        expected_str = "1  Developer ['coding', 'teamwork']"
        self.assertEqual(str(position), expected_str)

    @patch('items.position.Position.read_file')
    def test_get_category_by_position_id_success(self, mock_read_file):
        """Тестируем get_category_by_position_id - позиция найдена"""
        mock_position = Position(1, "Test Item", ["tech", "gadgets"])
        mock_read_file.return_value = [mock_position]

        result = Position.get_category_by_position_id(1)
        self.assertEqual(result, ["tech", "gadgets"])

    @patch('items.position.Position.read_file')
    def test_get_category_by_position_id_not_found(self, mock_read_file):
        """Тестируем get_category_by_position_id - позиция не найдена"""
        mock_position = Position(2, "Another Item", ["books", "education"])
        mock_read_file.return_value = [mock_position]

        result = Position.get_category_by_position_id(99)
        self.assertEqual(result, "Позиция не найдена")


if __name__ == "__main__":
    unittest.main()
