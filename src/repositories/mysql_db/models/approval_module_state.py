from sqlalchemy import Column, Integer, Boolean, JSON
from sqlalchemy.ext.mutable import MutableDict

from ..models import OrmBase, OrmBaseMixin


class ApprovalModuleState(OrmBaseMixin, OrmBase):
    smId = Column(Integer, nullable=False, unique=True)
    enabled = Column(Boolean, default=True, nullable=False)
    pendingTasks = Column(MutableDict.as_mutable(JSON))
    metaData = Column(MutableDict.as_mutable(JSON), default={})  # stores metadata about each task, like labels/views
