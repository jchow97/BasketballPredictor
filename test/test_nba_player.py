from unittest import TestCase
from unittest.mock import patch

from models.nba_player import NbaPlayer


class TestNbaPlayer(TestCase):

    def setUp(self):
        self.test_player = NbaPlayer("Test Player 1", "testplayer01")

    @patch('models.nba_player.GamePlayerLog')
    def test_update_bpm(self, mock_player_log):
        type(mock_player_log).box_plus_minus = 10

        self.test_player.update_bpm(mock_player_log)

        self.assertEqual(1, self.test_player.games_played)
        self.assertEqual(10, self.test_player.bpm_total)
        self.assertEqual(10, self.test_player.bpm)

        self.test_player.update_bpm(mock_player_log)

        self.assertEqual(2, self.test_player.games_played)
        self.assertEqual(20, self.test_player.bpm_total)
        self.assertEqual(10, self.test_player.bpm)
