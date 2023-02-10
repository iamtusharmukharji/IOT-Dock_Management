from database import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.sqlite import INTEGER, VARCHAR, JSON, DATETIME



class Zone(Base):
    __tablename__ = "zone"
    id = Column(INTEGER, primary_key = True, index = True)
    zone = Column(VARCHAR(1024))
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

class Location(Base):
    __tablename__ = "location"
    id = Column(INTEGER, primary_key = True, index = True)
    zone_id = Column(INTEGER, ForeignKey("zone.id"))
    location = Column(VARCHAR(1024))
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

class Entity(Base):
    __tablename__ = "entity"
    id = Column(INTEGER, primary_key = True, index = True)
    entity = Column(VARCHAR(1024))
    cost_code = Column(INTEGER)
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

class LocationCode(Base):
    __tablename__ = "location_code"
    id = Column(INTEGER, primary_key = True, index = True)
    code = Column(INTEGER)
    entity_id = Column(INTEGER, ForeignKey("entity.id"))
    location_id = Column(INTEGER, ForeignKey("location.id"))
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

class Device(Base):
    __tablename__ = "device"
    id = Column(INTEGER, primary_key = True, index = True)
    device_id = Column(VARCHAR(1024), unique=True, index= True)
    topic = Column(VARCHAR(1024))
    location_code = Column(INTEGER, ForeignKey("location.id"))
    total_connected_docks = Column(INTEGER)
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)