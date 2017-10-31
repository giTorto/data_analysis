from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import BIGINT, VARCHAR, TEXT, MEDIUMTEXT, DATE, MEDIUMINT, SMALLINT, DECIMAL, DATETIME
from sqlalchemy import Column, ForeignKey, Index


Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversations'
    session_id = Column(VARCHAR(256),primary_key=True)
    conversation_id = Column(VARCHAR(128))
    date = Column(DATE)
    rating = Column(DECIMAL(3,2,True))

class Turn(Base):
    __tablename__ = 'turns'
    id = Column(MEDIUMINT(),primary_key=True)
    user_id = Column(VARCHAR(256))
    session_id = Column(VARCHAR(256))
    turn = Column(MEDIUMINT)
    utterance = Column(TEXT)
    reply = Column(TEXT)
    run_info = Column(TEXT)
    time = Column(DATETIME)
