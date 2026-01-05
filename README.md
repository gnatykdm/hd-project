# Bank Intelligence System

A sleek, educational Business Intelligence (BI) demo for banking analytics — built with Python, SQLAlchemy and PyQt6. Explore customers, accounts, branches, transactions and daily balances using a star-schema data warehouse and a modern desktop GUI.

Badges: Python | PyQt6 | SQLAlchemy | MIT

---

## TL;DR
- Star-schema DW for banking analytics (dimensions + fact tables)
- Desktop GUI for interactive exploration and dashboards
- Built for learning, prototyping and small demos

---

## Highlights
- Data modeling with SQLAlchemy (ORM)
- Star schema: dim_accounts (center), dim_customers, dim_branches, dim_date
- Facts: fact_transactions, fact_daily_balances
- Desktop GUI with PyQt6 for dashboards, filters and visualizations
- Configurable DB: PostgreSQL or SQLite via .env
- Optional Alembic migrations

---

## Tech Stack
- Python 3.10+
- SQLAlchemy 2.x
- PyQt6 (GUI)
- Alembic (migrations, optional)
- PostgreSQL / SQLite
- dotenv for configuration

---

## Quickstart

1. Clone
```bash
git clone https://github.com/gnatykdm/hd-project.git
cd hd-project
```

2. Virtualenv
```bash
python -m venv venv
# Windows
venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate
```

3. Install Dependencies and Configure Environment
```bash
# Install required Python packages
pip install -r requirements.txt

# Copy the example environment file
cp .env.example .env

# Set up your database connection (PostgreSQL example)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=bankdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
```

```
4. Run
```bash

# Windows
start.bat

# Unix
./start.sh
```
> The script will automatically run migrations, seeders into your DB, and then start the program.
---

## Project Layout
hd-project/
├── app/                    # core app: db, gui, models, entry
│   ├── db/                 # SQLAlchemy models & config
│   ├── gui/                # PyQt6 windows, widgets, dashboards
│   ├── models/             # domain entities (Customer, Account, Transaction)
│   └── main.py             # app entrypoint
├── migrations/             # Alembic migrations (optional)
├── .env.example
├── requirements.txt
├── start.bat
└── README.md

---

## Planned
- Sample ETL scripts and data loaders
- Richer dashboards (Plotly / Matplotlib embedded)
- Unit & integration tests

---

## License
MIT — see LICENSE.

---

Screenshots, sample datasets and live demos will be added soon.