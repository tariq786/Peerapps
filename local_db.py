from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import time
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///peermessage.db', connect_args={'check_same_thread':False})

Base = declarative_base()
Base.metadata.bind = engine

def _get_timestamp():
    return int(time.time())

class MyKey(Base):
    __tablename__ = 'my_key'
    address = Column(String(250))
    blockindex = Column(Integer)
    tx_id = Column(String(250))
    key = Column(String(250), primary_key=True)
    time = Column(Integer, default=_get_timestamp)

#MICROBLOGGING
class Broadcast(Base):
    __tablename__ = 'broadcast'
    address_from = Column(String(250))
    blockindex = Column(Integer)
    tx_id = Column(String(250))
    msg = Column(Text())
    key = Column(String(250), primary_key=True)
    time = Column(Integer, default=_get_timestamp)

class Subscription(Base):
    __tablename__ = 'subscription'
    address = Column(String(250))
    tag = Column(String(250))
    key = Column(String(250), primary_key=True)
    time = Column(Integer, default=_get_timestamp)

#Encrypted Messaging
class Ignore(Base): #spamlist
    __tablename__ = 'ignore'
    address = Column(String(250))
    tag = Column(String(250))
    key = Column(String(250), primary_key=True)
    time = Column(Integer, default=_get_timestamp)

class PublicKey(Base):
    __tablename__ = 'public_key'
    address = Column(String(250))
    tag = Column(String(250))
    blockindex = Column(Integer)
    tx_id = Column(String(250))
    key = Column(String(250), primary_key=True)
    time = Column(Integer, default=_get_timestamp)

class Message(Base):
    __tablename__ = 'message'
    address_from = Column(String(250))
    address_to = Column(String(250))
    blockindex = Column(Integer)
    tx_id = Column(String(250))
    msg = Column(Text())
    key = Column(String(250), primary_key=True)
    time = Column(Integer, default=_get_timestamp)

class BlockchainScan(Base):
    __tablename__ = 'blockchain_scan'
    last_index = Column(Integer, primary_key=True)

class MemPoolScan(Base):
    __tablename__ = 'mempool_scan'
    txids_scanned = Column(Text(), primary_key=True)

def setup():
    Base.metadata.create_all(engine) #equiv to "Create Table" sql statements

def get_session():
    DBSession = sessionmaker(bind=engine)
    return DBSession()