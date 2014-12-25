from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    Text,
    DateTime,
    String,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

EngineMssql = ['']
    
from ..models import Base, DefaultModel

class KodeModel(DefaultModel):
    kode = Column(String(32))
    disabled = Column(SmallInteger, nullable=False)
    created  = Column(DateTime, nullable=False)
    updated  = Column(DateTime)
    create_uid  = Column(Integer, nullable=False)
    update_uid  = Column(Integer)
    
    @classmethod
    def get_by_kode(kode):
        return cls.query().filter_by(kode=kode).first()
        
    @classmethod
    def get_nama(uraian):
        return cls.query().filter_by(kode=kode)

    
class UraianModel(KodeModel):
    uraian = Column(String(128))
    @classmethod
    def get_by_uraian(uraian):
        return cls.query().filter_by(uraian=uraian).first()
        
    @classmethod
    def get_nama(uraian):
        return cls.query().filter_by(uraian=uraian)


class NamaModel(KodeModel):
    nama = Column(String(128))
    
    @classmethod
    def get_by_nama(nama):
        return cls.query().filter_by(nama=nama).first()
        
    @classmethod
    def get_nama(nama):
        return cls.query().filter_by(nama=nama)

class RouteModel(Base, NamaModel):
    __tablename__  = 'routes'
    __table_args__ = {'extend_existing':True}
    path     = Column(String(256), nullable=False)
    factory  = Column(String(256))
    
    
        