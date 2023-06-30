from unittest import TestCase

from models.nba_team import NbaTeam


class TestNbaTeam(TestCase):

    def setUp(self):
        self.test_team1 = NbaTeam("Test Team 1", 2000)
        self.test_team2 = NbaTeam("Test Team 2", 2000)

    def test_calculate_last10(self):
        self.fail()

    def test_calculate_win_loss_pct(self):
        self.fail()

    def test_update_features(self):
        self.fail()

    def test_set_features(self):
        self.fail()

    def test_update_last10(self):
        self.fail()
