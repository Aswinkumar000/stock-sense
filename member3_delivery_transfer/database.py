from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Local SQLite file for development/testing.
# NOTE: This is provisional. Once the team confirms the real shared
# database (Postgres/MySQL/etc.), the SQLALCHEMY_DATABASE_URL below
# will be swapped out. All model definitions should remain compatible.
SQLALCHEMY_DATABASE_URL = "sqlite:///./stocksense_member3.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()