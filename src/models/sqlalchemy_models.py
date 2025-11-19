from __future__ import annotations

from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.sql import func

from src.database.core import Base


class WaitingList(Base):
    __tablename__ = "waiting_list"

    waiting_list_id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    name_user = Column(Text, nullable=True)
    email_user = Column(Text, nullable=True)

