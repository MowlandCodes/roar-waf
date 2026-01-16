from sqlalchemy import Column, DateTime, Integer, String, Text

from libs import db


class AttackLog(db.Model):
    """
    Model for storing all attack logs that are blocked by the WAF
    """
    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    src_ip = Column(String(20), nullable=False)
    target_domain = Column(String(255), nullable=False)
    matched_rule = Column(String(100), nullable=False)
    payload_sample = Column(Text)
