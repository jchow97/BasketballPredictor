from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from scripts.Scraper import Scraper
from common.constants import CURRENT_TEAMS, TEAM_ABBRV
import psycopg2

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
    age = Column(Integer)

    games_played = Column(Integer)
    games_started = Column(Integer)
    minutes_played = Column(String(6))
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


def initialize_database(year, database='mock_nba_database'):
    # TODO: Figure out how to use drop tables and create tables in code below through SQLAlchemy,
    #  instead of dropping the entire database.
    conn = psycopg2.connect("dbname=nba_master user=jeffreychow")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f'DROP DATABASE IF EXISTS {database};')
    cur.execute(f'CREATE DATABASE {database};')
    conn.close()

    engine = create_engine(f'postgresql+psycopg2://jeffreychow:@localhost:5432/{database}')
    session = Session(engine)

    # Drop old and create new database tables
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    s = Scraper()

    schedule_df = s.scrape_nba_season(year)
    players = dict()

    season = Season(
        year=f"{year}",
        friendly_name=f"NBA Season {year - 1}-{year}",
        season_start=s.to_postgres_date(schedule_df['Date'].iloc[0]),
        season_end=get_season_end_date(schedule_df)
    )

    session.add(season)
    session.flush()

    populate_type_tables(session)
    populate_team_tables(session, season.id)

    # Query for season id.

    for i in schedule_df.index:
        game_datetime = schedule_df['Date'][i]
        home_team = schedule_df['Home/Neutral'][i]
        away_team = schedule_df['Visitor/Neutral'][i]

        game = Game(
            season_id=season.id,
            # TODO: scrape playoff games too
            type=1,
            start_datetime=s.to_postgres_date(game_datetime),
            game_code=s.get_game_code(game_datetime, home_team)
        )
        session.add(game)
        session.flush()

        game_summary, home_box, away_box = s.scrape_nba_match(game.game_code)
        # TODO: find an example of a box score in old db and use that to help query for team totals row.
        # Game Summary headers: Team | 1 | 2 | 3 | 4 | (OT) | T | Pace | eFG% | TOV% | ORB% | FT/FGA | ORtg
        """
        Game Summary Example:
        Team | one | two | three | four | _OT | T   | Pace | eFG_pct | TOV_pct | ORB_pct | FT_FGA | ORtg  
       ------+-----+-----+-------+------+-----+-----+------+---------+---------+---------+--------+-------
        NOP  | 32  | 27  | 24    | 29   | 13  | 125 | 95.6 | .576    | 8.6     | 18.8    | .111   | 118.4
        CHO  | 27  | 31  | 20    | 34   | 10  | 122 | 95.6 | .515    | 7.5     | 22.4    | .167   | 115.6

            Players      |      MP       | FG | FGA | FG_pct | _3P | _3PA | _3P_pct | FT | FTA | FT_pct | ORB | DRB | TRB | AST | STL | BLK | TOV | PF | PTS | plus_minus | TS_pct | eFG_pct | _3PAr |  FTr  | ORB_pct | DRB_pct | TRB_pct | AST_pct | STL_pct | BLK_pct | TOV_pct | USG_pct | ORtg  | DRtg  |  BPM  
        ------------------+---------------+----+-----+--------+-----+------+---------+----+-----+--------+-----+-----+-----+-----+-----+-----+-----+----+-----+------------+--------+---------+-------+-------+---------+---------+---------+---------+---------+---------+---------+---------+-------+-------+-------
        Hassan Whiteside | 33:36         | 7  | 14  | .500   | 0   | 0    |         | 3  | 6   | .500   | 3   | 13  | 16  | 0   | 1   | 2   | 0   | 0  | 17  | +15        | .511   | .500    | .000  | .429  | 11.3    | 40.4    | 27.2    | 0.0     | 1.5     | 4.7     | 0.0     | 22.1    | 117   | 97    | 2.4
        Wayne Ellington  | 33:07         | 3  | 11  | .273   | 2   | 9    | .222    | 3  | 3   | 1.000  | 0   | 2   | 2   | 5   | 2   | 1   | 0   | 2  | 11  | +13        | .446   | .364    | .818  | .273  | 0.0     | 6.3     | 3.5     | 17.8    | 3.1     | 2.4     | 0.0     | 16.6    | 119   | 104   | 3.5
        Goran Dragić     | 30:55         | 14 | 23  | .609   | 2   | 5    | .400    | 4  | 4   | 1.000  | 2   | 3   | 5   | 5   | 1   | 0   | 3   | 4  | 34  | +26        | .687   | .652    | .217  | .174  | 8.2     | 10.1    | 9.2     | 33.4    | 1.6     | 0.0     | 10.8    | 40.1    | 132   | 107   | 12.9
        Rodney McGruder  | 30:27         | 3  | 5   | .600   | 1   | 2    | .500    | 0  | 0   |        | 1   | 2   | 3   | 1   | 0   | 0   | 1   | 4  | 7   | +5         | .700   | .700    | .400  | .000  | 4.1     | 6.9     | 5.6     | 3.9     | 0.0     | 0.0     | 16.7    | 8.8     | 124   | 112   | -3.9
        Josh McRoberts   | 17:46         | 3  | 8   | .375   | 1   | 3    | .333    | 0  | 0   |        | 3   | 5   | 8   | 5   | 0   | 0   | 1   | 1  | 7   | +4         | .438   | .438    | .375  | .000  | 21.3    | 29.4    | 25.7    | 36.6    | 0.0     | 0.0     | 11.1    | 22.6    | 118   | 106   | 5.9
        James Johnson    | 30:14         | 6  | 9   | .667   | 0   | 2    | .000    | 2  | 4   | .500   | 2   | 3   | 5   | 3   | 0   | 0   | 2   | 1  | 14  | +7         | .651   | .667    | .222  | .444  | 8.4     | 10.4    | 9.5     | 13.4    | 0.0     | 0.0     | 15.7    | 18.9    | 122   | 111   | 0.2
        Tyler Johnson    | 29:50         | 5  | 10  | .500   | 1   | 2    | .500    | 0  | 0   |        | 0   | 3   | 3   | 3   | 1   | 0   | 2   | 3  | 11  | -3         | .550   | .550    | .200  | .000  | 0.0     | 10.5    | 5.7     | 13.1    | 1.7     | 0.0     | 16.7    | 18.0    | 102   | 107   | -3.3
        Josh Richardson  | 29:03         | 4  | 7   | .571   | 2   | 3    | .667    | 0  | 0   |        | 0   | 4   | 4   | 3   | 1   | 0   | 2   | 2  | 10  | -2         | .714   | .714    | .429  | .000  | 0.0     | 14.4    | 7.9     | 12.9    | 1.7     | 0.0     | 22.2    | 13.9    | 117   | 106   | 1.8
        Willie Reed      | 5:03          | 0  | 1   | .000   | 0   | 0    |         | 1  | 2   | .500   | 0   | 1   | 1   | 0   | 0   | 0   | 0   | 1  | 1   | -10        | .266   | .000    | .000  | 2.000 | 0.0     | 20.7    | 11.3    | 0.0     | 0.0     | 0.0     | 0.0     | 16.6    | 64    | 108   | -15.5
        Justise Winslow  | Did Not Dress |    |     |        |     |      |         |    |     |        |     |     |     |     |     |     |     |    |     |            |        |         |       |       |         |         |         |         |         |         |         |         |       |       | 
        Derrick Williams | Did Not Play  |    |     |        |     |      |         |    |     |        |     |     |     |     |     |     |     |    |     |            |        |         |       |       |         |         |         |         |         |         |         |         |       |       | 
        Udonis Haslem    | Did Not Play  |    |     |        |     |      |         |    |     |        |     |     |     |     |     |     |     |    |     |            |        |         |       |       |         |         |         |         |         |         |         |         |       |       | 
        Luke Babbitt     | Did Not Play  |    |     |        |     |      |         |    |     |        |     |     |     |     |     |     |     |    |     |            |        |         |       |       |         |         |         |         |         |         |         |         |       |       | 
        Team Totals      | 240           | 45 | 88  | .511   | 9   | 26   | .346    | 13 | 19  | .684   | 11  | 36  | 47  | 25  | 6   | 3   | 11  | 18 | 112 |            | .581   | .563    | .295  | .216  | 28.9    | 78.3    | 56.0    | 55.6    | 6.3     | 4.9     | 10.2    | 100.0   | 118.1 | 106.5 | 
        
        + Player Code 2nd column.
        """

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
                    # TODO: Replace datetime.now to actual date.
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

    # TODO: Improve PlayerStats table to be able to cover all the other tables on the player page (e.g. per game, total, per 36, playoffs for each, etc).
    for player in session.query(Player).all():
        player_stats_df = s.scrape_nba_player(player.unique_code)

        for i in player_stats_df.index[:-1]:
            player_stats = PlayerStats(
                player_id=player.id,
                type=1,  # for Regular Season
                season=player_stats_df['Season'][i],
                games_played=player_stats_df['G'][i],
                games_started=player_stats_df['GS'][i],
                minutes_played=player_stats_df['MP'][i],
                field_goals=player_stats_df['FG'][i],
                field_goal_attempts=player_stats_df['FGA'][i],
                field_goal_pct=player_stats_df['FG%'][i],
                three_pointers=player_stats_df['3P'][i],
                three_point_attempts=player_stats_df['3PA'][i],
                three_point_pct=player_stats_df['3P%'][i],
                two_pointers=player_stats_df['2P'][i],
                two_point_attempts=player_stats_df['2PA'][i],
                two_point_pct=player_stats_df['2P%'][i],
                effective_field_goal_pct=player_stats_df['eFG%'][i],
                free_throws=player_stats_df['FT'][i],
                free_throw_attempts=player_stats_df['FTA'][i],
                free_throw_pct=player_stats_df['FT%'][i],
                offensive_rebounds=player_stats_df['ORB'][i],
                defensive_rebounds=player_stats_df['DRB'][i],
                total_rebounds=player_stats_df['TRB'][i],
                assists=player_stats_df['AST'][i],
                steals=player_stats_df['STL'][i],
                blocks=player_stats_df['BLK'][i],
                turnovers=player_stats_df['TOV'][i],
                personal_fouls=player_stats_df['PF'][i],
                points=player_stats_df['PTS'][i]
            )

            session.add(player_stats)

        player_stats_regular_season_totals = player_stats_df.iloc[-1]
        player_stats_reg_career = PlayerStats(
            player_id=player.id,
            type=2,  # for Regular Season Career
            season=player_stats_regular_season_totals['Season'],
            games_played=player_stats_regular_season_totals['G'],
            games_started=player_stats_regular_season_totals['GS'],
            minutes_played=player_stats_regular_season_totals['MP'],
            field_goals=player_stats_regular_season_totals['FG'],
            field_goal_attempts=player_stats_regular_season_totals['FGA'],
            field_goal_pct=player_stats_regular_season_totals['FG%'],
            three_pointers=player_stats_regular_season_totals['3P'],
            three_point_attempts=player_stats_regular_season_totals['3PA'],
            three_point_pct=player_stats_regular_season_totals['3P%'],
            two_pointers=player_stats_regular_season_totals['2P'],
            two_point_attempts=player_stats_regular_season_totals['2PA'],
            two_point_pct=player_stats_regular_season_totals['2P%'],
            effective_field_goal_pct=player_stats_regular_season_totals['eFG%'],
            free_throws=player_stats_regular_season_totals['FT'],
            free_throw_attempts=player_stats_regular_season_totals['FTA'],
            free_throw_pct=player_stats_regular_season_totals['FT%'],
            offensive_rebounds=player_stats_regular_season_totals['ORB'],
            defensive_rebounds=player_stats_regular_season_totals['DRB'],
            total_rebounds=player_stats_regular_season_totals['TRB'],
            assists=player_stats_regular_season_totals['AST'],
            steals=player_stats_regular_season_totals['STL'],
            blocks=player_stats_regular_season_totals['BLK'],
            turnovers=player_stats_regular_season_totals['TOV'],
            personal_fouls=player_stats_regular_season_totals['PF'],
            points=player_stats_regular_season_totals['PTS']
        )
        session.add(player_stats_reg_career)
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
