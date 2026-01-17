from sqlalchemy.exc import OperationalError

from libs import db
from libs.logger import logger
from main import app
from models import App, Rule


def seed():
    logger.info("Memulai ritual penanaman data...")
    
    with app.app_context():
        try:
            db.create_all()
        except (OperationalError, Exception) as e:
            logger.error(f"Terjadi kesalahan saat membuat tabel: {e}")
            return
            
        
        logger.info("Adding Rules...")
        
        # Basic Rules (OWASP Top 10 Low Budget Version)
        initial_rules = [
            {
                "name": "SQL Injection Basic",
                "pattern": r"(?i)(union[\s+]+select|select[\s+]+from|insert[\s+]+into|update[\s+]+set|delete[\s+]+from|drop[\s+]+table|alter[\s+]+table)",
                "description": "Basic SQL Injection",
                "risk_level": "HIGH"
            },
            {
                "name": "XSS Script Tag",
                "pattern": r"(?i)(<script.*?>|<\/script>|javascript:|onload=|onerror=)",
                "description": "Cross-Site Scripting (XSS)",
                "risk_level": "MEDIUM"
            },
            {
                "name": "Path Traversal (LFI)",
                "pattern": r"(?i)(\.\./|\.\.\\|/etc/passwd|c:\\windows)",
                "description": "Local File Inclusion (LFI)",
                "risk_level": "HIGH"
            },
            {
                "name": "Command Injection",
                "pattern": r"(?i)(;|\||`|\$|\(|\)|exec|eval)", 
                "description": "Basic Command Injection",
                "risk_level": "CRITICAL"
            },
            {
                "name": "Log4Shell (Legacy)",
                "pattern": r"(?i)\$\{jndi:(ldap|rmi|dns):",
                "description": "Log4Shell (Legacy)",
                "risk_level": "HIGH"
            }
        ]

        for data in initial_rules:
            exists = Rule.query.filter_by(name=data["name"]).first()
            if not exists:
                rule = Rule(
                    name=data["name"],
                    pattern=data["pattern"],
                    description=data["description"],
                    risk_level=data["risk_level"],
                    is_active=True
                )
                db.session.add(rule)
                logger.info(f"Added Rule: {data['name']}")
            else:
                logger.warning(f"Skipped Rule: {data['name']} (Already exists)")

        logger.info("Seeding Apps...")

        initial_apps = [
            {
                "domain_name": "localhost",
                "upstream_url": "http://roar_victim:80" 
            }
        ]

        for data in initial_apps:
            exists = App.query.filter_by(domain_name=data["domain_name"]).first()
            if not exists:
                app_entry = App(
                    domain_name=data["domain_name"],
                    upstream_url=data["upstream_url"],
                    is_active=True
                )
                db.session.add(app_entry)
                logger.info(f"Added App: {data['domain_name']} -> {data['upstream_url']}")
            else:
                logger.warning(f"Skipped App: {data['domain_name']} (Already exists)")

        try:
            db.session.commit()
            logger.info("Seeding Finished!")
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Error on commit: {e}")

if __name__ == "__main__":
    seed()
