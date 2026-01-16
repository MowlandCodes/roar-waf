from sqlalchemy import Boolean, Column, Enum, Integer, String, Text

from libs import db


class Rule(db.Model):
    """
    Model for storing all rules for the WAF
    """
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    pattern = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    risk_level = Column(Enum("LOW", "MEDIUM", "HIGH"), default="MEDIUM")
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Rule {self.name}>"
