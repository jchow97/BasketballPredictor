from bs4 import BeautifulSoup, Comment
from urllib.error import HTTPError
import pandas as pd
import requests
from datetime import datetime
from src.common.constants import TEAM_ABBRV, MONTHS_ABBRV, MONTHS
import time
import re
from unidecode import unidecode

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
        self.__accessCounter = 0
        self.__timeoutSeconds = 3

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
    @return pandas DataFrame of the season schedule.
    """

    def scrape_nba_season(self, season: int) -> pd.DataFrame or None:
        print(f"Beginning scrape for {season} season.")
        # TODO: (#7) Add the summer months (july, aug, sept) to the months being scraped.
        # TODO: revert temporary changes.
        # months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
        months = ["june"]

        # List of DataFrame, each df represents one month in the calendar
        schedule = []

        for month in months:
            # Open URL, request the html, and create BeautifulSoup object
            try:
                url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html"
                time.sleep(self.__timeoutSeconds)
                html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
                self.__accessCounter += 1
                print("count: " + str(self.__accessCounter) + " url: " + url)

                if html.status_code == 404:
                    print("The month or season does not exist.")
                    return None

                soup = BeautifulSoup(html.text, 'lxml')
            except HTTPError as e:
                print("An HTTPError occurred!")
                print(e)
                # TODO: (#8) Add exception handling to Scraper class
                return None
            except:
                print("Unknown Error")
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
            final_schedule = pd.concat(schedule, ignore_index=True)
            return final_schedule
        except:
            print(f"Failed to scrape {season} schedule.")
            return None

    """
    Scrape the nba match and returns a collection of data frames from the match.
    
    @param game_code - game_code string for the website
    @param url - URL for specific game. Default is None. If specified, overrides specified season.
    @return Collection of pandas DataFrames
    """

    def scrape_nba_match(self, game_code, url=None) -> list[pd.DataFrame]:
        try:
            if url is None:
                url = f'https://www.basketball-reference.com/boxscores/{game_code}.html'

            time.sleep(self.__timeoutSeconds)
            html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
            self.__accessCounter += 1
            print("count: " + str(self.__accessCounter) + " url: " + url)

            soup = BeautifulSoup(html.text, 'lxml')
        except HTTPError as e:
            print("Error occurred!")
            print(e)
        else:
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

            # Changed adv headers to be statically set here, rather than dynamically scraped because Play-In Game's don't
            # track BPM.
            # TODO: (#8) Add dynamic handling for Play-In Games when scraping matches

            # if len(ls_headers) > 6:  # checking if there was OT need to make dynamic (e.g. 2OT, 3OT)
            #     i = len(ls_headers) - 6
            #     box_headers_adv = [th.get_text() for th in soup.find_all('table')[7 + i].find_all('th')][4:19]
            # else:
            #     box_headers_adv = [th.get_text() for th in soup.find_all('table')[7].find_all('th')][4:19]

            box_headers_adv = ['TS%', 'eFG%', '3PAr', 'FTr', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%',
                               'USG%', 'ORtg', 'DRtg', 'BPM']

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
            v_rows_basic, v_rows_adv = self.__parse_box_scores(visitor_basic_table, visitor_adv_table)

            # TODO: (#8) Add dynamic handling for Play-In Games when scraping matches
            if len(v_rows_adv[0]) < 15:
                for row in v_rows_adv:
                    row.append(None)

            v_basic_df = pd.DataFrame(v_rows_basic, columns=box_headers_basic)
            v_adv_df = pd.DataFrame(v_rows_adv, columns=box_headers_adv)
            v_box_score = pd.concat([v_basic_df, v_adv_df], axis=1)

            # Scrape the values in each row for the home team in both Basic and Advanced Box Scores.
            h_rows_basic, h_rows_adv = self.__parse_box_scores(home_basic_table, home_adv_table)

            # TODO: (#8) Add dynamic handling for Play-In Games when scraping matches
            if len(h_rows_adv[0]) < 15:
                for row in h_rows_adv:
                    row.append(None)

            h_basic_df = pd.DataFrame(h_rows_basic, columns=box_headers_basic)
            h_adv_df = pd.DataFrame(h_rows_adv, columns=box_headers_adv)
            h_box_score = pd.concat([h_basic_df, h_adv_df], axis=1)

            return game_summary, h_box_score, v_box_score

    """
    Scrapes one NBA Team and returns a collection of data frames on the team page.

    @param team - team name (e.g. TODO)
    @param season - year (e.g. 2022 is 2021-2022)
    @param html_file - relative path for specified html file. Default is None. If specified, overrides specified season.
    @return Collection of 3 pandas DataFrame
    """

    def scrape_nba_team(self, team, season, html_file=None) -> list[pd.DataFrame]:
        pass

    """
    Scrapes an NBA Player and returns a collection of data frames on the player page.

    @param player_code - unique player code used to find their stats page.
    @param url - Specific url of player to scrape. Default is None If specified, ignores player_code input.
    @return pandas DataFrame of player stats.
    """

    def scrape_nba_player(self, player_code, url=None) -> pd.DataFrame or None:
        last_initial = player_code[0]
        if url is None:
            url = f'https://www.basketball-reference.com/players/{last_initial}/{player_code}.html'

        try:
            time.sleep(self.__timeoutSeconds)
            html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
            self.__accessCounter += 1
            print("count: " + str(self.__accessCounter) + " url: " + url)

            soup = BeautifulSoup(html.text, 'lxml')
        except HTTPError as e:
            print("Error occured!")
            print(e)
        else:
            pg_stats = soup.find(id='per_game')

            if pg_stats is None:
                print("This guy isn't important enough to scrape.")
                return None

            # for other functions.
            pgstats_headers = [th.get_text() for th in pg_stats.find('tr').find_all('th')]
            # ['Season', 'Age', 'Tm', 'Lg', 'Pos', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', 
            # '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB','DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

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
    Converts date string from basketball-reference to PostgreSQL date format
    @param date_str - Basketball-reference date string format.
    @return string - PostgreSQL formatted date string.
    """

    def to_postgres_date(self, date_str: str) -> str:
        # Parse the input string into a datetime object
        date = datetime.strptime(date_str, '%a, %b %d, %Y')
        return date.strftime('%Y-%m-%d %H:%M:%S')

    """
    Converts date and time from basketball-reference to PostgreSQL date format
    @param date_str - Basketball-reference date string format.
    @param time_str - Basketball-reference time string format
    @return string - PostgreSQL formatted date string.
    """

    def to_postgres_datetime(self, date_str: str, time_str: str) -> str:
        # Parse the input string into a datetime object
        formatted_date = datetime.strptime(date_str, '%a, %b %d, %Y').date()
        time_str = time_str.replace('p', 'PM')
        time_str = time_str.replace('a', 'AM')
        formatted_time = datetime.strptime(time_str, '%I:%M%p').time()

        return datetime.combine(formatted_date, formatted_time).strftime('%Y-%m-%d %H:%M:%S')

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

    def get_game_code(self, date, home_team) -> str:
        parsed_date = date.split()
        game_date_year = parsed_date[3]
        game_date_month = MONTHS_ABBRV[parsed_date[1]]
        game_date_day = parsed_date[2][:-1]
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

                # Get Player Code
                player_code = ''
                if player != 'Team Totals':
                    player_code = basic_table[i].find('a', string=player)['href'].split('/')[-1].split('.')[0]

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
