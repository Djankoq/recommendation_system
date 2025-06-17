from unittest.mock import patch
from main import main_logic

def test_main_logic(capsys):
    with patch('main.Position.get_recommendations_for_user') as mock_get_recommendations:
        mock_get_recommendations.return_value = ["Position1", "Position2", "Position3"]

        main_logic()

        captured = capsys.readouterr()
        assert "Position1" in captured.out
        assert "Position2" in captured.out
        assert "Position3" in captured.out

        mock_get_recommendations.assert_called_once_with(44)
