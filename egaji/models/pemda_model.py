from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    String,
    ForeignKey
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from ..models import Base

from base_model import NamaModel

class UrusanModel(Base, NamaModel):
    __tablename__  = 'urusans'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'admin',}

class UnitModel(Base, NamaModel):
    __tablename__  = 'units'
    __table_args__ = {'extend_existing':True, 
                      'schema' : 'admin',}
    urusan_id = Column(Integer, ForeignKey('admin.urusans.id'))
    
