import unittest
from unittest.mock import patch

import numpy as np

from common.constants import CURRENT_TEAMS
from service.nba_pipeline import NbaPredictor


class TestNbaPipeline(unittest.TestCase):
    @patch("service.nba_pipeline.DatabaseService")
    def setUp(self, mock_db_service) -> None:
        self.test_nba_predictor = NbaPredictor(mock_db_service, [2023])

    @patch("service.nba_pipeline.NbaTeam")
    @patch("service.nba_pipeline.NbaTeam")
    def test_generate_features_differential(self, mock_home_team, mock_away_team):
        mock_home_team.features = [1.1, 1.2, 1.3]
        mock_away_team.features = [0.5, 0.5, 0.5]

        actual = self.test_nba_predictor.generate_features_differential(mock_home_team, mock_away_team)
        expected = np.array([0.6, 0.7, 0.8])
        self.assertTrue(np.allclose(expected, actual))

    def test_create_teams(self):
        test_teams = self.test_nba_predictor.create_teams(2023)

        for name in CURRENT_TEAMS:
            self.assertEqual(name, test_teams[name].team_name)
            self.assertEqual(2023, test_teams[name].season)
