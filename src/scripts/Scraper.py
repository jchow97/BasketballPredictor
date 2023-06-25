from bs4 import BeautifulSoup, Comment
from urllib.error import HTTPError
import pandas as pd
import requests
from datetime import datetime

from pandas import DataFrame

from src.common.constants import MONTHS_ABBRV
import time


class Scraper:
    """
    This class is responsible for web-scraping for data.

    Example of pages (links) that the scraper would like to scrape:
        NBA Schedule: f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month}.html"
        Match/Box Score Page: f"https://www.basketball-reference.com/boxscores/{date}0{home_team_abrv}.html"
        Team Page: f"https://www.basketball-reference.com/teams/{team_abrv}/{year}.html"
        Player Page: f"https://www.basketball-reference.com/players/{last_initial}/{player_code}.html"
    """

    def __init__(self):
        # TODO: Consider upgrading Agent to an entire request header
        self.__USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                            'Chrome/103.0.0.0 Safari/537.36'
        self.__accessCounter = 0
        self.__timeoutSeconds = 3

    def scrape_nba_seasons(self, seasons) -> None:
        """
        Scrapes every specified NBA season (season, schedules, matches, teams, players).
        :param seasons: list of seasons to scrape. Note: the 2021-2022 season would be season 2022.
        :return: None
        """

        print(f"Scrape Everything")
        for season in seasons:
            self.scrape_nba_season(season)

    def scrape_nba_season(self, season: int) -> pd.DataFrame or None:
        """
        Scrapes one NBA Season Schedule and returns a collection of schedules.
        :param season: NBA Season to scrape. Note: the 2021-2022 season would be season 2022.
        :return: Season schedule dataframe.
        """

        print(f"Beginning scrape for {season} season.")
        # TODO: (#7) Add the summer months (july, aug, sept) to the months being scraped.
        months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
        # months = ["june"]

        # List of DataFrame, each df represents one month in the calendar
        schedule = []

        for month in months:
            # Open URL, request the html, and create BeautifulSoup object
            try:
                url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html"
                soup = self.send_request(url)
            except HTTPError as e:
                print("An HTTPError occurred!")
                print(e)
                # TODO: (#8) Add exception handling to Scraper class
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
        except HTTPError:
            print(f"Failed to scrape {season} schedule.")
            return None

    def scrape_nba_match(self, game_code, url=None) -> tuple[DataFrame, DataFrame, DataFrame]:
        """
        Scrape the nba match and returns a collection of data frames from the match.
        :param game_code: Unique game code string for the website.
        :param url: URL for specific game. Default is None. If specified, overrides specified game code.
        :return: List of game summary and box score data frames.
        """

        try:
            if url is None:
                url = f'https://www.basketball-reference.com/boxscores/{game_code}.html'

            soup = self.send_request(url)
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

            # Changed adv headers to be statically set here, rather than dynamically scraped because Play-In Game's
            # don't track BPM.
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
            v_box_score = self.generate_boxscore_dataframes(box_headers_basic, v_rows_basic,
                                                            box_headers_adv, v_rows_adv)

            # Scrape the values in each row for the home team in both Basic and Advanced Box Scores.
            h_rows_basic, h_rows_adv = self.__parse_box_scores(home_basic_table, home_adv_table)
            h_box_score = self.generate_boxscore_dataframes(box_headers_basic, h_rows_basic,
                                                            box_headers_adv, h_rows_adv)

            return game_summary, h_box_score, v_box_score

    def scrape_nba_team(self, team, season, html_file=None) -> list[pd.DataFrame]:
        """
        Scrapes one NBA Team and returns a collection of data frames on the team page.
        :param team: Team name.
        :param season: Year (e.g. 2022 is 2021-2022).
        :param html_file: relative path for specified html file. Default is None.
                          If specified, overrides specified season.
        :return: Collection of 3 dataframes.
        """
        raise NotImplementedError()

    def scrape_nba_player(self, player_code, url=None) -> pd.DataFrame or None:
        """
        Scrapes an NBA Player and returns a collection of data frames on the player page.
        :param player_code: Unique player code used to find their stats page.
        :param url: Specific url of player to scrape. Default is None If specified, ignores player_code input.
        :return: Player stats dataframe.
        """
        last_initial = player_code[0]
        if url is None:
            url = f'https://www.basketball-reference.com/players/{last_initial}/{player_code}.html'

        try:
            soup = self.send_request(url)
        except HTTPError as e:
            print("Error occurred!")
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

    def scrape_odds_data(self, year: int, url=None) -> pd.DataFrame:
        # Ensure the input is an integer
        try:
            year = int(year)
        except ValueError:
            raise ValueError("Please enter a valid year.")

        # Format the year string
        year_string = f"{year - 1}-{str(year)[2:]}"

        if url is None:
            url = f"https://www.sportsbookreviewsonline.com/scoresoddsarchives/nba-odds-{year_string}/"

        try:
            soup = self.send_request(url)
        except HTTPError as e:
            print("Error occurred!")
            print(e)
        else:
            # headers = [td.get_text() for td in soup.find_all('tr', limit=2)[0] if td != '\n']
            headers = ['Date', 'Visitor_Team', 'Home_Team', 'Closing Odds']
            table = [[td.get_text() for td in tr if td != '\n'] for tr in soup.find_all('tr')[1:]]
            data = []
            for i in range(0, len(table), 2):
                date = table[i][0]
                visitor_team = table[i][3]
                home_team = table[i+1][3]
                odds_v = self.convert_to_float_or_zero(table[i][10])
                odds_h = self.convert_to_float_or_zero(table[i + 1][10])

                if odds_v < odds_h:
                    odds = float(odds_v)
                else:
                    odds = -abs(float(odds_h))

                data.append([date, visitor_team, home_team, odds])

            odds_df = pd.DataFrame(data, columns=headers)

            return odds_df

    # HELPER FUNCTIONS

    def send_request(self, url) -> BeautifulSoup or None:
        time.sleep(self.__timeoutSeconds)
        html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
        self.__accessCounter += 1
        print("count: " + str(self.__accessCounter) + " url: " + url)

        if html.status_code == 404:
            print("The month or season does not exist.")
            return None

        return BeautifulSoup(html.text, 'lxml')

    @staticmethod
    def convert_to_float_or_zero(s: str) -> float:
        """
        Converts the string to a float if possible, otherwise returns 0.0
        :param s: Input string
        :return: Float
        """
        try:
            return float(s)
        except ValueError:
            return 0.0

    @staticmethod
    def to_postgres_date(date_str: str) -> str:
        """
        Converts date string from basketball-reference to PostgreSQL date format.
        :param date_str: Basketball-reference date string format.
        :return: Postgres formatted date string.
        """
        # Parse the input string into a datetime object
        date = datetime.strptime(date_str, '%a, %b %d, %Y')
        return date.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def to_postgres_datetime(date_str: str, time_str: str) -> str:
        """
        Converts date and time from basketball-reference to PostgreSQL datetime format
        :param date_str: Basketball-reference date string format.
        :param time_str: Basketball-reference time string format.
        :return: Postgres formatted date string.
        """
        # Parse the input string into a datetime object
        formatted_date = datetime.strptime(date_str, '%a, %b %d, %Y').date()
        time_str = time_str.replace('p', 'PM')
        time_str = time_str.replace('a', 'AM')
        formatted_time = datetime.strptime(time_str, '%I:%M%p').time()

        return datetime.combine(formatted_date, formatted_time).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def parse_table_rows(table, mode=0) -> []:
        """
        Parse row data from given table.
        :param table: Beautiful Soup table to parse.
        :param mode: Mode to determine which types of table to process. **NOT SURE WHAT THIS IS**
        :return:
        """
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

    @staticmethod
    def get_game_code(date, home_team_abbr) -> str:
        """
        Gets the basketball-reference game-code based on the date and home team.
        :param date: Date string
        :param home_team_abbr: Home team's 3-letter abbreviation.
        :return: Game Code string.
        """
        parsed_date = date.split()
        game_date_year = parsed_date[3]
        game_date_month = MONTHS_ABBRV[parsed_date[1]]
        game_date_day = parsed_date[2][:-1]
        if len(game_date_day) == 1:
            game_date_day = '0' + game_date_day

        game_code = game_date_year + game_date_month + game_date_day + '0' + home_team_abbr

        return game_code

    @staticmethod
    def get_player_code(name: str) -> str:
        """
        Gets the basketball-reference player-code based on the player's name and TODO.
        :param name: Player Name
        :return: Unique player code string.
        """

    @staticmethod
    def __parse_box_scores(basic_table, adv_table) -> tuple[list[list], list[list]]:
        """
        Parse table data for team basic and advanced box scores.
        :param basic_table: Team's basic box score.
        :param adv_table: Team's advanced box score.
        :return: basic_rows, adv_rows - Team's nested list of row data for advanced and box score respectively.
        """
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

    @staticmethod
    def generate_boxscore_dataframes(basic_headers: list, basic_rows: list[list],
                                     advanced_headers: list, advanced_rows: list[list]) -> DataFrame:

        # TODO: (#8) Add dynamic handling for Play-In Games when scraping matches
        if len(advanced_rows[0]) < 15:
            for row in advanced_rows:
                row.append(None)

        basic_df = pd.DataFrame(basic_rows, columns=basic_headers)
        adv_df = pd.DataFrame(advanced_rows, columns=advanced_headers)
        return pd.concat([basic_df, adv_df], axis=1)

    @staticmethod
    def format_headers(headers: list[str]) -> list[str]:
        """
        Helper function to format column headers to fit SQL header convention, not including special cases.
        :param headers: The list of column headers to be formatted.
        :return: List of formatted headers
        """
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
