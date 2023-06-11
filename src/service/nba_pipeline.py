import numpy as np

from common.constants import CURRENT_TEAMS
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

    def train_model(self) -> None:
        """
        Trains the logistic regression model using the specified training years.
        :return: None
        """

        training_input_data = []
        training_output_data = []
        input_context = []


        seasons: list[NbaSeason] = self.db.get_seasons(self.training_seasons)

        # For each season, iterate through each match in the schedule.
        for season in seasons:
            for match in season.matches:
                away_team: NbaTeam = self.teams[f"{match.away_team}_{season}"]
                home_team: NbaTeam = self.teams[f"{match.home_team}_{season}"]

                away_box = match.away_box_score
                home_box = match.home_box_score

                away_avg_bpm = self.calculate_avg_bpm(away_box)
                home_avg_bpm = self.calculate_avg_bpm(home_box)

                bpm_diff = home_avg_bpm - away_avg_bpm
                pre_data = self.generate_input_data(away_team, home_team)
                np.append(pre_data, [self.HOME_COURT_ADV, bpm_diff])

                away_box_total = away_box.iloc[-1]
                away_pts = away_box_total["PTS"]

                home_box_total = home_box.iloc[-1]
                home_pts = home_box_total["PTS"]

                game_pt_diff = float(away_pts) - float(home_pts)  # Done this way to better reflect spreads.

                training_input_data.append(pre_data)
                training_output_data.append(game_pt_diff)
                # context/row identifiers [away, home]
                input_context.append([away_team, home_team])

                print(f'{match.game_code} input and output data added.')

                # Update team objects with new match data.
                print(f"Updating away team ({away_team}) features.")
                away_team.update_team_stats(away_box, home_box, match.game_summary)
                print(f"Updating home team ({home_team}) features.")
                home_team.update_team_stats(home_box, away_box, match.game_summary)

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
        away_f = away.features
        home_f = home.features

        input_data = np.subtract(home_f, away_f)
        return input_data

    @staticmethod
    def create_teams(years) -> dict:
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

    def calculate_avg_bpm(self, box_score):
        pre_bpm_sum = 0.0
        count = 0

        for i in box_score.index[:-1]:  # -1 to exclude team totals.
            player_name = box_score['Players'][i]
            print(f"Fetching {player_name}'s BPM.")
            player_code = self.db.scraper.get_player_code(player_name)
            player = self.db.get_player(player_code)
            pre_bpm_sum += float(player.bpm)
            count += 1

        return pre_bpm_sum / count
