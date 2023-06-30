from unittest import TestCase

from models.nba_player import NbaPlayer


class TestNbaPlayer(TestCase):

    def setUp(self):
        self.test_player = NbaPlayer("Test Player 1", "testplayer01")

    def test_update_bpm(self):
        self.fail()