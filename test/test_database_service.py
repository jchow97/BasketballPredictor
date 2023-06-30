import unittest


class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_season_by_years(self):
        raise NotImplementedError

    def test_get_season_by_year(self):
        raise NotImplementedError

    def test_get_games_by_season_id(self):
        raise NotImplementedError

    def test_get_game_by_game_code(self):
        raise NotImplementedError

    def test_get_game_by_date_and_teams(self):
        raise NotImplementedError

    def test_get_team_by_name_and_season_id(self):
        raise NotImplementedError

    def test_get_team_logs_by_game_id(self):
        raise NotImplementedError

    def test_get_player_by_player_id(self):
        raise NotImplementedError

    def test_get_player_stats_by_player_id(self):
        raise NotImplementedError

    def test_get_player_logs_by_game_id_team_id(self):
        raise NotImplementedError

    def test_get_spread_by_game_code(self):
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
