import numpy as np
import pandas as pd

from common.constants import CURRENT_TEAMS
from models.nba_player import NbaPlayer
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

    def train_model(self):
        """
        Trains the logistic regression model using the specified training years.
        :return: TODO (not sure what `pipeline.fit` returns.).
        """

        """
        Pseudocode: How model training works.
            1. 2d array of input (features) -> actual outcome
                [features] -> pt_differential (home - away)
            2. run pipeline.fit(training_input_data, training_output_data)
            
        """
        training_input_data, training_output_data = self.generate_training_data()
        # Train model
        self.pipeline.fit(training_input_data, training_output_data)

    def generate_training_data(self):
        """
        Pseudocode:
            1. Loop through each season's schedule.
            2. For each game:
                a. Get pre-game features' values from Team and Player objects (inputs).
                b. Get Game + Box Scores from database:
                    For each game, query for Game.
                a. calculate the pre-game features' values (inputs).
                    -> For each player that played: Get their season BPM value.
                b. calculate the point differential between teams (outcome).
                c. Use actual team and player box scores to update team features and player BPM values.
        :return:
        """


        raise NotImplementedError()

    def run_prediction(self, year: int):
        """
        Predicts a season of the NBA using a trained model.
        :param year: Season year (2021-2022 is 2022).
        :return:
        """
        raise NotImplementedError()

    def check_prediction(self):
        """
        Checks prediction against odds data for prediction accuracy.
        :return: Prediction accuracy
        """
        raise NotImplementedError()

    def process_odds_data(self, year: int):
        """
        Process odds data from Excel spreadsheet.
        :param year: Season year (2021-2022 is 2022).
        :return: A dataframe of the odds data for use.
        """
        raise NotImplementedError()

    @staticmethod
    def generate_features_differential(away: NbaTeam, home: NbaTeam) -> list[float]:
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
