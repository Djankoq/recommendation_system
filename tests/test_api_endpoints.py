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
    positions_file = './positions.json'
    
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

def test_create_user(http_server, test_user):
    new_user = test_user
    resp = requests.post(f'{http_server}/users', json=new_user)
    print(resp.json())
    assert resp.status_code == 201, f"Ожидался статус 201, получен {resp.status_code}"
    resp_duplicate = requests.post(f'{http_server}/users', json=new_user)
    data_resp = resp.json()
    assert data_resp['message'] == 'Пользователь создан'

    assert resp_duplicate.status_code == 400, f"Ожидался статус 400 для дубликата пользователя, получен {resp_duplicate.status_code}"
    data_duplicate = resp_duplicate.json()
    assert 'error' in data_duplicate
    assert data_duplicate['error'] == 'Пользователь уже существует', f"Ожидалась ошибка 'Пользователь уже существует', получена {data_duplicate.get('error')}"

def test_get_user(http_server, test_user):
    new_id = test_user['id']
    resp = requests.get(f'{http_server}/users/{new_id}')
    assert resp.status_code == 200, f"Ожидался статус 200, получен {resp.status_code}"
    data = resp.json()
    assert data['id'] == new_id, f"Ожидался ID пользователя {new_id}, получен {data['id']}"
    assert data['name'] == test_user['name'], f"Ожидалось имя пользователя '{test_user['name']}', получено {data['name']}"

    resp_not_found = requests.get(f'{http_server}/users/99999')
    print(resp_not_found.json())
    assert resp_not_found.status_code == 404, f"Ожидался статус 404 для несуществующего пользователя, получен {resp_not_found.status_code}"
    data_not_found = resp_not_found.json()
    assert 'error' in data_not_found
    assert data_not_found['error'] == 'Пользователь не найден', f"Ожидалась ошибка 'Пользователь не найден', получена {data_not_found.get('error')}"

def test_get_recommendations(http_server, test_user):
    new_id = test_user['id']
    resp = requests.get(f'{http_server}/users/{new_id}/recommendations')
    assert resp.status_code == 200, f"Ожидался статус 200, получен {resp.status_code}"

    data = resp.json()
    assert isinstance(data, list), "Ожидался список рекомендаций"
    assert len(data) == 999, f"Ожидалось 999 рекомендаций по умолчанию, получено {len(data)}"

    viewed_ids = test_user.get('viewed', [])
    assert all(item['id'] not in viewed_ids for item in data), "Просмотренные позиции не должны быть в рекомендациях"

    required_fields = ['id', 'position_name', 'tag']
    for item in data:
        for field in required_fields:
            assert field in item, f"Ожидалось поле '{field}' в рекомендации с ID {item.get('id')}"
