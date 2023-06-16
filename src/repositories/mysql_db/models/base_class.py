from typing import Any

from sqlalchemy import Integer, Column, DateTime, func
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declarative_base, declarative_mixin, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str


OrmBase = declarative_base()
OrmBase.registry.configure()


@declarative_mixin
class OrmBaseMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    createdAt = Column(DateTime(timezone=True), default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
