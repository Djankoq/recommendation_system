import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import re
import os
from user.user import User

USERS_FILE = "users.json"
POSITIONS_FILE = "positions.json"


def load_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


users = load_file(USERS_FILE)
positions = load_file(POSITIONS_FILE)


class UserHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        response = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _read_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("Пустое тело запроса")
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Неверный JSON: {str(e)}")

    def _find_user(self, user_id):
        return next((u for u in users if u['id'] == user_id), None)

    def _find_position(self, position_id):
        return next((p for p in positions if p['id'] == position_id), None)

    def do_GET(self):
        parsed = urlparse(self.path)
        match = re.match(r'^/users/(\d+)$', parsed.path)
        if match:
            user_id = int(match.group(1))
            user = self._find_user(user_id)
            if user:
                self._send_json(user)
            else:
                self._send_json({'error': 'Пользователь не найден'}, status=404)
            return

        match = re.match(r'^/users/(\d+)/recommendations$', parsed.path)
        if match:
            user_id = int(match.group(1))
            user = self._find_user(user_id)
            if not user:
                self._send_json({'error': 'Пользователь не найден'}, status=404)
                return
            # Примитивная логика: выдаем первые 5 непосещённых позиций
            viewed_ids = user.get('viewed', [])
            recommended = [p for p in positions if p['id'] not in viewed_ids]
            self._send_json(recommended)
            return

        self._send_json({'error': 'Не найдено'}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip('/').split('/')

        if parsed.path == '/users':
            try:
                new_user = self._read_body()

                required_fields = {'id', 'name', 'like_categories', 'dislike_categories', 'viewed'}
                if not required_fields.issubset(new_user):
                    self._send_json({'error': 'Отсутствуют обязательные поля'}, status=400)
                    return

                if not isinstance(new_user['id'], int) or not isinstance(new_user['name'], str):
                    self._send_json({'error': 'Неверный тип для id или имени'}, status=400)
                    return
                if self._find_user(new_user['id']):
                    self._send_json({'error': 'Пользователь уже существует'}, status=400)
                    return

                users.append(new_user)
                save_file(users, USERS_FILE)
                self._send_json({'message': 'Пользователь создан'}, status=201)
            except ValueError as e:
                self._send_json({'error': str(e)}, status=400)
            return

        elif len(path_parts) == 5 and path_parts[0] == 'users' and path_parts[2] == 'movie':
            try:
                user_id = int(path_parts[1])
                movie_id = int(path_parts[3])
                action = path_parts[4]

                if action == 'like':
                    User.add_like_to_user(user_id, movie_id)
                    self._send_json({'message': 'Лайк добавлен'}, status=200)

                elif action == 'dislike':
                    User.add_dislike_to_user(user_id, movie_id)
                    self._send_json({'message': 'Дизлайк добавлен'}, status=200)

                elif action == 'viewed':
                    User.add_viewed_item(user_id, movie_id)
                    self._send_json({'message': 'Фильм добавлен в просмотренные'}, status=200)

                else:
                    self._send_json({'error': 'Неизвестное действие'}, status=400)

            except ValueError as e:
                self._send_json({'error': str(e)}, status=404)
            except Exception as e:
                self._send_json({'error': f'Внутренняя ошибка сервера: {str(e)}'}, status=500)
            return

        else:
            self._send_json({'error': 'Не найдено'}, status=404)


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8000
    server = ThreadingHTTPServer((host, port), UserHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()
