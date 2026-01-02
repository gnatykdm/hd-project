import sys
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.seeders import seed_date_dimension, seed_banking_system

def run_seed():
    print("🚀 Connecting to Database...")
    db: Session = SessionLocal()
    try:
        print("📅 Seeding Date Dimension...")
        seed_date_dimension(db)
        
        print("🏦 Seeding Banking System (Customers, Accounts, Transactions)...")
        seed_banking_system(db)
        
        print("Data generation complete!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()
        print("Database connection closed.")

if __name__ == "__main__":
    run_seed()
