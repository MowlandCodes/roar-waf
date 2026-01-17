# ROAR-WAF (Rule Based Web Application Firewall)

> "Security by Regex" — Said no serious security engineer ever, but here we are.

## WHAT IS THIS?

This is a simple web application firewall (WAF) that uses Regex to inspect HTTP headers, query parameters, and request body.

## ARCHITECTURE

The architectural choices are pretty standard for a beginner:

1. Nginx (Front): Acts as the Reverse Proxy / Gatekeeper.
2. Flask (WAF Engine): The middleman handling the inspection logic.
3. PostgreSQL (Database): Stores the sins (logs) of attackers and your regex rules.
4. Backend App (Victim): The application being protected (or the victim of your experiments).

### The Flow

```text
User Request -> Nginx -> WAF Engine (Flask) -> Scanned via Regex Magic -> Backend (if safe) or 403 (if you got caught).
```

## TECH STACK

Here are the tools used to build this project:

- Language: Python 3.14
- Framework: Flask
- Server: Gunicorn
- Database: PostgreSQL
- Containerization: Docker & Docker Compose

## FEATURES (SO-CALLED "SECURITY")

Our WAF filters traffic using basic Regex.

- SQL Injection (Basic & Boolean): Blocks UNION SELECT, OR 1=1, etc.
- XSS (Cross-Site Scripting): Blocks <script>, javascript:, etc.
- LFI (Local File Inclusion): Prevents people from peeking at /etc/passwd.
- Command Injection: Blocks magical characters like ;, |, $.
- Log4Shell (Legacy): You still included this? That vulnerability is so 2021.
- Traffic Inspection: Checks URL params and Body (Head & Tail sampling to save memory, apparently).

## DEPLOYMENT (FOR THE LAZY ONES)

Requirement: You must have Docker and Docker Compose installed. Don't try to install dependencies manually, your laptop might explode.

1. Clone Repo

   ```bash
   git clone https://github.com/mowlandcodes/roar-waf.git
   cd roar-waf
   ```

2. Setup Environment Variables
   Copy the .env.example file (if you made one) or edit docker-compose.yaml directly. Make sure the DATABASE_URL is correct.

3. Fire It Up

   ```bash
   docker compose up --build -d
   ```

   Wait until all containers are healthy.

4. Seeding Rules
   Your database is empty. Fill it with default rules so the WAF actually does something.

   ```bash
   docker exec -it roar_engine python seed.py
   ```

   (Note: This adds basic OWASP Top 10 rules).

5. Test Drive
   Open your browser and go to [http://localhost:8080](http://localhost:8080).
   - Normal access: Should pass through to the 'whoami' backend.
   - Malicious access: Try [http://localhost:8080/?q=' OR 1=1--](<http://localhost:8080/?q=>' OR 1=1--)
   - Result: You should get slapped with a 403 Access Denied.

## FOLDER STRUCTURE

So you don't get lost in your own code:

```text
.
|-- libs/ # Helper functions
|-- models/ # SQLAlchemy models (Apps, Logs, Rules)
|-- nginx/ # Nginx Config (Gateway)
|-- templates/
|-- Dockerfile
|-- docker-compose.yaml # Orchestrator
|-- main.py # The core file
|-- seed.py # Script to populate initial data
|-- requirements.txt # All the Python dependencies
```

## DISCLAIMER

**DO NOT USE THIS IN A LARGE PRODUCTION ENVIRONMENT!**
This is just a `Just4Fun` project. I don't take responsibility for any damage done to your system.

---

<p align="center">Built by <a href="https://github.com/mowlandcodes">MowlandCodes</a>.</p>
