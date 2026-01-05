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

3. Install
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env → set DATABASE_URL (e.g. postgresql://user:pass@host:5432/bank_bi or sqlite:///./bank_bi.db)
```

4. (Optional) Migrate
```bash
alembic upgrade head
```

5. Run
```bash
# Windows
./start.bat
# or
python main.py
```

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
- FastAPI endpoints for ETL/data loading
- Sample ETL scripts and data loaders
- Richer dashboards (Plotly / Matplotlib embedded)
- Unit & integration tests

---

## Contributing
Contributions welcome. Please open an issue to discuss major changes before submitting a PR.

---

## License
MIT — see LICENSE.

---

Screenshots, sample datasets and live demos will be added soon.
