from bs4 import BeautifulSoup
from urllib.error import HTTPError
import pandas as pd
import psycopg2
import re
from sqlalchemy import create_engine
import requests
import datetime
from common.constants import TEAM_ABBRV, MONTHS_ABBRV

"""
The scraper should be responsible for generating data frames to form the database. Adding entities to the database should be done
elsewhere

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
        self.__USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'

    """
    Scrapes everything.

    @param seasons - list of seasons to scrape. Note: the 2021-2022 season would be season 2022
    @param database - PostgresSQL to create the tables in. Default is 'nba_database'
    @return None
    """
    def scrape_everything(self, seasons) -> None:
        print(f"Scrape Everything")

        for season in seasons:
            self.scrape_nba_season(self, season)

    """
    Scrapes one NBA Season Schedule and returns a collection of schedules.

    @param season - NBA Season to scrape. Note: the 2021-2022 season would be season 2022
    @param database - PostgresSQL to create the tables in. Default is 'nba_database'
    @return pandas DataFrame of the season schedule.
    """
    def scrape_nba_season(self, season) -> pd.DataFrame:
        print(f"beginning scrape for {season} season.")
        #TODO: add handling for july, aug, sept
        months = months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]

        # List of DataFrame, each df represents one month in the calendar
        schedule = []

        for month in months:
            # Open URL and create BeautifulSoup object
            try:
                url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html"
                # html = urlopen(url)
                html = requests.get(url, headers={'User-Agent': self.__USER_AGENT})
                soup = BeautifulSoup(html.text, 'lxml')
            except HTTPError as e:
                print("Error occured!")
                print(e)
                #TODO: Add error class for error handling
                return None
            except:
                print("The month or season does not exist.")
                return None
            else:
                # Extract headers into a list. Expected headers:
                # ['Date', 'Start (ET)', 'Visitor/Neutral', 'PTS', 'Home/Neutral', 'PTS', '\xa0', '\xa0', 'Attend.', 'Arena', 'Notes']
                headers = [th.get_text() for th in soup.find_all('tr', limit=2)[0].find_all('th')]

                table = soup.find_all('tr')[1:]
                
                # Scrape the values in each row.
                # Can't use List Comprehension because the 'date' column is under 'th' tag and not 'td'.
                rows_data = self.parse_table_rows(table)
                rows_df = pd.DataFrame(rows_data, columns = headers)
                schedule.append(rows_df)
        
        try:
            # create the final data frame
            final_schedule = pd.concat(schedule)
            return final_schedule
        except:
            print(f"Failed to scrape {season} schedule.")
            return None

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

    @param name - Name of the player.
    @param birth_date - birth_date of the player.
    @return pandas DataFrame of player stats.
    """
    def scrape_nba_player(self, name, birth_date) -> pd.DataFrame:
        pass

    # HELPER FUNCTIONS

    """
    Get Player Code based on trying to access their webpage on Basketball Reference.

    @param name - Name of the player.
    @param bd - Birth date of the player (e.g. 'January 1, 2022')
    @return str - player code that was determined.
    """
    def __get_player_code(self, name, bd) -> str:
        player_code_base = ''
        player_name = name.split()
        player_birth = bd.split()
        
        p_month = MONTHS[player_birth[0]]
        p_day = player_birth[1][:-1] # to remove the comma
        if len(p_day) == 1:
            p_day = '0' + p_day
        p_year = player_birth[2]

        # use birth code to find and finalize player code.
        birth_code = p_year + '-' + p_month + '-' + p_day

        ln_length = min(len(player_name[1]), 5)
        for i in range(ln_length):
            player_code_base = player_code_base + player_name[1][i]

        fn_length = min(len(player_name[0]), 2)
        for i in range(fn_length):
            player_code_base = player_code_base + player_name[0][i]

        player_code_base = player_code_base.lower()

        last_initial = player_name[1][0].lower()
        player_found = False
        player_number = 1
        player_code = ''

        while not player_found:
            try:
                player_code = player_code_base + str(player_number).zfill(2)
                
                url = f'https://www.basketball-reference.com/players/{last_initial}/{player_code}.html'
                html = requests.get(url, headers={'User-Agent': USER_AGENT})
                soup = BeautifulSoup(html.text, 'lxml')
                
                birth = [item['data-birth'] for item in soup.find_all('span', attrs={'data-birth' : True})][0]
                if birth == birth_code:
                    player_found = True
                else:
                    player_number += 1
            except HTTPError:
                logging.exception("This player does not exist.")
                break
        return player_code


    """
    Converts date string from basketball-reference to PostgreSQL date format
    @param date_string - Basketball-reference date string format.
    @return string - formatted date string.
    """
    def to_postgres_date(self, date_string: str) -> str:
        # Parse the input string into a datetime object
        date = datetime.datetime.strptime(date_string, '%a, %b %d, %Y')
        # Return the date in the PostgreSQL date format
        return date.strftime('%Y-%m-%d')

    """
    Parse row data from given table.

    @param table - BeautifulSoup Table to Parse
    @return Nested list of row data for the table.
    """
    def parse_table_rows(self, table, mode=0) -> list():
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