from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from service.database_service import DatabaseService
from scripts.Scraper import Scraper
from service.nba_pipeline import NbaPredictor

username = 'jeffreychow'
port = '5432'
database = 'nba_dev'


def main():
    engine = create_engine(f'postgresql+psycopg2://{username}:@localhost:{port}/{database}')
    session = Session(engine)
    scraper = Scraper()
    db_service = DatabaseService(session, scraper)

    # db_service.initialize_database()
    # db_service.populate_tables(2022)

    predictor = NbaPredictor(db_service, [2022])
    training_input, training_output, input_context = predictor.train_model()
    predictor.pipeline.fit(training_input, training_output)

    predictor.run_prediction(2023)
    result = predictor.check_prediction()
    print(result)
    return


if __name__ == "__main__":
    main()
