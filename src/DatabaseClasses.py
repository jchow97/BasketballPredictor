from urllib.parse import _ParseResultBytesBase
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from scripts.Scraper import Scraper

Base = declarative_base()

class Game(Base):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("season.id"))
    type = Column(Integer, ForeignKey("game_type.id"))
    start_datetime = Column(DateTime)
    game_code = Column(String)

class GamePlayerLog(Base):
    __tablename__ = "game_player_log"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id"))
    game_team_id = Column(Integer, ForeignKey("game_team.id"))

    minutes_played = Column(Integer)
    field_goals = Column(Integer)
    field_goal_attempts = Column(Integer)
    field_goal_pct = Column(Integer)
    three_pointers = Column(Integer)
    three_point_attempts = Column(Integer)
    three_point_pct = Column(DECIMAL)
    free_throws = Column(Integer)
    free_throw_attempts = Column(Integer)
    free_throw_pct = Column(DECIMAL)
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)
    total_rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    personal_fouls = Column(Integer)
    points = Column(Integer)
    plus_minus = Column(Integer)
    true_shooting_pct = Column(DECIMAL)
    effective_field_goal_pct = Column(DECIMAL)
    three_point_attempt_rate = Column(DECIMAL)
    free_throw_attempt_rate = Column(DECIMAL)
    offensive_rebound_pct = Column(DECIMAL)
    defensive_rebound_pct = Column(DECIMAL)
    total_rebound_pct = Column(DECIMAL)
    assist_pct = Column(DECIMAL)
    steal_pct = Column(DECIMAL)
    block_pct = Column(DECIMAL)
    turnover_pct = Column(DECIMAL)
    usage_pct = Column(DECIMAL)
    offensive_rating = Column(DECIMAL)
    defensive_rating = Column(DECIMAL)
    box_plus_minus = Column(DECIMAL)

class GameTeam(Base):
    __tablename__ = "game_team"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("game.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    team_home_away = Column(Integer, ForeignKey("team_home_away.id"))
    game_team_log = Column(Integer, ForeignKey("game_team_log.id"))
    spread = Column(DECIMAL)
    odds = Column(DECIMAL)
    money_line_odds = Column(DECIMAL)
    over_under_odds = Column(DECIMAL)

class GameTeamLog(Base):
    __tablename__ = "game_team_log"

    id = Column(Integer, primary_key=True)
    game_team_id = Column(Integer, ForeignKey("game_team.id"))

    total_points = Column(Integer)
    first_quarter_points = Column(Integer)
    second_quarter_points = Column(Integer)
    third_quarter_points = Column(Integer)
    fourth_quarter_points = Column(Integer)
    overtime_points = Column(String) # going to store a list of = Column(Integer)s, then we can store infinite overtime_points

    minutes_played = Column(Integer)
    field_goals = Column(Integer)
    field_goal_attempts = Column(Integer)
    field_goal_pct = Column(Integer)
    three_pointers = Column(Integer)
    three_point_attempts = Column(Integer)
    three_point_pct = Column(DECIMAL)
    free_throws = Column(Integer)
    free_throw_attempts = Column(Integer)
    free_throw_pct = Column(DECIMAL)
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)
    total_rebounds = Column(Integer)
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    personal_fouls = Column(Integer)
    points = Column(Integer)
    plus_minus = Column(Integer)

    true_shooting_pct = Column(DECIMAL)
    effective_field_goal_pct = Column(DECIMAL)
    three_point_attempt_rate = Column(DECIMAL)
    free_throw_attempt_rate = Column(DECIMAL)
    offensive_rebound_pct = Column(DECIMAL)
    defensive_rebound_pct = Column(DECIMAL)
    total_rebound_pct = Column(DECIMAL)
    assist_pct = Column(DECIMAL)
    steal_pct = Column(DECIMAL)
    block_pct = Column(DECIMAL)
    turnover_pct = Column(DECIMAL)
    usage_pct = Column(DECIMAL)
    offensive_rating = Column(DECIMAL)
    defensive_rating = Column(DECIMAL)
    box_plus_minus = Column(DECIMAL)
    pace = Column(DECIMAL)
    free_throws_per_field_goal_attempt = Column(DECIMAL)

class GameType(Base):
    __tablename__ = "game_type"

    id = Column(Integer, primary_key=True)
    type = Column(String) # preseason, regular season, play-in, playoffs (CQF, CSF, CF, F)

class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True)
    unique_code = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    friendly_name = Column(String)
    birth_date = Column(DateTime)

class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id"))
    type = Column(Integer, ForeignKey("player_stats_type.id")) # 0: season 1: career
    games_played = Column(Integer)
    games_started = Column(Integer)
    minutes_played = Column(DECIMAL)
    field_goals = Column(DECIMAL)
    field_goal_attempts = Column(DECIMAL)
    field_goal_pct = Column(DECIMAL)
    three_pointers = Column(DECIMAL)
    three_point_attempts = Column(DECIMAL)
    three_point_pct = Column(DECIMAL)
    two_pointers = Column(DECIMAL)
    two_point_attempts = Column(DECIMAL)
    two_point_pct = Column(DECIMAL)
    effective_field_goal_pct = Column(DECIMAL)
    free_throws = Column(DECIMAL)
    free_throw_attempts = Column(DECIMAL)
    free_throw_pct = Column(DECIMAL)
    offensive_rebounds = Column(DECIMAL)
    defensive_rebounds = Column(DECIMAL)
    total_rebounds = Column(DECIMAL)
    assists = Column(DECIMAL)
    steals = Column(DECIMAL)
    blocks = Column(DECIMAL)
    turnovers = Column(DECIMAL)
    personal_fouls = Column(DECIMAL)
    points = Column(DECIMAL)

class PlayerStatsType(Base):
    __tablename__ = "player_stats_type"

    id = Column(Integer, primary_key=True)
    type = Column(String)

class PlayerTeam(Base):
    __tablename__ = "player_team"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("player.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)

class Season(Base):
    __tablename__ = "season"

    id = Column(Integer, primary_key=True)
    year = Column(String(4))
    friendly_name = Column(String)
    preseason_start = Column(DateTime)
    preseason_end = Column(DateTime)
    season_start = Column(DateTime)
    season_end = Column(DateTime)
    playoffs_start = Column(DateTime)
    playoffs_end = Column(DateTime)

class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("season.id"))
    team_stats_id = Column(Integer, ForeignKey("team_stats.id"))
    team_advanced_stats_id = Column(Integer, ForeignKey("team_advanced_stats.id"))
    team_name = Column(String)
    friendly_name = Column(String)

    wins = Column(Integer)
    losses = Column(Integer)
    home_wins = Column(Integer)
    home_losses = Column(Integer)
    away_wins = Column(Integer)
    away_losses = Column(Integer)
    streak = Column(Integer)
    last_ten_wins = Column(Integer)
    last_ten_losses = Column(Integer)
    
    ats_wins = Column(Integer)
    ats_losses = Column(Integer)
    ats_ties = Column(Integer)
    ats_home_wins = Column(Integer)
    ats_home_losses = Column(Integer)
    ats_home_ties = Column(Integer)
    ats_away_wins = Column(Integer)
    ats_away_losses = Column(Integer)
    ats_away_ties = Column(Integer)

class TeamHomeAwayType(Base):
    __tablename__ = "team_home_away_type"
    
    id = Column(Integer, primary_key=True)
    type = Column(String)

class TeamStats(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True)
    type = Column(Integer, ForeignKey("team_stats_type.id"))
    minutes_played = Column(DECIMAL)
    field_goals = Column(DECIMAL)
    field_goal_attempts = Column(DECIMAL)
    three_pointers = Column(DECIMAL)
    three_point_attempts = Column(DECIMAL)
    three_point_pct = Column(DECIMAL)
    two_pointers = Column(DECIMAL)
    two_point_attempts = Column(DECIMAL)
    two_point_pct = Column(DECIMAL)
    free_throws = Column(DECIMAL)
    free_throw_attempts = Column(DECIMAL)
    free_throw_pct = Column(DECIMAL)
    offensive_rebounds = Column(DECIMAL)
    defensive_rebounds = Column(DECIMAL)
    total_rebounds = Column(DECIMAL)
    assists = Column(DECIMAL)
    steals = Column(DECIMAL)
    blocks = Column(DECIMAL)
    turnovers = Column(DECIMAL)
    personal_fouls = Column(DECIMAL)
    points = Column(DECIMAL)

class TeamStatsType(Base):
    __tablename__ = "team_stats_type"

    id = Column(Integer, primary_key=True)
    type = Column(String)

class TeamAdvancedStats(Base):
    __tablename__ = "team_advanced_stats"

    id = Column(Integer, primary_key=True)
    wins = Column(Integer)
    losses = Column(Integer)
    pythagorean_wins = Column(Integer)
    pythagorean_losses = Column(Integer)
    margin_of_victory = Column(DECIMAL)
    strength_of_schedule = Column(DECIMAL)
    simple_rating_system = Column(DECIMAL)
    offensive_rating = Column(DECIMAL)
    defensive_rating = Column(DECIMAL)
    pace = Column(DECIMAL)
    free_throw_attempt_rate = Column(DECIMAL)
    three_point_attempt_rate = Column(DECIMAL)
    effective_field_goal_pct = Column(DECIMAL)
    turnover_pct = Column(DECIMAL)
    offensive_rebound_pct = Column(DECIMAL)
    free_throws_per_field_goal_attempt = Column(DECIMAL)
    opponent_effective_field_goal_pct = Column(DECIMAL)
    opponent_turnover_pct = Column(DECIMAL)
    defensive_rebound_pct = Column(DECIMAL)
    defensive_free_throws_per_field_goal_attempt = Column(DECIMAL)
    arena = Column(String)
    attendance = Column(String)


def initialize_database(year, database='mock_nba_database'):
    engine = create_engine(f'postgresql+psycopg2://jeffreychow:@localhost:5432/{database}')
    session = Session(engine)

    # Create database tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    populate_type_tables(engine, session)

    s = Scraper()

    schedule_df = s.scrape_nba_season(year)

    #
    season = Season (
        year = f"{year}",
        friendly_name = f"NBA Season {year - 1}-{year}",
        season_start = s.to_postgres_date(schedule_df['Date'].iloc[0]),
        season_end = get_season_end_date(schedule_df)
    )
    
    session.add(season)
    session.commit()

    # Query for season id.
    curr_season_id = session.query(Season.id).filter(Season.year == f"{year}").first()
    
    for row in schedule_df.index:
        game_datetime = schedule_df['Date'][row]

        game = Game (
            season_id = curr_season_id,
            # TODO: scrape playoff games too
            type = 1,
            start_datetime = s.to_postgres_date(game_datetime),
            game_code = s.__get_game_code(game_datetime, schedule_df['Home/Neutral'][row])
        )
        session.add(game)
        session.commit()

    session.commit()

# HELPER FUNCTIONS

"""
Get the end-date for the regular season.

@param schedule_dataframe - the data frame of the season schedule.
@return string of date in postgres format.
"""
def get_season_end_date(schedule_dataframe) -> str:
    pass

"""
Populate the type tables with known types.
Type tables: game_type, player_stats_type, team_home_away_type, team_stats_type

@param engine - SQLAlchemy engine.
@param session - SQLAlchemy session.
@return None
"""
def populate_type_tables(engine, session) -> None:
    # Add Game Types TODO: Expand playoffs into CQF, CSF, CF, F.
    game_types = ["Preseason", "Regular Season", "Play-In Game", "Playoffs"]
    for gt in game_types:
        gt_object = GameType(type=gt)
        session.add(gt_object)
        session.commit()
    
    # Add Player Types
    player_stats_types = ["Regular Season", "Regular Season Career", "Playoffs", "Playoffs Career"]
    for pst in player_stats_types:
        pst_object = PlayerStatsType(type=pst)
        session.add(pst_object)
        session.commit()

    # Add Team Home/Away Types
    team_home_away_types = ["Home", "Away"]
    for that in team_home_away_types:
        that_object = TeamHomeAwayType(type=that)
        session.add(that_object)
        session.commit()

    # Add Team Stats Types
    team_stats_types = ["Team", "Team/g", "Opponent", "Opponent/g"]
    for tst in team_stats_types:
        tst_object = TeamStatsType(type=tst)
        session.add(tst_object)
        session.commmit()

