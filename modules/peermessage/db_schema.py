from sqlalchemy import Column, String, Integer, Text
from local_db import Base, _get_timestamp

#Encrypted Messaging
class MyKey(Base):
    __tablename__ = 'my_key'
    address = Column(String(250))
    blockindex = Column(Integer)
    tx_id = Column(String(250))
    key = Column(String(250), primary_key=True)
    time = Column(Integer, default=_get_timestamp)

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