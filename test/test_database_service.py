import unittest
from unittest.mock import Mock

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.database import Team
from models.nba_match import NbaMatch
from models.nba_player import NbaPlayer
from models.nba_season import NbaSeason
from models.nba_team import NbaTeam
from scripts.Scraper import Scraper
from service.database_service import DatabaseService


class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        # Attempt at mocking.
        # self.mock_session = Mock(name="Session").return_value
        # self.mock_scraper = Mock(name="Scraper").return_value

        # Pass through mock session and scraper to DatabaseService.
        username = 'jeffreychow'
        port = '5432'
        database = 'nba_test'
        engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:{port}/{database}')
        session = Session(engine)
        scraper = Scraper()
        self.database_service = DatabaseService(session, scraper)

    def test_get_season(self):
        test_season = self.database_service.get_games_by_season_id(2022)
        self.assertEqual(test_season.season, 2022)

    def test_get_game(self):
        test_game_code = '202110190MIL'
        test_home_team = 'Milwaukee Bucks'
        test_away_team = 'Brooklyn Nets'
        test_match = self.database_service.get_game_by_game_code(test_game_code)
        self.assertEqual(test_match.game_code, test_game_code)
        self.assertEqual(test_match.home_team, test_home_team)
        self.assertEqual(test_match.away_team, test_away_team)

    def test_get_team(self):
        test_team = self.database_service.get_team_by_name_and_season('Portland Trail Blazers', 2022)
        self.assertEqual(test_team.team_name, 'Portland Trail Blazers')
        self.assertEqual(test_team.team_abbrv, 'POR')

    def test_get_player(self):
        # Mocking attempt
        # mock_query = self.mock_session.query.return_value
        # mock_filter = mock_query.filter.return_value
        # mock_filter.all.return_value = [{'friendly_name': 'Test Player', 'unique_code': 'testplayer01'}]
        #
        # test_player = self.database_service.get_player('testplayer01')
        # self.assertEqual(test_player.player_name, 'Test Player')
        # self.assertEqual(test_player.player_code, 'testplayer01')


        test_player = self.database_service.get_player('lillada01')
        expected_player = NbaPlayer('Damian Lillard', 'lillada01')

        self.assertEqual(test_player.player_name, expected_player.player_name)
        self.assertEqual(test_player.player_code, expected_player.player_code)
        self.assertEqual(test_player.bpm, expected_player.bpm)
        self.assertEqual(test_player.bpm_total, expected_player.bpm_total)
        self.assertEqual(test_player.games_played, expected_player.games_played)


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
