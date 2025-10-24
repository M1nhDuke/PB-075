from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from typing import Generator


# Format: mysql+mysqldb://USER:PASSWORD@HOST:PORT/DATABASE_NAME
SQLALCHEMY_DATABASE_URL = "mysql+mysqldb://USER:PASSWORD@HOST:PORT/DATABASE_NAME"


engine: Engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=3600, # Reconnect after 1 hour
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")


if __name__ == "__main__":
    initialize_db()