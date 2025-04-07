import pytest
from unittest.mock import patch
from main import main_logic

def test_main_logic(capsys):
    # Мокируем метод Position.get_recommend_position
    with patch('items.position.Position.get_recommend_position') as mock_get_recommend_position:
        # Задаем возвращаемое значение для мок-объекта
        mock_get_recommend_position.return_value = ["Position1", "Position2", "Position3"]

        # Вызываем main_logic
        main_logic()

        # Проверяем, что данные были выведены в консоль
        captured = capsys.readouterr()
        assert "Position1" in captured.out
        assert "Position2" in captured.out
        assert "Position3" in captured.out

        # Проверяем, что метод был вызван с правильным аргументом
        mock_get_recommend_position.assert_called_once_with(1000)
