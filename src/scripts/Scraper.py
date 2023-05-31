from bs4 import BeautifulSoup
from bs4 import Comment
from urllib.error import HTTPError
import pandas as pd
import psycopg2
import re
from sqlalchemy import create_engine
import requests
import datetime
from src.common.constants import TEAM_ABBRV, MONTHS_ABBRV, MONTHS

"""
The scraper should be responsible for generating data frames to form the database. Adding entities to the database 
should be done elsewhere

Pages (links) that the scraper would like to scrape:
 - Note: f-strings
 - date: date in YYYYMMDD format
 - team_abrv: abbreviation of team
 - year: year in YYYY format
 - month: month in lowercase string format (e.g. october, november, etc.)
 - last_initial: first letter of the player's last name (e.g. Damian Lillard's last_initial is l)
 - player_code: string composed of: first 5 chars of last name + first 2 chars of first name + 01 
    (incremented for duplicate names)
    - e.g. Damian Lillard -> lillada01; Gary Payton Sr. -> paytoga01; Gary Payton II -> paytoga02.
        - Number at the end is incremented by whichever player came into the league first (? probably)

    NBA Schedule: f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html"
    Match/Box Score Page: f"https://www.basketball-reference.com/boxscores/{date}0{home_team_abrv}.html"
    Team Page: f"https://www.basketball-reference.com/teams/{team_abrv}/{year}.html"
    Player Page: f"https://www.basketball-reference.com/players/{last_initial}/{player_code}.html"
"""


class Scraper:

    def __init__(self):
        # TODO: Consider upgrading Agent to an entire request header
        self.__USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                            'Chrome/103.0.0.0 Safari/537.36'

    """
    Scrapes every specified NBA season (seasons, schedules, matches, teams, players) 

    @param seasons - list of seasons to scrape. Note: the 2021-2022 season would be season 2022
    @param database - PostgresSQL to create the tables in. Default is 'nba_database'
    @return None
    """

    def scrape_nba_seasons(self, seasons) -> None:
        print(f"Scrape Everything")

        for season in seasons:
            self.scrape_nba_season(season)

    """
    Scrapes one NBA Season Schedule and returns a collection of schedules.

    @param season - NBA Season to scrape. Note: the 2021-2022 season would be season 2022
    @param database - PostgresSQL to create the tables in. Default is 'nba_database'
    @return pandas DataFrame of the season schedule.
    """

    def scrape_nba_season(self, season) -> pd.DataFrame or None:
        print(f"Beginning scrape for {season} season.")
        # TODO: add handling for july, aug, sept
        months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]

        # List of DataFrame, each df represents one month in the calendar
        schedule = []

        for month in months:
            # Open URL, request the html, and create BeautifulSoup object
            try:
                url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html"
                # html = urlopen(url)
                html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
                soup = BeautifulSoup(html.text, 'lxml')
            except HTTPError as e:
                print("Error occured!")
                print(e)
                # TODO: Add error class for error handling
                return None
            except:
                print("The month or season does not exist.")
                return None
            else:
                # Extract headers into a list. Expected headers:
                # ['Date', 'Start (ET)', 'Visitor/Neutral', 'PTS', 'Home/Neutral', 'PTS', '\xa0', '\xa0', 'Attend.',
                #  'Arena', 'Notes']
                headers = [th.get_text() for th in soup.find_all('tr', limit=2)[0].find_all('th')]

                # Extract the actual table.
                table = soup.find_all('tr')[1:]

                # From the table, we parse each row to get a list of "games" from that month.
                # Note: Can't use List Comprehension because the 'date' column is under 'th' tag and not 'td'.
                rows_data = self.parse_table_rows(table)

                # Convert the table into a data frame.
                rows_df = pd.DataFrame(rows_data, columns=headers)

                # Add the month's schedule to the final schedule.
                schedule.append(rows_df)

        try:
            # Concatenate all the months together into one single data frame.
            final_schedule = pd.concat(schedule)
            return final_schedule
        except:
            print(f"Failed to scrape {season} schedule.")
            return None

    """
    Scrape the nba match and returns a collection of data frames from the match.
    
    @param game_code - game_code string for the website
    @return Collection of pandas DataFrames
    """

    def scrape_nba_match(self, game_code) -> list[pd.DataFrame]:
        # TODO: take the match scraper from old scraper, then remove the unneeded parts.
        try:
            url = f'https://www.basketball-reference.com/boxscores/{game_code}.html'
            html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
            soup = BeautifulSoup(html.text, 'lxml')
        except HTTPError as e:
            print("Error occured!")
            print(e)
        else:
            # TODO: Line Score and Four Factors Headers + Tables
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            ls = -1  # index for line_score comment
            ff = -1  # index for four_factors comment
            for i in range(len(comments)):
                if 'line_score' in comments[i]:
                    ls = i
                elif 'four_factors' in comments[i]:
                    ff = i
            comment_ls_soup = BeautifulSoup(comments[ls], 'lxml')
            comment_ff_soup = BeautifulSoup(comments[ff], 'lxml')

            ls_headers = [th.get_text() for th in comment_ls_soup.find('table').find_all('th')[1:-2]]
            # ['\xa0', '1', '2', '3', '4', 'T'] Optional: OT
            ff_headers = [th.get_text() for th in comment_ff_soup.find('table').find_all('th')[4:-2]]
            # ['\xa0', 'Pace', 'eFG%', 'TOV%', 'ORB%', 'FT/FGA', 'ORtg']

            # Change blank line score header to "Team"
            ls_headers[0] = "Team"

            line_score_table = comment_ls_soup.find('table').find_all('tr')[2:]
            four_factors_table = comment_ff_soup.find('table').find_all('tr')[2:]

            ls_rows = self.parse_table_rows(line_score_table)
            ff_rows = self.parse_table_rows(four_factors_table, 1)

            ls_df = pd.DataFrame(ls_rows, columns=ls_headers)
            ff_df = pd.DataFrame(ff_rows, columns=ff_headers)
            game_summary = pd.concat([ls_df, ff_df], axis=1)

            # Scrape for Basic Box Score Stat Headers and Advanced Box Score Stat Headers and merge into one big
            # header list.
            box_headers_basic = [th.get_text() for th in soup.find('table').find_all('th')][2:23]
            box_headers_basic[0] = 'Players'

            if len(ls_headers) > 6:  # checking if there was OT need to make dynamic (e.g. 2OT, 3OT)
                i = len(ls_headers) - 6
                box_headers_adv = [th.get_text() for th in soup.find_all('table')[7 + i].find_all('th')][4:19]
            else:
                box_headers_adv = [th.get_text() for th in soup.find_all('table')[7].find_all('th')][4:19]

            # Add player code to basic box header.
            box_headers_basic.insert(1, "Player Code")

            if len(ls_headers) > 6:
                i = len(ls_headers) - 6
                visitor_basic_table = soup.find_all('table')[0].find_all('tr')
                visitor_adv_table = soup.find_all('table')[7 + i].find_all('tr')
                home_basic_table = soup.find_all('table')[8 + i].find_all('tr')
                home_adv_table = soup.find_all('table')[15 + (2 * i)].find_all('tr')
            else:
                visitor_basic_table = soup.find_all('table')[0].find_all('tr')
                visitor_adv_table = soup.find_all('table')[7].find_all('tr')
                home_basic_table = soup.find_all('table')[8].find_all('tr')
                home_adv_table = soup.find_all('table')[15].find_all('tr')

            # Scrape the values in each row for the visitor team in both Basic and Advanced Box Scores.
            # TODO parse_row_data() is too simple/standard for this table at the moment.
            v_rows_basic, v_rows_adv = self.__parse_box_scores(visitor_basic_table, visitor_adv_table)

            v_basic_df = pd.DataFrame(v_rows_basic, columns=box_headers_basic)
            v_adv_df = pd.DataFrame(v_rows_adv, columns=box_headers_adv)
            v_box_score = pd.concat([v_basic_df, v_adv_df], axis=1)

            # Scrape the values in each row for the home team in both Basic and Advanced Box Scores.
            h_rows_basic, h_rows_adv = self.__parse_box_scores(home_basic_table, home_adv_table)

            h_basic_df = pd.DataFrame(h_rows_basic, columns=box_headers_basic)
            h_adv_df = pd.DataFrame(h_rows_adv, columns=box_headers_adv)
            h_box_score = pd.concat([h_basic_df, h_adv_df], axis=1)

            return game_summary, h_box_score, v_box_score

    """
    Scrapes one NBA Team and returns a collection of data frames on the team page.

    @param team - team name (e.g. TODO)
    @param season - year (e.g. 2022 is 2021-2022)
    @return Collection of 3 pandas DataFrame
    """

    def scrape_nba_team(self, team, season) -> list[pd.DataFrame]:
        pass

    """
    Scrapes an NBA Player and returns a collection of data frames on the player page.

    @param player_code - unique player code used to find their stats page.
    @return pandas DataFrame of player stats.
    """

    def scrape_nba_player(self, player_code) -> pd.DataFrame or None:
        last_initial = player_code[0]
        url = f'https://www.basketball-reference.com/players/{last_initial}/{player_code}.html'

        try:
            html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
            soup = BeautifulSoup(html.text, 'lxml')
        except HTTPError as e:
            print("Error occured!")
            print(e)
        else:
            pg_stats = soup.find(id='per_game')

            if pg_stats is None:
                print("This guy isn't important enough to scrape.")
                return None

            # TODO filtering table in line above, then 'tr' then 'th' may be a better way to get table headers
            # for other functions.
            pgstats_headers = [th.get_text() for th in pg_stats.find('tr').find_all('th')]
            # ['Season', 'Age', 'Tm', 'Lg', 'Pos', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', 
            # '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB','DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

            pgstats_headers = self.format_headers(pgstats_headers)

            pgstats_table = pg_stats.find_all('tr')[1:]
            pgstats_rows = []

            for i in range(len(pgstats_table)):
                try:
                    number = pgstats_table[i].find('th').get_text()
                    data = [td.get_text() for td in pgstats_table[i].find_all('td')]
                    data.insert(0, number)
                except AttributeError:
                    # for DNP seasons
                    data = [td.get_text() for td in pgstats_table[i].find_all('td')]
                    dnp = ['DNP'] * 27
                    data = data + dnp
                pgstats_rows.append(data)

            pg_stats_df = pd.DataFrame(pgstats_rows, columns=pgstats_headers)

            return pg_stats_df

    # HELPER FUNCTIONS

    """
    Get Player Code Base (e.g. lillada of lillada01)

    @param name - Name of the player.
    @return str - player code that was determined.
    """

    def __get_player_code_base(self, name) -> str:
        player_code_base = ''
        player_name = name.split()

        ln_length = min(len(player_name[1]), 5)
        for i in range(ln_length):
            player_code_base = player_code_base + player_name[1][i]

        fn_length = min(len(player_name[0]), 2)
        for i in range(fn_length):
            player_code_base = player_code_base + player_name[0][i]

        player_code_base = player_code_base.lower()

        return player_code_base

    """
    Converts date string from basketball-reference to PostgreSQL date format
    @param date_string - Basketball-reference date string format.
    @return string - formatted date string.
    """

    def to_postgres_date(self, date_string: str):
        # Parse the input string into a datetime object
        date = datetime.datetime.strptime(date_string, '%a, %b %d, %Y')

        # Return the date in the PostgreSQL date format
        return date.strftime('%Y-%m-%d')

    """
    Parse row data from given table.

    @param table - BeautifulSoup Table to Parse
    @return Nested list of row data for the table.
    """

    def parse_table_rows(self, table, mode=0) -> []:
        # Scrape the values in each row.
        # Can't use List Comprehension because the 'date' column is under 'th' tag and not 'td'.
        rows_data = []
        if mode == 0:
            for i in range(len(table)):
                zero_col = table[i].find('th').get_text()
                data = [td.get_text() for td in table[i].find_all('td')]
                data.insert(0, zero_col)
                rows_data.append(data)
        elif mode == 1:
            for i in range(len(table)):
                data = [td.get_text() for td in table[i].find_all('td')]
                rows_data.append(data)
        return rows_data

    """
    Gets the basketball-reference game-code based on the date and home team
    
    @param date - date-string
    @param home_team - home team 3-letter abbreviation.
    @return string of game code.
    """

    def __get_game_code(self, date, home_team) -> str:
        game_date_year = date[3]
        game_date_month = MONTHS_ABBRV[date[1]]
        game_date_day = date[2][:-1]
        if len(game_date_day) == 1:
            game_date_day = '0' + game_date_day

        game_code = game_date_year + game_date_month + game_date_day + '0' + TEAM_ABBRV[home_team]

        return game_code

    """
    Parse table data for team basic and advanced box scores.

    @param basic_table - Team's basic box score.
    @param adv_table - Team's advanced box score.
    @return basic_rows, adv_rows - Team's nested list of row data for advanced and box score respectively.
    TODO add return signature. Not sure how to signature 2 return values.
    """

    def __parse_box_scores(self, basic_table, adv_table):
        basic_rows = []
        adv_rows = []
        for i in range(2, len(basic_table)):
            if i != 7:
                player = basic_table[i].find('th').get_text()
                basic_data = [td.get_text() for td in basic_table[i].find_all('td')]
                basic_data.insert(0, player)

                player_code_base = self.__get_player_code_base(player)
                player_code = basic_table[i].select(f"a[href*={player_code_base}]")
                basic_data.insert(1, player_code)

                adv_data = [td.get_text() for td in adv_table[i].find_all('td')[1:]]
                basic_rows.append(basic_data)
                adv_rows.append(adv_data)
        return basic_rows, adv_rows

    """
    Helper function to format column headers to fit SQL header convention, not including special cases.

    @param header - the list of column headers to be formatted.
    @return list of formatted headers
    """
    def format_headers(self, headers: list[str]) -> list[str]:
        for i in range(len(headers)):
            headers[i] = headers[i].replace("3", "_3")
            headers[i] = headers[i].replace("2", "_2")
            headers[i] = headers[i].replace("%", "_pct")
            headers[i] = headers[i].replace('+', 'plus')
            headers[i] = headers[i].replace('-', 'minus')
            headers[i] = headers[i].replace('/', '_')
            headers[i] = headers[i].replace('.', '_')
            headers[i] = headers[i].replace(' ', '')
        return headers
