from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DB_URL = "postgresql+psycopg:///db_plataforma"

engine = create_engine(DB_URL)
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = Session()
    try:
        yield db 
    finally:
        db.close()