from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker
from models import Base
from models import Conversation, Turn
from contextlib import contextmanager


class DBManager:
    def __init__(self):
        # change to localhost when running locally
        host = 'rmlogs.cphifyouepcn.us-east-1.rds.amazonaws.com'  # to change to make it work online
        user = 'admin'
        password = 'pantabanana'
        encoding = 'utf8mb4'
        charset = '?charset=' + encoding
        use_unicode = '&use_unicode=0'
        db_name = 'rm_logs'
        self.engine = create_engine('mysql+pymysql://' + user + ':' + password + '@' + host + '/'+db_name + charset,
                                    pool_recycle=3600, isolation_level="READ COMMITTED", pool_size=20)
        Base.metadata.bind = self.engine
        self.DBSession = sessionmaker(bind=self.engine)
        string_to_access_db = "mysql -h rmlogs.cphifyouepcn.us-east-1.rds.amazonaws.com -P 3306 -u admin --password=\"pantabanana\" rm_logs"

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.DBSession()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def get_conversation_date(self,conversation_id):
        with self.session_scope() as session:
            q = session.query(Conversation.date).distinct() \
                .filter(Conversation.conversation_id==conversation_id)
            results = q.all()
        return results

    def get_related_session_id(self, conversation_id, session):
        q = session.query(Conversation.session_id, Conversation.date).filter(Conversation.conversation_id == conversation_id)
        results = q.all()
        session_id = None
        if len(results) == 0:
            return None, None
        else:
            session_id = results[0][0]
            date = results[0][1]
        return session_id, date

    def get_number_turns(self, conversation_id):
        with self.session_scope() as session:
            session_id, date = self.get_related_session_id(conversation_id,session)

            q = session.query(distinct(Turn.turn)).filter(Turn.session_id==session_id)
            results = q.all()
        if len(results) == 0:
            return 0
        else:
            return len(results)

    def get_all_conversation_info(self, conversation_id):
        results = None
        date = None
        with self.session_scope() as session:
            session_id,date = self.get_related_session_id(conversation_id, session)
            if session_id is not None:
                q = session.query(Turn).filter(Turn.session_id==session_id)
                results = q.all()
                session.expunge_all()
        return results, date

    def close(self):
        self.engine.dispose()