import unittest
from pymongo import MongoClient
from unittest.mock import patch
from items.position import Position
from user.user import User


class TestPosition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''Подготовка места хранения тестовых данных'''
        cls.client = MongoClient("mongodb://localhost:27017/")
        cls.db = cls.client["recommendation_system_test"]
        cls.users = cls.db["users"]
        cls.positions = cls.db["positions"]

        Position.positions_collection = cls.positions
        Position.users_collection = cls.users
        User.users_collection = cls.users
        User.positions_collection = cls.positions

    def setUp(self):
        '''Подготовка тестовых данных'''
        self.positions.delete_many({})
        self.users.delete_many({})

        self.positions.insert_many([
            {"id": 1, "position_name": "Gin - Gilbeys London, Dry", "tag": ["sports"], "categories": ["sports"]},
            {"id": 2, "position_name": "Shrimp - 100 / 200 Cold Water", "tag": ["horror movies", "music"],
             "categories": ["horror movies", "music"]}
        ])
        self.users.insert_many([
            {
                "id": 1,
                "name": "Rosalia Losebie",
                "like_categories": ["sports", "music"],
                "dislike_categories": ["fast food", "horror movies"],
                "viewed": [122, 135, 640, 133]
            },
            {
                "id": 2,
                "name": "Alexandre Moorman",
                "like_categories": ["music"],
                "dislike_categories": ["horror movies"],
                "viewed": [1, 2, 640, 133]
            }
        ])

    def tearDown(self):
        '''Очищаем коллекции после каждого теста'''
        self.positions.delete_many({})
        self.users.delete_many({})

    @classmethod
    def tearDownClass(cls):
        '''Очищаем коллекции и закрываем соединение после всех тестов'''
        cls.positions.delete_many({})
        cls.users.delete_many({})
        cls.client.close()

    def test_get_category_by_position_id_success(self):
        '''Позитивный тест: получение категорий фильма по id'''
        result = Position.get_category_by_position_id(1)
        self.assertEqual(result, ["sports"])

    def test_get_category_by_position_id_not_found(self):
        '''Негативный тест: поиск категорий несуществующего фильма'''
        result = Position.get_category_by_position_id(999)
        self.assertEqual(result, "Позиция не найдена")

    def test_get_position_by_id_success(self):
        '''Позитивный тест: получение фильма по id'''
        pos = Position.get_position_by_id(1)
        self.assertIsInstance(pos, dict)
        self.assertEqual(pos["position_name"], "Gin - Gilbeys London, Dry")

    def test_get_position_by_id_not_found(self):
        '''Негативный тест: поиск несуществующего фильма'''
        pos = Position.get_position_by_id(999)
        self.assertEqual(pos, "Позиция не найдена")

    def test_get_recommendations_for_user(self):
        '''Позитивный тест: получение рекомендации для указанного пользователя'''
        recs = Position.get_recommendations_for_user(1)
        self.assertIsInstance(recs, list)
        if recs:
            self.assertIn("id", recs[0])
        recs = Position.get_recommendations_for_user(999)
        self.assertEqual(recs, "Пользователь не найден")

    def test_get_recommendations_for_user_no_results(self):
        '''Негативный тест: для пользователя 2 не должно быть рекомендаций (все просмотрено/не совпадает)'''
        recs = Position.get_recommendations_for_user(2)
        self.assertIsInstance(recs, list)
        self.assertEqual(len(recs), 0)

    def test_get_recommendations_for_user_user_not_found(self):
        '''Негативный тест: получение рекомендация для указанного пользователя'''
        recs = Position.get_recommendations_for_user(123456)
        self.assertEqual(recs, "Пользователь не найден")

    def test_str(self):
        '''Позитивный тест: проверка переопределенного метода __str__'''
        p = Position()
        p.id = 1
        p.position_name = "Developer"
        p.tag = ["coding", "teamwork"]
        expected = "1  Developer ['coding', 'teamwork']"
        self.assertEqual(str(p), expected)

    @patch('items.position.Position.positions_collection')
    def test_get_category_by_position_id_mocked(self, mock_positions):
        '''Позитивный тест: проверяем работу при мокнутой коллекции (например, если нужно тестировать без БД)'''
        mock_positions.find_one.return_value = {"id": 1, "categories": ["tech", "gadgets"]}
        result = Position.get_category_by_position_id(1)
        self.assertEqual(result, ["tech", "gadgets"])

    @patch('items.position.Position.positions_collection')
    def test_get_category_by_position_id_not_found_mocked(self, mock_positions):
        '''Негативный тест: поиск фильма при немокнутых данных'''
        mock_positions.find_one.return_value = None
        result = Position.get_category_by_position_id(99)
        self.assertEqual(result, "Позиция не найдена")


if __name__ == "__main__":
    unittest.main()
