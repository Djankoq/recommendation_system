import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
from user.user import User
from items.position import Position


class TestUser(unittest.TestCase):
    TEST_USER_FILE_PATH = "./test_users.json"
    TEST_POSITION_FILE_PATH = "./test_positions.json"

    def setUp(self):
        """Настройка перед каждым тестом: создание тестовых файлов."""
        self.initial_users_data = [
            {"id": 1, "name": "Alice", "like_categories": ["sports"], "dislike_categories": [], "viewed": [101]},
            {"id": 2, "name": "Bob", "like_categories": ["music"], "dislike_categories": ["horror"], "viewed": []},
            {"id": 3, "name": "Charlie", "like_categories": [], "dislike_categories": [], "viewed": []}
        ]
        with open(self.TEST_USER_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.initial_users_data, f, indent=4, ensure_ascii=False)

        self.test_positions_data = [
            {"id": 101, "position_name": "Football", "tag": ["sports"]},
            {"id": 102, "position_name": "Concert Ticket", "tag": ["music"]},
            {"id": 103, "position_name": "Scary Movie", "tag": ["horror", "movies"]},
            {"id": 104, "position_name": "Travel Guide", "tag": ["travel"]}
        ]
        with open(self.TEST_POSITION_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.test_positions_data, f, indent=4, ensure_ascii=False)

        User.FILE_PATH = self.TEST_USER_FILE_PATH
        Position.FILE_PATH = self.TEST_POSITION_FILE_PATH

    def tearDown(self):
        """Удаление тестовых файлов после каждого теста."""
        if os.path.exists(self.TEST_USER_FILE_PATH):
            os.remove(self.TEST_USER_FILE_PATH)
        if os.path.exists(self.TEST_POSITION_FILE_PATH):
            os.remove(self.TEST_POSITION_FILE_PATH)


    def test_user_initialization_and_getters(self):
        """Позитивный тест: Проверка корректной инициализации User и геттеров."""
        user = User(1, "Test User", ["coding"], ["bugs"], [1, 2, 3])
        self.assertEqual(user.get_id(), 1)
        self.assertEqual(user.get_name(), "Test User")
        self.assertEqual(user.get_likes(), ["coding"])
        self.assertEqual(user.get_dislikes(), ["bugs"])
        self.assertEqual(user.get_viewed(), [1, 2, 3])

    def test_to_dict(self):
        """Позитивный тест: Проверка метода __to_dict__."""
        user = User(1, "Test User", ["coding"], ["bugs"], [1, 2, 3])
        expected_dict = {
            "id": 1,
            "name": "Test User",
            "like_categories": ["coding"],
            "dislike_categories": ["bugs"],
            "viewed": [1, 2, 3]
        }
        self.assertEqual(user._User__to_dict(), expected_dict)

    def test_read_file_existing_users(self):
        """Позитивный тест: Чтение пользователей из существующего файла."""
        users = User._User__read_file()
        self.assertEqual(len(users), 3)
        self.assertEqual(users[0].get_name(), "Alice")
        self.assertEqual(users[1].get_likes(), ["music"])

    def test_read_file_empty_file(self):
        """Позитивный тест: Чтение из пустого файла."""
        os.remove(self.TEST_USER_FILE_PATH)
        with open(self.TEST_USER_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("")
        users = User._User__read_file()
        self.assertEqual(users, [])

    def test_add_user_success(self):
        """Позитивный тест: Успешное добавление нового пользователя."""
        new_user = User(4, "David", ["cooking"], [], [])
        User.add_user(new_user)
        users = User._User__read_file()
        self.assertEqual(len(users), 4)
        self.assertEqual(users[3].get_name(), "David")
        self.assertEqual(users[3].get_id(), 4)

    def test_get_uniq_id_success(self):
        """Позитивный тест: Получение уникального ID."""
        uniq_id = User.get_uniq_id()
        self.assertEqual(uniq_id, 4)

        new_user = User(4, "David", [], [], [])
        User.add_user(new_user)
        self.assertEqual(User.get_uniq_id(), 5)

    @patch('items.position.Position.get_position_by_id')
    @patch('items.position.Position.get_category_by_position_id')
    def test_add_like_to_user_success(self, mock_get_category, mock_get_position):
        """Позитивный тест: Успешное добавление лайка пользователю."""
        mock_get_position.return_value = Position(104, "Travel Guide", ["travel"])
        mock_get_category.return_value = ["travel"]

        User.add_like_to_user(1, 104)
        updated_user = User.get_user_by_id(1)
        self.assertIn("travel", updated_user.get_likes())
        self.assertEqual(len(updated_user.get_likes()), 2)

    @patch('items.position.Position.get_position_by_id')
    @patch('items.position.Position.get_category_by_position_id')
    def test_add_dislike_to_user_success(self, mock_get_category, mock_get_position):
        """Позитивный тест: Успешное добавление дизлайка пользователю."""
        mock_get_position.return_value = Position(104, "Travel Guide", ["travel"])
        mock_get_category.return_value = ["travel"]

        User.add_dislike_to_user(2, 104)
        updated_user = User.get_user_by_id(2)
        self.assertIn("travel", updated_user.get_dislikes())
        self.assertEqual(len(updated_user.get_dislikes()), 2)

    @patch('items.position.Position.get_position_by_id')
    def test_add_viewed_item_success(self, mock_get_position):
        """Позитивный тест: Успешное добавление просмотренного элемента."""
        mock_get_position.return_value = Position(104, "Travel Guide", ["travel"])

        User.add_viewed_item(2, 104)
        updated_user = User.get_user_by_id(2)
        self.assertIn(104, updated_user.get_viewed())
        self.assertEqual(len(updated_user.get_viewed()), 1)

    def test_get_user_by_id_success(self):
        """Позитивный тест: Получение существующего пользователя по ID."""
        user = User.get_user_by_id(1)
        self.assertEqual(user.get_name(), "Alice")
        self.assertEqual(user.get_likes(), ["sports"])

    def test_str_representation(self):
        """Позитивный тест: Проверка метода __str__."""
        user = User(99, "Test User", ["test_like"], ["test_dislike"], [500])
        expected_str = "99  Test User ['test_like'] ['test_dislike'] [500]"
        self.assertEqual(str(user), expected_str)

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_read_file_not_found(self, mock_open):
        """Негативный тест: Обработка отсутствия файла при чтении."""
        users = User._User__read_file()
        self.assertEqual(users, [])

    def test_get_user_by_id_not_found(self):
        """Негативный тест: Попытка получить несуществующего пользователя."""
        with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
            User.get_user_by_id(999)

    @patch('items.position.Position.get_position_by_id', return_value="Позиция не найдена")
    def test_add_like_to_user_position_not_found(self, mock_get_position):
        """Негативный тест: Добавление лайка с несуществующей позицией."""
        with self.assertRaisesRegex(ValueError, "Позиция не найдена"):
            User.add_like_to_user(1, 999)

    def test_add_like_to_user_user_not_found(self):
        """Негативный тест: Добавление лайка несуществующему пользователю."""
        with patch('items.position.Position.get_position_by_id', return_value=Position(101, "Test", ["test_cat"])):
            with patch('items.position.Position.get_category_by_position_id', return_value=["test_cat"]):
                with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
                    User.add_like_to_user(999, 101)

    @patch('items.position.Position.get_position_by_id')
    @patch('items.position.Position.get_category_by_position_id')
    def test_add_like_to_user_category_already_liked_or_disliked(self, mock_get_category, mock_get_position):
        """Негативный тест: Попытка добавить лайк, если категория уже есть в лайках/дизлайках."""
        mock_get_position.return_value = Position(101, "Football", ["sports"])
        mock_get_category.return_value = ["sports"]

        User.add_like_to_user(1, 101)
        updated_user = User.get_user_by_id(1)
        self.assertEqual(updated_user.get_likes(), ["sports"])
        self.assertEqual(len(updated_user.get_likes()), 1)

        mock_get_position.return_value = Position(103, "Scary Movie", ["horror"])
        mock_get_category.return_value = ["horror"]
        User.add_like_to_user(2, 103)
        updated_user_bob = User.get_user_by_id(2)
        self.assertNotIn("horror", updated_user_bob.get_likes())
        self.assertIn("horror", updated_user_bob.get_dislikes())

    @patch('items.position.Position.get_position_by_id', return_value="Позиция не найдена")
    def test_add_dislike_to_user_position_not_found(self, mock_get_position):
        """Негативный тест: Добавление дизлайка с несуществующей позицией."""
        with self.assertRaisesRegex(ValueError, "Позиция не найдена"):
            User.add_dislike_to_user(1, 999)

    def test_add_dislike_to_user_user_not_found(self):
        """Негативный тест: Добавление дизлайка несуществующему пользователю."""
        with patch('items.position.Position.get_position_by_id', return_value=Position(101, "Test", ["test_cat"])):
            with patch('items.position.Position.get_category_by_position_id', return_value=["test_cat"]):
                with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
                    User.add_dislike_to_user(999, 101)

    @patch('items.position.Position.get_position_by_id', return_value="Позиция не найдена")
    def test_add_viewed_item_position_not_found(self, mock_get_position):
        """Негативный тест: Добавление просмотренного элемента с несуществующей позицией."""
        with self.assertRaisesRegex(ValueError, "Позиция не найдена"):
            User.add_viewed_item(1, 999)

    def test_add_viewed_item_user_not_found(self):
        """Негативный тест: Добавление просмотренного элемента несуществующему пользователю."""
        with patch('items.position.Position.get_position_by_id', return_value=Position(101, "Test", ["test_cat"])):
            with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
                User.add_viewed_item(999, 101)

    @patch('items.position.Position.get_position_by_id')
    def test_add_viewed_item_already_viewed(self, mock_get_position):
        """Негативный тест: Попытка добавить уже просмотренный элемент."""
        mock_get_position.return_value = Position(101, "Football", ["sports"])
        with self.assertRaisesRegex(ValueError, "Позиция 101 уже была добавлена"):
            User.add_viewed_item(1, 101)


if __name__ == '__main__':
    unittest.main()
