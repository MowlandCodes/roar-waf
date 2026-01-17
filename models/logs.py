from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from libs import db


class AttackLog(db.Model):
    """
    Model for storing all attack logs that are blocked by the WAF
    """
    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    src_ip = Column(String(20), nullable=False)
    target_domain = Column(String(255), nullable=False)
    matched_rule = Column(String(100), nullable=False)
    payload_sample = Column(Text)

    def __init__(self, src_ip: str, target_domain: str, matched_rule: str, payload_sample: str | None = None):
        self.src_ip = src_ip
        self.target_domain = target_domain
        self.matched_rule = matched_rule
        
        if payload_sample:
            self.payload_sample = payload_sample

    def __repr__(self):
        return f"<Log {self.src_ip} -> {self.matched_rule}>"
