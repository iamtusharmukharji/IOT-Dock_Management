
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

eng = create_engine("sqlite:///web_services/dockManagement.db", echo=True)

Base = declarative_base()

def init_db(): 
    Base.metadata.create_all(eng)
    return