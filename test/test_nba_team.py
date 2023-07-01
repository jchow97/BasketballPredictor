from collections import deque
from unittest import TestCase

from models.nba_team import NbaTeam


class TestNbaTeam(TestCase):

    def setUp(self):
        self.test_team = NbaTeam("Test Team", 2000)

    def test_calculate_last10_success(self):
        # set up
        self.test_team.last10.extend("WLWLW")

        self.assertEqual(0.6, self.test_team.calculate_last10())

    def test_calculate_last10_no_losses_success(self):
        # set up
        self.test_team.last10.extend("WWW")
        self.assertEqual(1.0, self.test_team.calculate_last10())

    def test_calculate_last10_no_wins_success(self):
        # set up
        self.test_team.last10.extend("LLL")

        self.assertEqual(0.0, self.test_team.calculate_last10())

    def test_calculate_win_loss_pct_success(self):
        self.test_team.wins = 3
        self.test_team.losses = 2

        self.test_team.calculate_win_loss_pct()

        self.assertEqual(0.6, self.test_team.win_loss_pct)

    def test_calculate_win_loss_pct_no_wins_success(self):
        self.test_team.wins = 0
        self.test_team.losses = 2

        self.test_team.calculate_win_loss_pct()

        self.assertEqual(0.0, self.test_team.win_loss_pct)

    def test_calculate_win_loss_pct_no_losses_success(self):
        self.test_team.wins = 3
        self.test_team.losses = 0

        self.test_team.calculate_win_loss_pct()

        self.assertEqual(1.0, self.test_team.win_loss_pct)

    def test_calculate_win_loss_pct_no_wins_no_losses_success(self):
        self.test_team.wins = 0
        self.test_team.losses = 0

        self.test_team.calculate_win_loss_pct()

        self.assertEqual(0.0, self.test_team.win_loss_pct)

    # TODO: Mocking candidate
    # def test_update_features(self):
    #     # test_team_log
    #     # test_opp_log
    #     self.fail()

    def test_set_features(self):
        self.test_team.win_loss_pct = 0.1
        self.test_team.mov = 0.2
        self.test_team.off_rtg = 0.3
        self.test_team.tov_pct = 0.4
        self.test_team.off_reb = 0.5
        self.test_team.ts_pct = 0.6
        self.test_team.def_rtg = 0.7
        self.test_team.def_reb = 0.8
        self.test_team.opp_tov_pct = 0.9
        self.test_team.pace = 1.0
        self.test_team.last10_pct = 1.1

        self.test_team.set_features()

        self.assertEqual(
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
            self.test_team.features
        )

    def test_update_last10(self):
        self.test_team.last10.extend("WWWWWLLL")

        # adding to not full queue
        self.test_team.update_last10("L")
        self.assertEqual(9, len(self.test_team.last10))

        self.test_team.update_last10("L")
        self.assertEqual(10, len(self.test_team.last10))

        # no change in w/l
        self.test_team.update_last10("W")
        self.assertEqual(10, len(self.test_team.last10))
        self.assertEqual(0.5, self.test_team.calculate_last10())

        # change in w/l
        self.test_team.update_last10("L")
        self.assertEqual(10, len(self.test_team.last10))
        self.assertEqual(0.4, self.test_team.calculate_last10())
