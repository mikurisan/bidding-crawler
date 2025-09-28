from abc import ABC
from sqlmodel import Session
from app.db import db_manager
from typing import Optional

class BaseRepository(ABC):
    def __init__(self, session: Optional[Session] = None):
        self._session = session
        self._own_session = session is None
    
    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = db_manager.create_session()
        return self._session
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self._session:
            try:
                if exc_type is None:
                    self._session.commit()
                else:
                    self._session.rollback()
            finally:
                self._session.close()
                self._session = None
