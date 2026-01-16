from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from libs import db


class App(db.Model):
    """
    Model for storing all apps that protected by the WAF
    """
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True)
    domain_name = Column(String(200), unique=True, nullable=False)
    upstream_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<App {self.domain_name} -> {self.upstream_url}>"
