import unittest
from pymongo import MongoClient
from user.user import User


class TestUserMongo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''Подготовка места хранения тестовых данных'''
        cls.client = MongoClient("mongodb://localhost:27017/")
        cls.db = cls.client["recommendation_system_test"]
        cls.users = cls.db["users"]
        cls.positions = cls.db["positions"]
        User.users_collection = cls.users
        User.positions_collection = cls.positions

    def setUp(self):
        '''Подготовка тестовых данных'''
        self.users.delete_many({})
        self.positions.delete_many({})
        self.users.insert_many([
            {"id": 1, "name": "Alice", "like_categories": ["sports"], "dislike_categories": [], "viewed": [101]},
            {"id": 2, "name": "Bob", "like_categories": ["music"], "dislike_categories": ["horror"], "viewed": []},
            {"id": 3, "name": "Charlie", "like_categories": [], "dislike_categories": [], "viewed": []}
        ])
        self.positions.insert_many([
            {"id": 101, "position_name": "Football", "tag": ["sports"], "categories": ["sports"]},
            {"id": 102, "position_name": "Concert Ticket", "tag": ["music"], "categories": ["music"]},
            {"id": 103, "position_name": "Scary Movie", "tag": ["horror", "movies"],
             "categories": ["horror", "movies"]},
            {"id": 104, "position_name": "Travel Guide", "tag": ["travel"], "categories": ["travel"]}
        ])

    def tearDown(self):
        '''Очищаем коллекции после каждого теста'''
        self.users.delete_many({})
        self.positions.delete_many({})

    @classmethod
    def tearDownClass(cls):
        '''Очищаем коллекции и закрываем соединение после всех тестов'''
        cls.client.drop_database("recommendation_system_test")
        cls.client.close()

    def test_add_user_success(self):
        '''Позитивный тест: добавление пользователя'''
        user_dict = {"name": "David", "like_categories": ["cooking"], "dislike_categories": [], "viewed": []}
        resp, code = User.add_user(user_dict)
        self.assertEqual(code, 201)
        self.assertEqual(resp["message"], "Пользователь создан")
        found = self.users.find_one({"id": resp["id"]})
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "David")

    def test_add_user_missing_fields(self):
        '''Негативный тест: добавление пользователя без некоторых полей'''
        user_dict = {"name": "Eve"}
        resp, code = User.add_user(user_dict)
        self.assertEqual(code, 400)
        self.assertIn("error", resp)

    def test_add_user_duplicate_id(self):
        '''Негативный тест: добавление пользователя с существующем id'''
        user_dict = {"id": 1, "name": "Eve", "like_categories": [], "dislike_categories": [], "viewed": []}
        resp, code = User.add_user(user_dict)
        self.assertEqual(code, 400)
        self.assertIn("Пользователь уже существует", resp["error"])

    def test_add_user_wrong_name_type(self):
        '''Негативный тест: создание пользователя с неверным типом имени'''
        user_dict = {"name": 123, "like_categories": [], "dislike_categories": [], "viewed": []}
        resp, code = User.add_user(user_dict)
        self.assertEqual(code, 400)
        self.assertIn("Неверный тип для имени", resp["error"])

    def test_get_user_by_id_success(self):
        '''Позитивный тест: поиск пользователя по id'''
        user = User.get_user_by_id(1)
        self.assertEqual(user["name"], "Alice")
        self.assertEqual(user["like_categories"], ["sports"])

    def test_get_user_by_id_not_found(self):
        '''Позитивный тест: поиск пользователя по несуществующему id'''
        with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
            User.get_user_by_id(999)

    def test_get_uniq_id(self):
        '''Позитивный тест: получение уникального id для пользователя'''
        uniq_id = User.get_uniq_id()
        self.assertEqual(uniq_id, 4)
        User.add_user({"name": "Eve", "like_categories": [], "dislike_categories": [], "viewed": []})
        self.assertEqual(User.get_uniq_id(), 5)

    def test_add_like_to_user_success(self):
        '''Позитивный тест: добавление пользователю лайка для выбранного фильма'''
        User.add_like_to_user(1, 104)
        updated = self.users.find_one({"id": 1})
        self.assertIn("travel", updated["like_categories"])
        self.assertEqual(len(updated["like_categories"]), 2)

    def test_add_like_to_user_position_not_found(self):
        '''Негативный тест: добавление пользователю лайка для несуществующего фильма'''
        with self.assertRaisesRegex(ValueError, "Позиция не найдена"):
            User.add_like_to_user(1, 999)

    def test_add_like_to_user_user_not_found(self):
        '''Негативный тест: добавление лайка несуществующему пользователю'''
        with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
            User.add_like_to_user(999, 101)

    def test_add_like_to_user_category_already_liked_or_disliked(self):
        '''Позитивный тест: добавление лайка и дизлайка для фильмом чьи категорию уже были отмечены пользователем'''
        User.add_like_to_user(1, 101)
        updated_alice = self.users.find_one({"id": 1})
        self.assertEqual(updated_alice["like_categories"], ["sports"])
        User.add_like_to_user(2, 103)
        updated_bob = self.users.find_one({"id": 2})
        self.assertNotIn("horror", updated_bob["like_categories"])
        self.assertIn("horror", updated_bob["dislike_categories"])

    def test_add_dislike_to_user_success(self):
        '''Позитивный тест: добавление дизлайку пользователю для выбранного фильма'''
        User.add_dislike_to_user(2, 104)
        updated = self.users.find_one({"id": 2})
        self.assertIn("travel", updated["dislike_categories"])
        self.assertEqual(len(updated["dislike_categories"]), 2)

    def test_add_dislike_to_user_position_not_found(self):
        '''Негативный тест: добавление пользователю дизлайка для несущесвтвующего фильма'''
        with self.assertRaisesRegex(ValueError, "Позиция не найдена"):
            User.add_dislike_to_user(1, 999)

    def test_add_dislike_to_user_user_not_found(self):
        '''Негативный тест: добавление несуществующему пользователю дизлайка'''
        with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
            User.add_dislike_to_user(999, 101)

    def test_add_viewed_item_success(self):
        '''Позитивный тест: добавление пользователю просмотренного фильма'''
        User.add_viewed_item(2, 104)
        updated = self.users.find_one({"id": 2})
        self.assertIn(104, updated["viewed"])
        self.assertEqual(len(updated["viewed"]), 1)

    def test_add_viewed_item_position_not_found(self):
        '''Негативный тест: добавление пользователю в просмотренные несущесвующего фильма'''
        with self.assertRaisesRegex(ValueError, "Позиция не найдена"):
            User.add_viewed_item(1, 999)

    def test_add_viewed_item_user_not_found(self):
        '''Негативный тест: добавление несуществующему пользователю в просмотренные фильма'''
        with self.assertRaisesRegex(ValueError, "Пользователь с id 999 не найден"):
            User.add_viewed_item(999, 101)

    def test_add_viewed_item_already_viewed(self):
        '''Негативный тест: добавление уже просмотренного фильма'''
        with self.assertRaisesRegex(ValueError, "Позиция 101 уже была добавлена"):
            User.add_viewed_item(1, 101)


if __name__ == "__main__":
    unittest.main()
