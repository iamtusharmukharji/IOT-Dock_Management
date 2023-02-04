from database import Base, init_db
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import INTEGER, VARCHAR, JSON, DATETIME


init_db()

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
    zone_id = Column(INTEGER, ForeignKey("zone.id"))
    location_id = Column(INTEGER, ForeignKey("location.id"))
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

class LocationCode(Base):
    __tablename__ = "location_code"
    id = Column(INTEGER, primary_key = True, index = True)
    code = Column(INTEGER)
    entity_id = Column(INTEGER, ForeignKey("entity.id"))
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

class DockDetail(Base):
    __tablename__ = "dock_detail"
    id = Column(INTEGER, primary_key = True, index = True)
    topic = Column(VARCHAR(1024), unique=True, index= True)
    location_id = Column(INTEGER, ForeignKey("location.id"))
    dock_status = Column(JSON, nullable = False, default=dict)
    is_deleted = Column(INTEGER)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)