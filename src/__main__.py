import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from service.database_service import DatabaseService
from scripts.Scraper import Scraper
from service.nba_pipeline import NbaPredictor

username = 'jeffreychow'
port = '5432'
database = 'nba_test'


def main():
    # Set Parameters
    training_years = [2022]
    prediction_year = 2022

    engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:{port}/{database}')
    session = Session(engine)
    scraper = Scraper()
    db_service = DatabaseService(session, scraper, engine)

    # Scraper-related methods
    db_service.initialize_database()
    db_service.populate_tables(2022)
    # odds_data: pd.DataFrame = scraper.scrape_odds_data(2022)
    # db_service.add_odds_data(odds_data)

    predictor = NbaPredictor(db_service, training_years)
    predictor.train_model()

    predictor.run_prediction_for_season(prediction_year)
    return


if __name__ == "__main__":
    main()
