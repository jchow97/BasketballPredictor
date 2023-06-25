from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from service.database_service import DatabaseService
from scripts.Scraper import Scraper
from service.nba_pipeline import NbaPredictor

username = 'jeffreychow'
port = '5432'
database = 'nba_test'


def main():
    engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:{port}/{database}')
    session = Session(engine)
    scraper = Scraper()
    db_service = DatabaseService(session, scraper)

    scraper.scrape_odds_data(2022)
    # # db_service.initialize_database()
    # # db_service.populate_tables(2022)
    #
    # predictor = NbaPredictor(db_service, [2022])
    # predictor.train_model()
    #
    # predictor.run_prediction(2023)
    # result = predictor.check_prediction()
    # print(result)
    # return


if __name__ == "__main__":
    main()
