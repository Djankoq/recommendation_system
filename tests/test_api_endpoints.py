import pytest
import requests
import threading
import time
import json
import os
from http.server import ThreadingHTTPServer
from httpserver import UserHandler


@pytest.fixture(scope='module')
def http_server():
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


@pytest.fixture(scope='module')
def test_user(http_server):
    new_id = 1002
    new_user = {
        "id": new_id,
        "name": f"Test User {new_id}",
        "like_categories": ["Action"],
        "dislike_categories": ["Horror"],
        "viewed": [2]
    }
    return new_user


@pytest.fixture(scope='module', autouse=True)
def backup_and_restore_data():
    users_file = './users.json'
    positions_file = '../positions.json'

    original_users = []
    original_positions = []

    if os.path.exists(users_file):
        with open(users_file, 'r', encoding='utf-8') as f:
            content = f.read()
            original_users = json.loads(content) if content else []
            print(f"Исходные данные пользователей сохранены: {len(original_users)} пользователей")

    if os.path.exists(positions_file):
        with open(positions_file, 'r', encoding='utf-8') as f:
            content = f.read()
            original_positions = json.loads(content) if content else []
            print(f"Исходные данные позиций сохранены: {len(original_positions)} позиций")

    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
        print("Файл пользователей очищен перед тестами")

    with open(positions_file, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
        print("Файл позиций очищен перед тестами")

    yield

    with open(users_file, 'w', encoding='utf-8') as f:
        json.dump(original_users, f, ensure_ascii=False, indent=2)
        print(f"Исходные данные пользователей восстановлены: {len(original_users)} пользователей")

    with open(positions_file, 'w', encoding='utf-8') as f:
        json.dump(original_positions, f, ensure_ascii=False, indent=2)
        print(f"Исходные данные позиций восстановлены: {len(original_positions)} позиций")


# Позитивные тесты (ожидаемый результат совпадает с фактическим)
def test_create_user_success(http_server, test_user):
    new_user = test_user
    resp = requests.post(f'{http_server}/users', json=new_user)
    print(resp.json())
    assert resp.status_code == 201, f"Ожидался статус 201, получен {resp.status_code}"
    data_resp = resp.json()
    assert data_resp['message'] == 'Пользователь создан'


def test_get_user_success(http_server, test_user):
    new_id = test_user['id']
    resp = requests.get(f'{http_server}/users/{new_id}')
    assert resp.status_code == 200, f"Ожидался статус 200, получен {resp.status_code}"
    data = resp.json()
    assert data['id'] == new_id, f"Ожидался ID пользователя {new_id}, получен {data['id']}"
    assert data['name'] == test_user[
        'name'], f"Ожидалось имя пользователя '{test_user['name']}', получено {data['name']}"


def test_get_recommendations_success(http_server, test_user):
    new_id = test_user['id']
    resp = requests.get(f'{http_server}/users/{new_id}/recommendations')
    assert resp.status_code == 200, f"Ожидался статус 200, получен {resp.status_code}"

    data = resp.json()
    assert isinstance(data, list), "Ожидался список рекомендаций"
    assert len(data) == 999, f"Ожидалось 999 рекомендаций по умолчанию, получено {len(data)}"

    required_fields = ['id', 'position_name', 'tag']
    for item in data:
        for field in required_fields:
            assert field in item, f"Ожидалось поле '{field}' в рекомендации с ID {item.get('id')}"


def test_create_user_duplicate(http_server, test_user):
    # Повторная попытка создать того же пользователя
    resp = requests.post(f'{http_server}/users', json=test_user)
    assert resp.status_code == 400
    assert resp.json().get('error') == 'Пользователь уже существует'


def test_create_user_invalid_body(http_server):
    # Некорректный JSON
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f'{http_server}/users', data="{invalid_json}", headers=headers)
    assert resp.status_code == 400
    assert 'Неверный JSON' in resp.json().get('error')


def test_get_user_not_found(http_server):
    resp = requests.get(f'{http_server}/users/999999')
    assert resp.status_code == 404
    assert resp.json().get('error') == 'Пользователь не найден'


def test_get_recommendations_not_found(http_server):
    resp = requests.get(f'{http_server}/users/999999/recommendations')
    assert resp.status_code == 404
    assert resp.json().get('error') == 'Пользователь не найден'


def test_add_like_success(http_server, test_user):
    user_id = test_user['id']
    resp = requests.post(f'{http_server}/users/{user_id}/movie/1/like')
    assert resp.status_code == 200
    assert resp.json().get('message') == 'Лайк добавлен'


def test_add_dislike_success(http_server, test_user):
    user_id = test_user['id']
    resp = requests.post(f'{http_server}/users/{user_id}/movie/2/dislike')
    assert resp.status_code == 200
    assert resp.json().get('message') == 'Дизлайк добавлен'


def test_add_viewed_success(http_server, test_user):
    user_id = test_user['id']
    resp = requests.post(f'{http_server}/users/{user_id}/movie/1/viewed')
    assert resp.status_code == 200
    assert resp.json().get('message') == 'Фильм добавлен в просмотренные'


def test_add_like_invalid_user(http_server):
    resp = requests.post(f'{http_server}/users/99999/movie/1/like')
    assert resp.status_code == 404
    assert 'не найден' in resp.json().get('error').lower()


def test_add_dislike_invalid_movie(http_server, test_user):
    user_id = test_user['id']
    resp = requests.post(f'{http_server}/users/{user_id}/movie/99999/dislike')
    assert resp.status_code == 404
    assert 'не найден' in resp.json().get('error').lower()


def test_invalid_action(http_server, test_user):
    user_id = test_user['id']
    resp = requests.post(f'{http_server}/users/{user_id}/movie/1/unknown')
    assert resp.status_code == 400
    assert resp.json().get('error') == 'Неизвестное действие'
