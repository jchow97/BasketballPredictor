import os

import numpy as np
import pandas as pd

from common.constants import CURRENT_TEAMS
from models.database import GamePlayerLog
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
        self.training_years = seasons
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
        training_input_data, training_output_data, game_codes = self.generate_data(self.training_years)
        # Train model
        self.pipeline.fit(training_input_data, training_output_data)

    def generate_data(self, years: list[int]) -> tuple[list[list[float]], list[float], list[str]]:
        """
        Generates input data to model training and predictions
        :param years: list of seasons
        :return: Input features (2d array), actual outcome data (array), corresponding game code (array)
        """
        pipeline_inputs = []
        actual_outcomes = []
        corresponding_matches = []

        for year in years:
            season = self.db.get_season_by_year(year)
            schedule = self.db.get_games_by_season_id(season.id)
            teams: dict = self.create_teams(year)
            players: dict[NbaPlayer] = {}
            count = 0
            for match in schedule:
                # if count <= 30:
                #     count += 1
                #     continue
                if count > 1230:
                    break
                # Get team game logs from database.
                home_team_log, away_team_log = self.db.get_team_logs_by_game_id(match.id)

                # Get Team objects from memory.
                home_team_obj: NbaTeam = teams[f"{home_team_log.name}"]
                away_team_obj: NbaTeam = teams[f"{away_team_log.name}"]

                home_player_logs: list[GamePlayerLog] = self.db.get_player_logs_by_game_id_team_id(match.id,
                                                                                                   match.home_team_id)
                away_player_logs: list[GamePlayerLog] = self.db.get_player_logs_by_game_id_team_id(match.id,
                                                                                                   match.away_team_id)

                # Get features from team objects (before this game's stats).
                features: list[float] = self.generate_features_differential(home_team_obj, away_team_obj)

                # Add average BPM differential from player objects
                np.append(features, (self.calculate_avg_bpm(home_player_logs, players) -
                                     self.calculate_avg_bpm(away_player_logs, players)))

                # Calculate outcome data.
                total_points_differential: float = \
                    home_team_log.GameTeamLog.total_points - away_team_log.GameTeamLog.total_points

                pipeline_inputs.append(features)
                actual_outcomes.append(total_points_differential)
                corresponding_matches.append(match.game_code)

                # Update team and player objects.
                home_team_obj.update_features(home_team_log, away_team_log)
                away_team_obj.update_features(away_team_log, home_team_log)

                count += 1

        return pipeline_inputs, actual_outcomes, corresponding_matches

    def run_prediction_for_season(self, year: int):
        """
        Predicts a season of the NBA using a trained model; used for prediction accuracy.
        :param year: Season year (2021-2022 is 2022).
        :return: None
        """
        # Initialize counters
        correct, incorrect, push, dnp = 0, 0, 0, 0
        results = []

        prediction_inputs, actual_outcomes, game_codes = self.generate_data([year])
        predictions = self.pipeline.predict(prediction_inputs)

        if len(predictions) != len(actual_outcomes):
            raise ValueError("List lengths should be the same")

        for i in range(len(predictions)):
            odds: float | None = self.db.get_spread_by_game_code(game_codes[i])
            if odds is None:
                dnp += 1  # no odds: do not count prediction.
                continue

            # Predict home team wins by more than the oddsmakers. We bet the home team spread.
            # TODO: double check that this math is correct (i.e. Positives and negatives).
            res = [predictions[i], actual_outcomes[i], odds, game_codes[i]]
            print(f"{i}: {game_codes[i]}")
            if predictions[i] < odds:
                if actual_outcomes[i] < odds:
                    correct += 1
                    res.append("Correct")
                elif actual_outcomes[i] > odds:
                    incorrect += 1
                    res.append("Incorrect")
                else:
                    push += 1
                    res.append("Push")
            elif predictions[i] > odds:
                if actual_outcomes[i] < odds:
                    incorrect += 1
                    res.append("Incorrect")
                elif actual_outcomes[i] > odds:
                    correct += 1
                    res.append("Correct")
                else:
                    push += 1
                    res.append("Push")
            else:
                dnp += 1
                continue

            results.append(res)

        results_summary = pd.DataFrame(data=results,
                                       columns=['Prediction', 'Actual Point Difference', 'Closing Odds',
                                                'Prediction Outcome', 'Game Code'])
        outname = f'{year}_prediction.csv'
        outdir = './data'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        fullname = os.path.join(outdir, outname)
        results_summary.to_csv(fullname)

        win_correctness = float(correct) / (float(correct) + float(incorrect) + float(push))
        win_loss_pct = float(correct) / (float(correct) + float(incorrect))
        print(f"Correct: {correct} ; Incorrect: {incorrect} ; Push: {push} ; Did Not Predict: {dnp}.")
        print(f"Win Correctness: {win_correctness} (Includes pushes in total count, but not as wins; does not include "
              f"DNPs)")
        print(f"Win Loss Percentage: {win_loss_pct} (Does not include pushes or DNP)")

    def check_prediction(self):
        """
        Checks prediction based on odds data against outcome data for prediction accuracy.
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

    def calculate_avg_bpm(self, player_logs, players: dict) -> float:
        """
        Calculates the average box plus/minus differential of the players between two teams in a match.
        :param players: Dictionary of NbaPlayer objects.
        :param player_logs: Team's player logs for the match.
        :return: float of the average box plus/minus.
        """
        pre_bpm_sum = 0.0
        count = 0

        # TODO: Add support to advanced stats in database.
        # TODO: Currently this uses a player dict, but make it so that we query instead to reduce our memory usage.
        for player_log in player_logs:
            if player_log.minutes_played is None:
                continue

            player = self.db.get_player_by_player_id(player_log.player_id)
            player_obj = players.get(player.unique_code)
            if not player_obj:
                players[player.unique_code] = NbaPlayer(player.friendly_name, player.unique_code)
                pre_bpm_sum += float(players[player.unique_code].bpm)
            else:
                pre_bpm_sum += float(player_obj.bpm)
            count += 1

            players[player.unique_code].update_bpm(player_log)
        if count == 0:
            return 0

        return pre_bpm_sum / count

    @staticmethod
    def generate_features_differential(home: NbaTeam, away: NbaTeam) -> list[float]:
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
    def create_teams(year: int) -> dict:
        """
        Creates a dictionary of all current teams, for each year.
        :param year: Seasons to create teams for.
        :return: Dictionary of NBA teams (season unique).
        """
        teams = {}
        for team in CURRENT_TEAMS:
            teams[team] = NbaTeam(team, year)
            print(f'{team} created.')
        return teams
