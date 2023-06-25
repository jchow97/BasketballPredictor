import unittest


class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        raise NotImplementedError

    def test_get_season(self):
        raise NotImplementedError

    def test_get_game(self):
        raise NotImplementedError

    def test_get_team(self):
        raise NotImplementedError

    def test_get_player(self):
        raise NotImplementedError


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
