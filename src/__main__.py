import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from service.database_service import DatabaseService
from scripts.Scraper import Scraper
from service.nba_pipeline import NbaPredictor

username = 'jeffreychow'
port = '5432'
database = 'nba_dev'


def main():
    # Set Parameters
    scrape_years = [2022]
    training_years = [2017, 2018, 2019, 2021]
    prediction_year = 2022

    engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:{port}/{database}')
    session = Session(engine)
    scraper = Scraper()
    db_service = DatabaseService(session, scraper, engine)

    # Scraper-related methods; uncomment if we need to re-initialize the database.
    # db_service.initialize_database()
    for year in scrape_years:
        db_service.populate_tables(year)
        odds_data: pd.DataFrame = scraper.scrape_odds_data(year)
        if odds_data is None:
            continue
        db_service.add_odds_data(odds_data)

    # predictor = NbaPredictor(db_service, training_years)
    # predictor.train_model()
    #
    # predictor.run_prediction_for_season(prediction_year)
    # predictor.check_profit(f'data/{prediction_year}_prediction.csv', float(1000), float(0.05), float(5))
    return


if __name__ == "__main__":
    main()
