import pytest
import requests
import threading
import time
from http.server import ThreadingHTTPServer
from pymongo import MongoClient
from httpserver import UserHandler


@pytest.fixture(scope='module')
def mongo():
    '''Фикстура для работы с тестовой MongoDB'''
    client = MongoClient("mongodb://localhost:27017/")
    db = client["recommendation_system_test"]
    users = db["users"]
    positions = db["positions"]
    yield users, positions
    users.delete_many({})
    positions.delete_many({})


@pytest.fixture(scope='module')
def http_server(mongo):
    '''Фикстура запуска HTTP-сервера'''
    from user.user import User
    from items.position import Position
    users, positions = mongo
    User.users_collection = users
    User.positions_collection = positions
    Position.users_collection = users
    Position.positions_collection = positions

    server = ThreadingHTTPServer(('localhost', 0), UserHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(0.1)
    base_url = f'http://localhost:{port}'
    yield base_url
    server.shutdown()
    thread.join()


@pytest.fixture(autouse=True)
def prepare_data(mongo):
    '''Фикстура для подготовки данных перед каждым тестом'''
    users, positions = mongo
    users.delete_many({})
    positions.delete_many({})
    positions.insert_many([
        {"id": i, "position_name": f"Movie {i}", "tag": "Test"} for i in range(1, 1001)
    ])
    users.insert_one({
        "id": 100,
        "name": "Test User 100",
        "like_categories": ["Action"],
        "dislike_categories": ["Horror"],
        "viewed": [],
        "liked": [],
        "disliked": []
    })


@pytest.fixture
def test_user():
    '''Фикстура с тестовым пользователем'''
    return {
        "id": 1002,
        "name": "Test User 1002",
        "like_categories": ["Action"],
        "dislike_categories": ["Horror"],
        "viewed": [2]
    }


def test_create_user_success(http_server, test_user):
    '''Позитивный тест: создание нового пользователя'''
    resp = requests.post(f'{http_server}/users', json=test_user)
    print(resp.json())
    assert resp.status_code == 201, f"Ожидался статус 201, получен {resp.status_code}"
    data_resp = resp.json()
    assert data_resp['message'] == 'Пользователь создан'


def test_get_user_success(http_server, test_user):
    '''Позитивный тест: получаем пользователя по id'''
    requests.post(f'{http_server}/users', json=test_user)
    new_id = test_user['id']
    resp = requests.get(f'{http_server}/users/{new_id}')
    assert resp.status_code == 200, f"Ожидался статус 200, получен {resp.status_code}"
    data = resp.json()
    assert data['id'] == new_id, f"Ожидался ID пользователя {new_id}, получен {data['id']}"
    assert data['name'] == test_user[
        'name'], f"Ожидалось имя пользователя '{test_user['name']}', получено {data['name']}"


def test_get_recommendations_success(http_server, test_user, mongo):
    '''Позитивный тест: получаем рекомендованные фильмы для пользователя'''
    users_collection, positions_collection = mongo
    positions_collection.delete_many({})
    test_positions = [
        {"id": 1, "position_name": "Test Movie 1", "tag": "Action"},
        {"id": 2, "position_name": "Test Movie 2", "tag": "Comedy"},
        {"id": 3, "position_name": "Test Movie 3", "tag": "Horror"},
    ]
    positions_collection.insert_many(test_positions)

    requests.post(f'{http_server}/users', json=test_user)
    new_id = test_user['id']

    resp = requests.get(f'{http_server}/users/{new_id}/recommendations')
    assert resp.status_code == 200, f"Ожидался статус 200, получен {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Ожидался список рекомендаций"

    expected = [pos for pos in test_positions if
                pos["tag"] in test_user["like_categories"] and pos["tag"] not in test_user["dislike_categories"]]
    assert len(data) == len(expected), f"Ожидалось {len(expected)} рекомендаций, получено {len(data)}"

    required_fields = ['id', 'position_name', 'tag']
    for item in data:
        for field in required_fields:
            assert field in item, f"Ожидалось поле '{field}' в рекомендации с ID {item.get('id')}"


def test_like_movie_success(http_server):
    '''Позитивный тест: добавляем пользователю лайк по указанном фильму'''
    user_id = 100
    movie_id = 1
    resp = requests.post(f'{http_server}/users/{user_id}/movie/{movie_id}/like')
    assert resp.status_code == 200, f"Ожидался статус 200 при лайке, получен {resp.status_code}"


def test_dislike_movie_success(http_server):
    '''Позитивный тест: добавляем пользователю дизлайк по указанном фильму'''
    user_id = 100
    movie_id = 1
    resp = requests.post(f'{http_server}/users/{user_id}/movie/{movie_id}/dislike')
    assert resp.status_code == 200, f"Ожидался статус 200 при дизлайке, получен {resp.status_code}"


def test_add_viewed_movie_success(http_server):
    '''Позитивный тест: добавляем пользователю просмотренный фильм'''
    user_id = 100
    movie_id = 3
    resp = requests.post(f'{http_server}/users/{user_id}/movie/{movie_id}/viewed')
    assert resp.status_code == 200, f"Ожидался статус 200 при добавлении в просмотренные, получен {resp.status_code}"


def test_create_user_duplicate_failure(http_server, test_user):
    '''Негативный тест: создание дубликата пользователя'''
    requests.post(f'{http_server}/users', json=test_user)
    resp_duplicate = requests.post(f'{http_server}/users', json=test_user)
    assert resp_duplicate.status_code == 400, f"Ожидался статус 400 для дубликата пользователя, получен {resp_duplicate.status_code}"
    data_duplicate = resp_duplicate.json()
    assert 'error' in data_duplicate
    assert data_duplicate[
               'error'] == 'Пользователь уже существует', f"Ожидалась ошибка 'Пользователь уже существует', получена {data_duplicate.get('error')}"


def test_create_user_invalid_json_failure(http_server):
    '''Негатиный тест: создание недопустимого пользователя'''
    invalid_user = {"id": 1003, "name": None}
    resp = requests.post(f'{http_server}/users', json=invalid_user)
    assert resp.status_code in [400,
                                422], f"Ожидался статус 400 или 422 для некорректного JSON, получен {resp.status_code}"
    data = resp.json()
    assert 'error' in data, "Ожидалась ошибка в ответе для некорректного JSON"


def test_get_user_not_found_failure(http_server):
    '''Негативный тест: поиск несуществующего пользователя'''
    resp_not_found = requests.get(f'{http_server}/users/99999')
    print(resp_not_found.json())
    assert resp_not_found.status_code == 404, f"Ожидался статус 404 для несуществующего пользователя, получен {resp_not_found.status_code}"
    data_not_found = resp_not_found.json()
    assert 'error' in data_not_found
    assert data_not_found[
               'error'] == 'Пользователь не найден', f"Ожидалась ошибка 'Пользователь не найден', получена {data_not_found.get('error')}"


def test_get_recommendations_viewed_excluded(http_server, test_user):
    '''Негативный тест: попытка найти в рекомендациях просмтренный фильм'''
    requests.post(f'{http_server}/users', json=test_user)
    new_id = test_user['id']
    resp = requests.get(f'{http_server}/users/{new_id}/recommendations')
    assert resp.status_code == 200, f"Ожидался статус 200, получен {resp.status_code}"
    data = resp.json()
    viewed_ids = test_user.get('viewed', [])
    assert all(item['id'] not in viewed_ids for item in data), "Просмотренные позиции не должны быть в рекомендациях"


def test_get_recommendations_not_found_failure(http_server):
    '''Негативный тест: поиск рекомендация для несуществующего пользователя'''
    resp_not_found = requests.get(f'{http_server}/users/99999/recommendations')
    assert resp_not_found.status_code == 404, f"Ожидался статус 404 для рекомендаций несуществующего пользователя, получен {resp_not_found.status_code}"
    data_not_found = resp_not_found.json()
    assert 'error' in data_not_found
    assert data_not_found[
               'error'] == 'Пользователь не найден', f"Ожидалась ошибка 'Пользователь не найден', получена {data_not_found.get('error')}"


def test_create_user_empty_categories(http_server):
    '''Позитивный тест: создание пользователя с пустыми лайками, дизлайками и просмотренными фильмами'''
    new_id = 1004
    user_empty_categories = {
        "id": new_id,
        "name": f"Test User {new_id}",
        "like_categories": [],
        "dislike_categories": [],
        "viewed": []
    }
    resp = requests.post(f'{http_server}/users', json=user_empty_categories)
    assert resp.status_code == 201, f"Ожидался статус 201 для пользователя с пустыми категориями, получен {resp.status_code}"
    data_resp = resp.json()
    assert data_resp['message'] == 'Пользователь создан'


def test_like_movie_user_not_found(http_server):
    '''Негативный тест: добавление несуществующему пользователю понравивщегося фильма'''
    non_existing_user_id = 99999
    existing_movie_id = 1
    resp = requests.post(f'{http_server}/users/{non_existing_user_id}/movie/{existing_movie_id}/like')
    assert resp.status_code == 404, f"Ожидался статус 404 при лайке от несуществующего пользователя, получен {resp.status_code}"
    data = resp.json()
    assert 'error' in data
    assert 'не найден' in data['error']


def test_like_movie_movie_not_found(http_server):
    '''Негативный тест: добавление пользователю лайка к несуществующему фильму'''
    existing_user_id = 100
    non_existing_movie_id = 99999
    resp = requests.post(f'{http_server}/users/{existing_user_id}/movie/{non_existing_movie_id}/like')
    assert resp.status_code == 404, f"Ожидался статус 404 при лайке несуществующего фильма, получен {resp.status_code}"
    data = resp.json()
    assert 'error' in data
    assert 'не найден' in data['error']


def test_dislike_movie_user_not_found(http_server):
    '''Негативный тест: добавление несуществующему пользователю непонравившегося фильма'''
    non_existing_user_id = 99999
    existing_movie_id = 1
    resp = requests.post(f'{http_server}/users/{non_existing_user_id}/movie/{existing_movie_id}/dislike')
    assert resp.status_code == 404, f"Ожидался статус 404 при дизлайке от несуществующего пользователя, получен {resp.status_code}"
    data = resp.json()
    assert 'error' in data
    assert 'не найден' in data['error']


def test_dislike_movie_movie_not_found(http_server):
    '''Негативный тест: добавление пользователю дизлайка к несуществующему фильму'''
    existing_user_id = 100
    non_existing_movie_id = 99999
    resp = requests.post(f'{http_server}/users/{existing_user_id}/movie/{non_existing_movie_id}/dislike')
    assert resp.status_code == 404, f"Ожидался статус 404 при дизлайке несуществующего фильма, получен {resp.status_code}"
    data = resp.json()
    assert 'error' in data
    assert 'не найден' in data['error']


def test_add_viewed_movie_invalid_data(http_server):
    '''Негатиавный тест: добавление несуществующему пользователю просмотренного фильма'''
    user_id = 9999
    invalid_movie_id = 'abc'
    resp = requests.post(f'{http_server}/users/{user_id}/movie/{invalid_movie_id}/viewed')
    assert resp.status_code in [400, 422,
                                404], f"Ожидался статус ошибки при некорректном ID фильма, получен {resp.status_code}"


def test_add_viewed_movie_nonexistent_movie(http_server):
    '''Негатиавный тест: добавление пользователю несуществующего просмотренного фильма'''
    user_id = 100
    nonexistent_movie_id = 999999
    resp = requests.post(f'{http_server}/users/{user_id}/movie/{nonexistent_movie_id}/viewed')
    assert resp.status_code == 404, f"Ожидался статус 404 для несуществующего фильма, получен {resp.status_code}"
    data = resp.json()
    assert 'error' in data
    assert 'не найден' in data['error']


def test_like_movie_invalid_id_string(http_server):
    '''Негативный тест: добавление пользователю со строкой id понравившегося фильма'''
    user_id = 'abc'
    movie_id = 100
    resp = requests.post(f'{http_server}/users/{user_id}/movie/{movie_id}/like')
    assert resp.status_code in [400, 422,
                                404], f"Ожидался статус ошибки при строковом user_id, получен {resp.status_code}"


def test_like_movie_empty_path(http_server):
    '''Негативный тест: неверный путь'''
    resp = requests.post(f'{http_server}/users//movie//like')
    assert resp.status_code in [404, 400], f"Ожидался статус ошибки при пустом пути, получен {resp.status_code}"


def test_like_movie_twice(http_server):
    '''Негативный тест: попытка добавить пользователю для одного и тогоже фильма'''
    user_id = 100
    movie_id = 1
    first_resp = requests.post(f'{http_server}/users/{user_id}/movie/{movie_id}/like')
    assert first_resp.status_code == 200, f"Первый лайк должен быть успешным, получен {first_resp.status_code}"
    second_resp = requests.post(f'{http_server}/users/{user_id}/movie/{movie_id}/like')
    assert second_resp.status_code in [200,
                                       409], f"Ожидался 409 или 200 при повторном лайке, получен {second_resp.status_code}"
