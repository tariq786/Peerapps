from sqlalchemy import Column, String, Integer, Text
from __init__ import Base, _get_timestamp

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