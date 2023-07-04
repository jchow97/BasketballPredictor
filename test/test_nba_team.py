from unittest import TestCase
from unittest.mock import Mock, patch, PropertyMock, MagicMock

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

    @patch('models.nba_team.Row')
    @patch('models.nba_team.Row')
    def test_update_features(self, mock_team_log, mock_opp_log):
        # Mock logs
        mock_team_log = MagicMock()
        mock_opp_log = MagicMock()

        type(mock_team_log).GameTeamLog = PropertyMock()
        type(mock_opp_log).GameTeamLog = PropertyMock()

        type(mock_team_log).GameTeamLog.total_points = 100
        type(mock_team_log).GameTeamLog.offensive_rating = 101
        type(mock_team_log).GameTeamLog.turnover_pct = 0.12
        type(mock_team_log).GameTeamLog.offensive_rebounds = 13
        type(mock_team_log).GameTeamLog.true_shooting_pct = 0.4
        type(mock_team_log).GameTeamLog.defensive_rating = 105
        type(mock_team_log).GameTeamLog.defensive_rebounds = 16
        type(mock_team_log).GameTeamLog.pace = 107

        type(mock_opp_log).GameTeamLog.total_points = 90
        type(mock_opp_log).GameTeamLog.offensive_rating = 91
        type(mock_opp_log).GameTeamLog.turnover_pct = 0.09
        type(mock_opp_log).GameTeamLog.offensive_rebounds = 9
        type(mock_opp_log).GameTeamLog.true_shooting_pct = 0.39
        type(mock_opp_log).GameTeamLog.defensive_rating = 99
        type(mock_opp_log).GameTeamLog.defensive_rebounds = 9
        type(mock_opp_log).GameTeamLog.pace = 99

        self.test_team.update_features(mock_team_log, mock_opp_log)

        self.assertEqual(1, self.test_team.wins)
        self.assertEqual(10, self.test_team.mov)
        self.assertEqual(101, self.test_team.off_rtg)
        self.assertEqual(0.12, self.test_team.tov_pct)
        self.assertEqual(13, self.test_team.off_reb)
        self.assertEqual(0.4, self.test_team.ts_pct)
        self.assertEqual(105, self.test_team.def_rtg)
        self.assertEqual(16, self.test_team.def_reb)
        self.assertEqual(0.09, self.test_team.opp_tov_pct)
        self.assertEqual(107, self.test_team.pace)
        self.assertEqual(1.0, self.test_team.win_loss_pct)
        self.assertEqual(1.0, self.test_team.last10_pct)

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
