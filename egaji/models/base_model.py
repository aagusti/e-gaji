from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
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

from ..models import Base, DefaultModel

class KodeModel(DefaultModel):
    kode = Column(String(32))
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

        