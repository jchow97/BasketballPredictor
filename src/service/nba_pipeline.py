import numpy as np
import pandas as pd

from common.constants import CURRENT_TEAMS
from models.database import *
from models.nba_match import NbaMatch
from models.nba_player import NbaPlayer
from models.nba_season import NbaSeason
from models.nba_team import NbaTeam
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from service.database_service import DatabaseService


class NbaPredictor:
    """
    This class is the predictor for NBA Games utilizing sklearn pipeline.
    """

    def __init__(self, database_service: DatabaseService, seasons: list[int]):
        """
        Constructor for Logistic Regression ML pipeline.
        :param seasons: Years for model training.
        """
        self.training_seasons = seasons
        self.teams = self.create_teams(seasons)
        self.pipeline = Pipeline([
            # ("scale", StandardScaler()),
            ("model", LogisticRegression(random_state=True, solver='liblinear', max_iter=100))
        ])

        self.HOME_COURT_ADV = 1.0

        self.db = database_service

    def train_model(self) -> tuple[list[list[float]], list[float], list[list[NbaTeam]]]:
        """
        Trains the logistic regression model using the specified training years.
        :return: None
        """

    def run_prediction(self, year: int):
        """
        Predicts a season of the NBA using a trained model.
        :param year: Season year (2021-2022 is 2022).
        :return:
        """

    def check_prediction(self):
        """
        Checks prediction against odds data for prediction accuracy.
        :return: Prediction accuracy
        """

    def process_odds_data(self, year: int):
        """
        Process odds data from Excel spreadsheet.
        :param year: Season year (2021-2022 is 2022).
        :return: A dataframe of the odds data for use.
        """

    @staticmethod
    def generate_input_data(away: NbaTeam, home: NbaTeam) -> list[float]:
        """
        Generate the differential between the features of the home team.
        :param away: Away team object.
        :param home: Home team object.
        :return: List of differences for each feature.
        """

        away_f: list[float] = away.features
        home_f: list[float] = home.features

        input_data = np.subtract(home_f, away_f)
        return input_data

    @staticmethod
    def create_teams(years: list[int]) -> dict:
        """
        Creates a dictionary of all current teams, for each year.
        :param years: Seasons to create teams for.
        :return: Dictionary of NBA teams (season unique).
        """
        teams = dict()
        for year in years:
            for team in CURRENT_TEAMS:
                team_name = f"{team}_{year}"
                teams[team_name] = NbaTeam(team, year)
                print(f'{team_name} created.')
        return teams

    def calculate_avg_bpm(self, box_score: pd.DataFrame) -> float:
        """
        Calculates the average box plus/minus for the team's box score.
        :param box_score: Dataframe of the team's box score.
        :return: float of the average box plus/minus.
        """
        pre_bpm_sum = 0.0
        count = 0

        for i in box_score.index[:-1]:  # -1 to exclude team totals.
            player_name = box_score['Players'][i]
            print(f"Fetching {player_name}'s BPM.")
            player_code: str = self.db.scraper.get_player_code(player_name)
            player: NbaPlayer = self.db.get_player(player_code)
            pre_bpm_sum += float(player.bpm)
            count += 1

        return pre_bpm_sum / count
