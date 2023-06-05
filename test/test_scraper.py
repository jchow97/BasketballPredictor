import unittest

import pandas as pd

from scripts.Scraper import Scraper


class TestScraper(unittest.TestCase):

    def setUp(self) -> None:
        self.test_scraper = Scraper()
        self.arbitrary_season_year = '2000'


    def test_scrape_nba_match(self):
        self.test_scraper.scrape_nba_match('202110190MIL', 'https://www.basketball-reference.com/boxscores/202110190MIL.html')


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")
