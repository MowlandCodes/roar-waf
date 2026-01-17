from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func

from libs import db


class Rule(db.Model):
    """
    Model for storing all rules for the WAF
    """
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    pattern = Column(Text, nullable=False) 
    description = Column(Text, nullable=False)
    risk_level = Column(Enum("LOW", "MEDIUM", "HIGH", name="risk_level"), default="MEDIUM")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Rule {self.name}>"
