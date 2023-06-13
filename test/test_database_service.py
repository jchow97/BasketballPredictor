import unittest
from unittest.mock import Mock

from models.database import Team
from models.nba_match import NbaMatch
from models.nba_player import NbaPlayer
from models.nba_season import NbaSeason
from models.nba_team import NbaTeam
from service.database_service import DatabaseService


class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        self.mock_session = Mock(name="Session")
        self.mock_scraper = Mock(name="Scraper")

        # Pass through mock session and scraper to DatabaseService.
        self.database_service = DatabaseService(self.mock_session, self.mock_scraper)

    def test_get_season(self):
        test_season = self.database_service.get_season(2023)
        self.mock_session.query.return_value = NbaSeason(2023)

        self.assertEqual(test_season.season, 2023)

    def test_get_game(self):
        test_game_code = '010120230POR'
        test_home_team = NbaTeam('Portland Trail Blazers', 2023)
        test_away_team = NbaTeam('Golden State Warriors', 2023)
        self.mock_session.query.return_value = NbaMatch(test_game_code, test_home_team, test_away_team)

        test_match = self.database_service.get_game(test_game_code)
        self.assertEqual(test_match.game_code, test_game_code)
        self.assertEqual(test_match.home_team, test_home_team)
        self.assertEqual(test_match.away_team, test_away_team)


    def test_get_team(self):
        self.mock_session.query.return_value = NbaTeam('Portland Trail Blazers', 2023)

        test_team = self.database_service.get_team('Portland Trail Blazers', 2023)
        self.assertEqual(test_team.team_name, 'Portland Trail Blazers')
        self.assertEqual(test_team.team_abbrv, 'POR')
    def test_get_player(self):
        self.mock_session.query.return_value = NbaPlayer('Test Player', 'testplayer01')

        test_player = self.database_service.get_player('testplayer01')
        self.assertEqual(test_player.player_name, 'Test Player')
        self.assertEqual(test_player.player_code, 'testplayer01')


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
