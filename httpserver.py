import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import re
from pymongo import MongoClient
from user.user import User
from items.position import Position
import os

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")

db_name = os.environ.get("DB_NAME", "recommendation_system")
db = client[db_name]

users_collection = db["users"]
positions_collection = db["positions"]

class UserHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        response = json.dumps(data, ensure_ascii=False).encode('utf-8')
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
        return users_collection.find_one({"id": user_id})

    def _find_position(self, position_id):
        return positions_collection.find_one({"id": position_id})

    def do_GET(self):
        parsed = urlparse(self.path)
        match = re.match(r'^/users/(\d+)$', parsed.path)
        if match:
            user_id = int(match.group(1))
            user = self._find_user(user_id)
            if user:
                user.pop('_id', None)
                self._send_json(user)
            else:
                self._send_json({'error': 'Пользователь не найден'}, status=404)
            return
        
        match = re.match(r'^/users/(\d+)/recommendations$', parsed.path)
        if match:
            user_id = int(match.group(1))
            recommendations = Position.get_recommendations_for_user(user_id)
            if isinstance(recommendations, str):  # если вернулась ошибка
                self._send_json({'error': recommendations}, status=404)
            else:
                self._send_json(recommendations)
            return

        self._send_json({'error': 'Не найдено'}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.strip('/').split('/')
        # import pdb; pdb.set_trace()

        if parsed.path == '/users':
            try:
                new_user = self._read_body()
                result, status = User.add_user(new_user)
                self._send_json(result, status=status)
            except ValueError as e:
                self._send_json({'error': str(e)}, status=400)
            return

        elif len(path_parts) == 5 and path_parts[0] == 'users' and path_parts[2] == 'movie':
            try:
                user_id = int(path_parts[1])
                movie_id = int(path_parts[3])
                action = path_parts[4]

                if not self._find_user(user_id):
                    self._send_json({'error': 'Пользователь не найден'}, status=404)
                    return

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
