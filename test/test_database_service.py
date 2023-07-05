import unittest
from unittest.mock import patch, MagicMock, call

from mock_alchemy.mocking import UnifiedAlchemyMagicMock

from models.database import Season, Game, Team, Player, PlayerStats, GamePlayerLog
from service.database_service import DatabaseService


class TestDatabaseService(unittest.TestCase):
    @patch("service.database_service.Engine")
    @patch("service.database_service.Scraper")
    def setUp(self, mock_scraper, mock_engine):
        mock_session = UnifiedAlchemyMagicMock()
        self.test_database_service = DatabaseService(mock_session, mock_scraper, mock_engine)

    def test_get_season_by_years(self):
        self.test_database_service.get_season_by_year = MagicMock()
        test_years = [2022, 2023]
        self.test_database_service.get_seasons_by_years(test_years)

        self.test_database_service.get_season_by_year.assert_has_calls([call(2022), call(2023)])

    def test_get_season_by_year(self):
        self.test_database_service.get_season_by_year(2023)

        self.test_database_service.session.assert_has_calls([
            call.query(Season),
            call.where(Season.year == '2023'),
            call.one_or_none()
        ])

    def test_get_games_by_season_id(self):
        self.test_database_service.get_games_by_season_id(1)

        self.test_database_service.session.assert_has_calls([
            call.query(Game),
            call.where(Game.season_id == 1),
            call.all()
        ])

    def test_get_game_by_game_code(self):
        self.test_database_service.get_game_by_game_code("testgame01")

        self.test_database_service.session.assert_has_calls([
            call.query(Game),
            call.where(Game.game_code == 'testgame01'),
            call.one_or_none()
        ])

    def test_get_game_by_date_and_teams(self):
        # TODO: Figure out how to test: Currently because it is using a mock database,
        #       it doesn't have real values to re-query.
        pass

    def test_get_team_by_name_and_season_id(self):
        self.test_database_service.get_team_by_name_and_season_id("Test Team", 1)

        self.test_database_service.session.assert_has_calls([
            call.query(Team),
            call.where(Team.season_id == 1, Team.name == "Test Team"),
            call.one_or_none()
        ])

    def test_get_team_logs_by_game_id(self):
        # self.test_database_service.get_team_logs_by_game_id("testgame01")
        #
        # self.test_database_service.session.assert_has_calls([
        #     call.query(GameTeamLog, Team.name),
        #     call.where(GameTeamLog.game_id == "testgame01"),
        #     call.where(GameTeamLog.team_id == Team.id),
        #     call.one_or_none()
        # ])
        # TODO: Fix test; tuple return
        pass

    def test_get_player_by_player_id(self):
        self.test_database_service.get_player_by_player_id(1)

        self.test_database_service.session.assert_has_calls([
            call.query(Player),
            call.where(Player.id == 1),
            call.one_or_none()
        ])

    def test_get_player_stats_by_player_id(self):
        self.test_database_service.get_player_stats_by_player_id(1)

        self.test_database_service.session.assert_has_calls([
            call.query(PlayerStats),
            call.where(PlayerStats.player_id == 1),
            call.order_by(PlayerStats.season.desc()),
            call.first()
        ])

    def test_get_player_logs_by_game_id_team_id(self):
        self.test_database_service.get_player_logs_by_game_id_team_id(1, 1)

        self.test_database_service.session.assert_has_calls([
            call.query(GamePlayerLog),
            call.where(GamePlayerLog.game_id == 1, GamePlayerLog.team_id == 1),
            call.all()
        ])

    def test_get_spread_by_game_code(self):
        # self.test_database_service.get_spread_by_game_code("testgame01")
        #
        # self.test_database_service.session.assert_has_calls([
        #     call.query(Game.spread),
        #     call.where(Game.game_code == "testgame01"),
        #     call.one_or_none()
        # ])
        # TODO: Fix test, tuple return
        pass


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
