from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import time
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///peerapps.db', connect_args={'check_same_thread':False})

Base = declarative_base()
Base.metadata.bind = engine

def _get_timestamp():
    return int(time.time())

def setup():
    Base.metadata.create_all(engine) #equiv to "Create Table" sql statements

def get_session():
    DBSession = sessionmaker(bind=engine)
    return DBSession()

import os
for name in os.listdir("./modules/"):
    if os.path.isfile("./modules/"+name+"/db_schema.py"):
        exec "from modules."+name+".db_schema import *"
