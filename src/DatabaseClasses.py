from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from scripts.Scraper import Scraper
from common.constants import CURRENT_TEAMS, TEAM_ABBRV
import psycopg2

Base = declarative_base()
database = 'mock_nba_database'


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

    minutes_played = Column(String, default=None)
    field_goals = Column(Integer, default=None)
    field_goal_attempts = Column(Integer, default=None)
    field_goal_pct = Column(DECIMAL, default=None)
    three_pointers = Column(Integer, default=None)
    three_point_attempts = Column(Integer, default=None)
    three_point_pct = Column(DECIMAL, default=None)
    free_throws = Column(Integer, default=None)
    free_throw_attempts = Column(Integer, default=None)
    free_throw_pct = Column(DECIMAL, default=None)
    offensive_rebounds = Column(Integer, default=None)
    defensive_rebounds = Column(Integer, default=None)
    total_rebounds = Column(Integer, default=None)
    assists = Column(Integer, default=None)
    steals = Column(Integer, default=None)
    blocks = Column(Integer, default=None)
    turnovers = Column(Integer, default=None)
    personal_fouls = Column(Integer, default=None)
    points = Column(Integer, default=None)
    plus_minus = Column(Integer, default=None)
    true_shooting_pct = Column(DECIMAL, default=None)
    effective_field_goal_pct = Column(DECIMAL, default=None)
    three_point_attempt_rate = Column(DECIMAL, default=None)
    free_throw_attempt_rate = Column(DECIMAL, default=None)
    offensive_rebound_pct = Column(DECIMAL, default=None)
    defensive_rebound_pct = Column(DECIMAL, default=None)
    total_rebound_pct = Column(DECIMAL, default=None)
    assist_pct = Column(DECIMAL, default=None)
    steal_pct = Column(DECIMAL, default=None)
    block_pct = Column(DECIMAL, default=None)
    turnover_pct = Column(DECIMAL, default=None)
    usage_pct = Column(DECIMAL, default=None)
    offensive_rating = Column(DECIMAL, default=None)
    defensive_rating = Column(DECIMAL, default=None)
    box_plus_minus = Column(DECIMAL, default=None)


class GameTeam(Base):
    __tablename__ = "game_team"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("game.id"))
    team_id = Column(Integer, ForeignKey("team.id"))
    team_home_away_type = Column(Integer, ForeignKey("team_home_away_type.id"))
    game_team_log_id = Column(Integer, ForeignKey("game_team_log.id"))
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
    overtime_points = Column(
        String)  # going to store a list of = Column(Integer)s, then we can store infinite overtime_points

    minutes_played = Column(String(6))
    field_goals = Column(Integer)
    field_goal_attempts = Column(Integer)
    field_goal_pct = Column(DECIMAL)
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
    type = Column(String)  # preseason, regular season, play-in, playoffs (CQF, CSF, CF, F)


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
    type = Column(Integer, ForeignKey("player_stats_type.id"))  # 0: season 1: career
    season = Column(String)
    age = Column(Integer, default=None)

    games_played = Column(Integer, default=None)
    games_started = Column(Integer, default=None)
    minutes_played = Column(String, default=None)
    field_goals = Column(DECIMAL, default=None)
    field_goal_attempts = Column(DECIMAL, default=None)
    field_goal_pct = Column(DECIMAL, default=None)
    three_pointers = Column(DECIMAL, default=None)
    three_point_attempts = Column(DECIMAL, default=None)
    three_point_pct = Column(DECIMAL, default=None)
    two_pointers = Column(DECIMAL, default=None)
    two_point_attempts = Column(DECIMAL, default=None)
    two_point_pct = Column(DECIMAL, default=None)
    effective_field_goal_pct = Column(DECIMAL, default=None)
    free_throws = Column(DECIMAL, default=None)
    free_throw_attempts = Column(DECIMAL, default=None)
    free_throw_pct = Column(DECIMAL, default=None)
    offensive_rebounds = Column(DECIMAL, default=None)
    defensive_rebounds = Column(DECIMAL, default=None)
    total_rebounds = Column(DECIMAL, default=None)
    assists = Column(DECIMAL, default=None)
    steals = Column(DECIMAL, default=None)
    blocks = Column(DECIMAL, default=None)
    turnovers = Column(DECIMAL, default=None)
    personal_fouls = Column(DECIMAL, default=None)
    points = Column(DECIMAL, default=None)


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
    name = Column(String)
    abbreviation = Column(String(3))
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
    team_id = Column(Integer, ForeignKey("team.id"))
    type = Column(Integer, ForeignKey("team_stats_type.id"))
    minutes_played = Column(String(6))
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
    team_id = Column(Integer, ForeignKey("team.id"))
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


def initialize_database():
    # TODO: (#2) Figure out how to use drop tables and create tables in code below through SQLAlchemy,
    #  instead of dropping the entire database.
    conn = psycopg2.connect("dbname=nba_master user=jeffreychow")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS {database};')
    cur.execute(f'CREATE DATABASE {database};')
    conn.close()

    engine = create_engine(f'postgresql+psycopg2://jeffreychow:@localhost:5432/{database}')

    # Create tables.
    Base.metadata.create_all(engine)

"""
Populate empty database tables using the scraper.

@param year - Specifies what season's data we are inserting into the database tables.
"""


def populate_tables(year, session):
    s = Scraper()

    schedule_df = s.scrape_nba_season(year)

    season_start_date = s.to_postgres_date(schedule_df['Date'].iloc[0])
    season_end_date = get_season_end_date(schedule_df)

    season = Season(
        year=f"{year}",
        friendly_name=f"NBA Season {year - 1}-{year}",
        season_start=season_start_date,
        season_end=season_end_date
    )

    session.add(season)
    session.flush()

    populate_type_tables(session)
    populate_team_tables(session, season.id)

    # Query for season id.

    for i in schedule_df.index:
        game_datetime = s.to_postgres_datetime(schedule_df['Date'][i], schedule_df['Start (ET)'][i])
        home_team = schedule_df['Home/Neutral'][i]
        away_team = schedule_df['Visitor/Neutral'][i]
        game_code = s.get_game_code(schedule_df['Date'][i], home_team)

        # TODO: (#3) Correct assignment of game types.
        game = Game(
            season_id=season.id,
            type=2,  # 2: regular season
            start_datetime=game_datetime,
            game_code=game_code
        )
        session.add(game)
        session.flush()

        game_summary, home_box, away_box = s.scrape_nba_match(game.game_code)
        # Game Summary headers: Team | 1 | 2 | 3 | 4 | (OT) | T | Pace | eFG% | TOV% | ORB% | FT/FGA | ORtg

        home_box_team_stats = home_box.iloc[-1]
        home_team_game_summary = game_summary.iloc[1]
        away_box_team_stats = away_box.iloc[-1]
        away_team_game_summary = game_summary.iloc[0]

        game_home_team = GameTeam(
            game_id=game.id,
            team_id=session.query(Team.id).filter(Team.name == home_team).scalar_subquery(),
            team_home_away_type=1
        )

        session.add(game_home_team)
        session.flush()

        game_home_team_log = GameTeamLog(
            game_team_id=game_home_team.id,

            total_points=home_team_game_summary['T'],
            first_quarter_points=home_team_game_summary['1'],
            second_quarter_points=home_team_game_summary['2'],
            third_quarter_points=home_team_game_summary['3'],
            fourth_quarter_points=home_team_game_summary['4'],
            overtime_points=None,  # TODO: Configure OT calculation.

            minutes_played=home_box_team_stats['MP'],
            field_goals=home_box_team_stats['FG'],
            field_goal_attempts=home_box_team_stats['FGA'],
            field_goal_pct=home_box_team_stats['FG%'],
            three_pointers=home_box_team_stats['3P'],
            three_point_attempts=home_box_team_stats['3PA'],
            three_point_pct=home_box_team_stats['3P%'],
            free_throws=home_box_team_stats['FT'],
            free_throw_attempts=home_box_team_stats['FTA'],
            free_throw_pct=home_box_team_stats['FT%'],
            offensive_rebounds=home_box_team_stats['ORB'],
            defensive_rebounds=home_box_team_stats['DRB'],
            total_rebounds=home_box_team_stats['TRB'],
            assists=home_box_team_stats['AST'],
            steals=home_box_team_stats['STL'],
            blocks=home_box_team_stats['BLK'],
            turnovers=home_box_team_stats['TOV'],
            personal_fouls=home_box_team_stats['PF'],
            points=home_box_team_stats['PTS'],
            plus_minus=None,

            true_shooting_pct=home_box_team_stats['TS%'],
            effective_field_goal_pct=home_box_team_stats['eFG%'],
            three_point_attempt_rate=home_box_team_stats['3PAr'],
            free_throw_attempt_rate=home_box_team_stats['FTr'],
            offensive_rebound_pct=home_box_team_stats['ORB%'],
            defensive_rebound_pct=home_box_team_stats['DRB%'],
            total_rebound_pct=home_box_team_stats['TRB%'],
            assist_pct=home_box_team_stats['AST%'],
            steal_pct=home_box_team_stats['STL%'],
            block_pct=home_box_team_stats['BLK%'],
            turnover_pct=home_box_team_stats['TOV%'],
            usage_pct=home_box_team_stats['USG%'],
            offensive_rating=home_box_team_stats['ORtg'],
            defensive_rating=home_box_team_stats['DRtg'],
            box_plus_minus=None,
            pace=home_team_game_summary['Pace'],
            free_throws_per_field_goal_attempt=home_team_game_summary['FT/FGA'],
        )
        session.add(game_home_team_log)

        for i in home_box.index[:-1]:
            player_name = home_box['Players'][i]
            player_code = home_box['Player Code'][i]
            player = session.query(Player).filter(
                Player.unique_code == player_code and Player.friendly_name == player_name).one_or_none()

            if player is None:
                player = Player(
                    unique_code=player_code,
                    first_name=player_name.split()[0],
                    last_name=player_name.split()[1],
                    friendly_name=player_name
                )

                session.add(player)
                session.flush()

                player_team = PlayerTeam(
                    player_id=player.id,
                    team_id=game_home_team.team_id,
                    # TODO: Replace datetime.now to actual date.
                    start_date=datetime.now()
                )
                session.add(player_team)

            if ("Did Not" in home_box['MP'][i]) or ("Not With" in home_box['MP'][i]):
                game_player_log = GamePlayerLog(
                    player_id=player.id,
                    game_team_id=game_home_team.id
                )
            else:
                game_player_log = GamePlayerLog(
                    player_id=player.id,
                    game_team_id=game_home_team.id,

                    minutes_played=home_box['MP'][i] if (home_box['MP'][i] != '') else None,
                    field_goals=home_box['FG'][i] if (home_box['FG'][i] != '') else None,
                    field_goal_attempts=home_box['FGA'][i] if (home_box['FGA'][i] != '') else None,
                    field_goal_pct=home_box['FG%'][i] if (home_box['FG%'][i] != '') else None,
                    three_pointers=home_box['3P'][i] if (home_box['3P'][i] != '') else None,
                    three_point_attempts=home_box['3PA'][i] if (home_box['3PA'][i] != '') else None,
                    three_point_pct=home_box['3P%'][i] if (home_box['3P%'][i] != '') else None,
                    free_throws=home_box['FT'][i] if (home_box['FT'][i] != '') else None,
                    free_throw_attempts=home_box['FTA'][i] if (home_box['FTA'][i] != '') else None,
                    free_throw_pct=home_box['FT%'][i] if (home_box['FT%'][i] != '') else None,
                    offensive_rebounds=home_box['ORB'][i] if (home_box['ORB'][i] != '') else None,
                    defensive_rebounds=home_box['DRB'][i] if (home_box['DRB'][i] != '') else None,
                    total_rebounds=home_box['TRB'][i] if (home_box['TRB'][i] != '') else None,
                    assists=home_box['AST'][i] if (home_box['AST'][i] != '') else None,
                    steals=home_box['STL'][i] if (home_box['STL'][i] != '') else None,
                    blocks=home_box['BLK'][i] if (home_box['BLK'][i] != '') else None,
                    turnovers=home_box['TOV'][i] if (home_box['TOV'][i] != '') else None,
                    personal_fouls=home_box['PF'][i] if (home_box['PF'][i] != '') else None,
                    points=home_box['PTS'][i] if (home_box['PTS'][i] != '') else None,
                    plus_minus=home_box['+/-'][i] if (home_box['+/-'][i] != '') else None,

                    true_shooting_pct=home_box['TS%'][i] if (home_box['TS%'][i] != '') else None,
                    effective_field_goal_pct=home_box['eFG%'][i] if (home_box['eFG%'][i] != '') else None,
                    three_point_attempt_rate=home_box['3PAr'][i] if (home_box['3PAr'][i] != '') else None,
                    free_throw_attempt_rate=home_box['FTr'][i] if (home_box['FTr'][i] != '') else None,
                    offensive_rebound_pct=home_box['ORB%'][i] if (home_box['ORB%'][i] != '') else None,
                    defensive_rebound_pct=home_box['DRB%'][i] if (home_box['DRB%'][i] != '') else None,
                    total_rebound_pct=home_box['TRB%'][i] if (home_box['TRB%'][i] != '') else None,
                    assist_pct=home_box['AST%'][i] if (home_box['AST%'][i] != '') else None,
                    steal_pct=home_box['STL%'][i] if (home_box['STL%'][i] != '') else None,
                    block_pct=home_box['BLK%'][i] if (home_box['BLK%'][i] != '') else None,
                    turnover_pct=home_box['TOV%'][i] if (home_box['TOV%'][i] != '') else None,
                    usage_pct=home_box['USG%'][i] if (home_box['USG%'][i] != '') else None,
                    offensive_rating=home_box['ORtg'][i] if (home_box['ORtg'][i] != '') else None,
                    defensive_rating=home_box['DRtg'][i] if (home_box['DRtg'][i] != '') else None,
                    box_plus_minus=home_box['BPM'][i] if (home_box['BPM'][i] != '') else None
                )
            session.add(game_player_log)

        game_away_team = GameTeam(
            game_id=game.id,
            team_id=session.query(Team.id).filter(Team.name == away_team).scalar_subquery(),
            team_home_away_type=2
        )
        session.add(game_away_team)
        session.flush()

        game_away_team_log = GameTeamLog(
            game_team_id=game_away_team.id,

            total_points=away_team_game_summary['T'],
            first_quarter_points=away_team_game_summary['1'],
            second_quarter_points=away_team_game_summary['2'],
            third_quarter_points=away_team_game_summary['3'],
            fourth_quarter_points=away_team_game_summary['4'],
            overtime_points=None,  # TODO: Configure OT calculation.

            minutes_played=away_box_team_stats['MP'],
            field_goals=away_box_team_stats['FG'],
            field_goal_attempts=away_box_team_stats['FGA'],
            field_goal_pct=away_box_team_stats['FG%'],
            three_pointers=away_box_team_stats['3P'],
            three_point_attempts=away_box_team_stats['3PA'],
            three_point_pct=away_box_team_stats['3P%'],
            free_throws=away_box_team_stats['FT'],
            free_throw_attempts=away_box_team_stats['FTA'],
            free_throw_pct=away_box_team_stats['FT%'],
            offensive_rebounds=away_box_team_stats['ORB'],
            defensive_rebounds=away_box_team_stats['DRB'],
            total_rebounds=away_box_team_stats['TRB'],
            assists=away_box_team_stats['AST'],
            steals=away_box_team_stats['STL'],
            blocks=away_box_team_stats['BLK'],
            turnovers=away_box_team_stats['TOV'],
            personal_fouls=away_box_team_stats['PF'],
            points=away_box_team_stats['PTS'],
            plus_minus=None,

            true_shooting_pct=away_box_team_stats['TS%'],
            effective_field_goal_pct=away_box_team_stats['eFG%'],
            three_point_attempt_rate=away_box_team_stats['3PAr'],
            free_throw_attempt_rate=away_box_team_stats['FTr'],
            offensive_rebound_pct=away_box_team_stats['ORB%'],
            defensive_rebound_pct=away_box_team_stats['DRB%'],
            total_rebound_pct=away_box_team_stats['TRB%'],
            assist_pct=away_box_team_stats['AST%'],
            steal_pct=away_box_team_stats['STL%'],
            block_pct=away_box_team_stats['BLK%'],
            turnover_pct=away_box_team_stats['TOV%'],
            usage_pct=away_box_team_stats['USG%'],
            offensive_rating=away_box_team_stats['ORtg'],
            defensive_rating=away_box_team_stats['DRtg'],
            box_plus_minus=None,
            pace=away_team_game_summary['Pace'],
            free_throws_per_field_goal_attempt=away_team_game_summary['FT/FGA'],
        )
        session.add(game_away_team_log)

        for i in away_box.index[:-1]:
            player_name = away_box['Players'][i]
            player_code = away_box['Player Code'][i]
            player = session.query(Player).filter(
                Player.unique_code == player_code and Player.friendly_name == player_name).one_or_none()

            if player is None:
                player = Player(
                    unique_code=player_code,
                    first_name=player_name.split()[0],
                    last_name=player_name.split()[1],
                    friendly_name=player_name
                )

                session.add(player)
                session.flush()

                player_team = PlayerTeam(
                    player_id=player.id,
                    team_id=game_away_team.team_id,
                    # TODO: (#13) Scrape PlayerTeam.start_date
                    start_date=datetime.now()
                )
                session.add(player_team)

            if ("Did Not" in away_box['MP'][i]) or ("Not In" in away_box['MP']):
                game_player_log = GamePlayerLog(
                    player_id=player.id,
                    game_team_id=game_away_team.id,
                    minutes_played=away_box['MP'][i] if (away_box['MP'][i] != '') else None
                )
            else:
                game_player_log = GamePlayerLog(
                    player_id=player.id,
                    game_team_id=game_away_team.id,

                    minutes_played=away_box['MP'][i] if (away_box['MP'][i] != '') else None,
                    field_goals=away_box['FG'][i] if (away_box['FG'][i] != '') else None,
                    field_goal_attempts=away_box['FGA'][i] if (away_box['FGA'][i] != '') else None,
                    field_goal_pct=away_box['FG%'][i] if (away_box['FG%'][i] != '') else None,
                    three_pointers=away_box['3P'][i] if (away_box['3P'][i] != '') else None,
                    three_point_attempts=away_box['3PA'][i] if (away_box['3PA'][i] != '') else None,
                    three_point_pct=away_box['3P%'][i] if (away_box['3P%'][i] != '') else None,
                    free_throws=away_box['FT'][i] if (away_box['FT'][i] != '') else None,
                    free_throw_attempts=away_box['FTA'][i] if (away_box['FTA'][i] != '') else None,
                    free_throw_pct=away_box['FT%'][i] if (away_box['FT%'][i] != '') else None,
                    offensive_rebounds=away_box['ORB'][i] if (away_box['ORB'][i] != '') else None,
                    defensive_rebounds=away_box['DRB'][i] if (away_box['DRB'][i] != '') else None,
                    total_rebounds=away_box['TRB'][i] if (away_box['TRB'][i] != '') else None,
                    assists=away_box['AST'][i] if (away_box['AST'][i] != '') else None,
                    steals=away_box['STL'][i] if (away_box['STL'][i] != '') else None,
                    blocks=away_box['BLK'][i] if (away_box['BLK'][i] != '') else None,
                    turnovers=away_box['TOV'][i] if (away_box['TOV'][i] != '') else None,
                    personal_fouls=away_box['PF'][i] if (away_box['PF'][i] != '') else None,
                    points=away_box['PTS'][i] if (away_box['PTS'][i] != '') else None,
                    plus_minus=away_box['+/-'][i] if (away_box['+/-'][i] != '') else None,

                    true_shooting_pct=away_box['TS%'][i] if (away_box['TS%'][i] != '') else None,
                    effective_field_goal_pct=away_box['eFG%'][i] if (away_box['eFG%'][i] != '') else None,
                    three_point_attempt_rate=away_box['3PAr'][i] if (away_box['3PAr'][i] != '') else None,
                    free_throw_attempt_rate=away_box['FTr'][i] if (away_box['FTr'][i] != '') else None,
                    offensive_rebound_pct=away_box['ORB%'][i] if (away_box['ORB%'][i] != '') else None,
                    defensive_rebound_pct=away_box['DRB%'][i] if (away_box['DRB%'][i] != '') else None,
                    total_rebound_pct=away_box['TRB%'][i] if (away_box['TRB%'][i] != '') else None,
                    assist_pct=away_box['AST%'][i] if (away_box['AST%'][i] != '') else None,
                    steal_pct=away_box['STL%'][i] if (away_box['STL%'][i] != '') else None,
                    block_pct=away_box['BLK%'][i] if (away_box['BLK%'][i] != '') else None,
                    turnover_pct=away_box['TOV%'][i] if (away_box['TOV%'][i] != '') else None,
                    usage_pct=away_box['USG%'][i] if (away_box['USG%'][i] != '') else None,
                    offensive_rating=away_box['ORtg'][i] if (away_box['ORtg'][i] != '') else None,
                    defensive_rating=away_box['DRtg'][i] if (away_box['DRtg'][i] != '') else None,
                    box_plus_minus=away_box['BPM'][i] if (away_box['BPM'][i] != '') else None
                )
            session.add(game_player_log)

    session.commit()

    # TODO: (#5) Add advanced analytics tables from player page to PlayerStats
    for player in session.query(Player).all():
        player_stats_df = s.scrape_nba_player(player.unique_code)

        for i in player_stats_df.index[:-1]:
            if player_stats_df['Season'][i] != '':
                player_stats = PlayerStats(
                    player_id=player.id,
                    type=2 if player_stats_df['Season'][i] == 'Career' else 1,  # for Regular Season
                    season=player_stats_df['Season'][i] if (player_stats_df['Season'][i] != 'DNP')
                                                           and (player_stats_df['Season'][i] != '') else None,
                    games_played=player_stats_df['G'][i] if (player_stats_df['G'][i] != 'DNP')
                                                            and (player_stats_df['G'][i] != '') else None,
                    games_started=player_stats_df['GS'][i] if (player_stats_df['GS'][i] != 'DNP')
                                                              and (player_stats_df['GS'][i] != '') else None,
                    minutes_played=player_stats_df['MP'][i] if (player_stats_df['MP'][i] != 'DNP')
                                                               and (player_stats_df['MP'][i] != '') else None,
                    field_goals=player_stats_df['FG'][i] if (player_stats_df['FG'][i] != 'DNP')
                                                            and (player_stats_df['FG'][i] != '') else None,
                    field_goal_attempts=player_stats_df['FGA'][i] if (player_stats_df['FGA'][i] != 'DNP')
                                                                     and (player_stats_df['FGA'][i] != '') else None,
                    field_goal_pct=player_stats_df['FG%'][i] if (player_stats_df['FG%'][i] != 'DNP')
                                                                and (player_stats_df['FG%'][i] != '') else None,
                    three_pointers=player_stats_df['3P'][i] if (player_stats_df['3P'][i] != 'DNP')
                                                               and (player_stats_df['3P'][i] != '') else None,
                    three_point_attempts=player_stats_df['3PA'][i] if (player_stats_df['3PA'][i] != 'DNP')
                                                                      and (player_stats_df['3PA'][i] != '') else None,
                    three_point_pct=player_stats_df['3P%'][i] if (player_stats_df['3P%'][i] != 'DNP')
                                                                 and (player_stats_df['3P%'][i] != '') else None,
                    two_pointers=player_stats_df['2P'][i] if (player_stats_df['2P'][i] != 'DNP')
                                                             and (player_stats_df['2P'][i] != '') else None,
                    two_point_attempts=player_stats_df['2PA'][i] if (player_stats_df['2PA'][i] != 'DNP')
                                                                    and (player_stats_df['2PA'][i] != '') else None,
                    two_point_pct=player_stats_df['2P%'][i] if (player_stats_df['2P%'][i] != 'DNP')
                                                               and (player_stats_df['2P%'][i] != '') else None,
                    effective_field_goal_pct=player_stats_df['eFG%'][i] if (player_stats_df['eFG%'][i] != 'DNP')
                                                                           and (player_stats_df['eFG%'][
                                                                                    i] != '') else None,
                    free_throws=player_stats_df['FT'][i] if (player_stats_df['FT'][i] != 'DNP')
                                                            and (player_stats_df['FT'][i] != '') else None,
                    free_throw_attempts=player_stats_df['FTA'][i] if (player_stats_df['FTA'][i] != 'DNP')
                                                                     and (player_stats_df['FTA'][i] != '') else None,
                    free_throw_pct=player_stats_df['FT%'][i] if (player_stats_df['FT%'][i] != 'DNP')
                                                                and (player_stats_df['FT%'][i] != '') else None,
                    offensive_rebounds=player_stats_df['ORB'][i] if (player_stats_df['ORB'][i] != 'DNP')
                                                                    and (player_stats_df['ORB'][i] != '') else None,
                    defensive_rebounds=player_stats_df['DRB'][i] if (player_stats_df['DRB'][i] != 'DNP')
                                                                    and (player_stats_df['DRB'][i] != '') else None,
                    total_rebounds=player_stats_df['TRB'][i] if (player_stats_df['TRB'][i] != 'DNP')
                                                                and (player_stats_df['TRB'][i] != '') else None,
                    assists=player_stats_df['AST'][i] if (player_stats_df['AST'][i] != 'DNP')
                                                         and (player_stats_df['AST'][i] != '') else None,
                    steals=player_stats_df['STL'][i] if (player_stats_df['STL'][i] != 'DNP')
                                                        and (player_stats_df['STL'][i] != '') else None,
                    blocks=player_stats_df['BLK'][i] if (player_stats_df['BLK'][i] != 'DNP')
                                                        and (player_stats_df['BLK'][i] != '') else None,
                    turnovers=player_stats_df['TOV'][i] if (player_stats_df['TOV'][i] != 'DNP')
                                                           and (player_stats_df['TOV'][i] != '') else None,
                    personal_fouls=player_stats_df['PF'][i] if (player_stats_df['PF'][i] != 'DNP')
                                                               and (player_stats_df['PF'][i] != '') else None,
                    points=player_stats_df['PTS'][i] if (player_stats_df['PTS'][i] != 'DNP')
                                                        and (player_stats_df['PTS'][i] != '') else None
                )
                session.add(player_stats)
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

@param session - SQLAlchemy session.
@return None
"""


def populate_type_tables(session: Session) -> None:
    # Add Game Types
    # TODO: (#6) Differentiate between playoff games by their rounds in `game_type` table.
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
        session.commit()


"""
Populate the team tables with the current teams for the season and initialize their related tables.
Team tables: team, team_stats, team_advanced_stats

@param session - SQLAlchemy session.
@return None
"""


def populate_team_tables(session: Session, season_id) -> None:
    for team in CURRENT_TEAMS:
        season = session.query(Season.year).where(Season.id == season_id).one()[0]
        prev_year = str(int(season) - 1)
        t = Team(
            season_id=season_id,
            name=team,
            abbreviation=TEAM_ABBRV[team],
            friendly_name=f"{prev_year}-{season} {team}",

            wins=0,
            losses=0,
            home_wins=0,
            home_losses=0,
            away_wins=0,
            away_losses=0,
            streak=0,
            last_ten_wins=0,
            last_ten_losses=0,

            ats_wins=0,
            ats_losses=0,
            ats_ties=0,
            ats_home_wins=0,
            ats_home_losses=0,
            ats_home_ties=0,
            ats_away_wins=0,
            ats_away_losses=0,
            ats_away_ties=0
        )
        session.add(t)
        session.flush()

        for i in range(4):
            ts = TeamStats(
                team_id=t.id,
                type=i + 1,
                minutes_played="",
                field_goals=0,
                field_goal_attempts=0,
                three_pointers=0,
                three_point_attempts=0,
                three_point_pct=0,
                two_pointers=0,
                two_point_attempts=0,
                two_point_pct=0,
                free_throws=0,
                free_throw_attempts=0,
                free_throw_pct=0,
                offensive_rebounds=0,
                defensive_rebounds=0,
                total_rebounds=0,
                assists=0,
                steals=0,
                blocks=0,
                turnovers=0,
                personal_fouls=0,
                points=0
            )
            session.add(ts)

        tas = TeamAdvancedStats(
            team_id=t.id,
            wins=0,
            losses=0,
            pythagorean_wins=0,
            pythagorean_losses=0,
            margin_of_victory=0,
            strength_of_schedule=0,
            simple_rating_system=0,
            offensive_rating=0,
            defensive_rating=0,
            pace=0,
            free_throw_attempt_rate=0,
            three_point_attempt_rate=0,
            effective_field_goal_pct=0,
            turnover_pct=0,
            offensive_rebound_pct=0,
            free_throws_per_field_goal_attempt=0,
            opponent_effective_field_goal_pct=0,
            opponent_turnover_pct=0,
            defensive_rebound_pct=0,
            defensive_free_throws_per_field_goal_attempt=0,
        )
        session.add(tas)


"""
Convert a datestring to the postgres date.
@param datetime - Python datetime object.
@return string in PostgreSQL format.
"""


def to_postgres_timestamp(date_string: str) -> str:
    # Convert the input string to a datetime object
    date_obj = datetime.strptime(date_string, '%a, %b %d, %Y')

    # Convert the datetime object to the PostgreSQL timestamp format
    postgres_timestamp = date_obj.strftime('%Y-%m-%d %H:%M:%S')

    return postgres_timestamp

# initialize_database(2022)
