import sys
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.db.seeders import (
    seed_date_dimension,
    seed_banking_system
)

def run_database_setup() -> None:
    """
    Orchestrates the database seeding process with proper 
    session management and error handling.
    """
    print("🚀 Initializing Banking BI Data Seed...")
    
    # Create a new session using the SessionLocal factory
    db: Session = SessionLocal()
    
    try:
        # 1. Populate the Calendar (Dimension)
        print("📅 Populating Date Dimension...")
        seed_date_dimension(db)
        
        print("🏦 Generating Customers, Accounts, and Transactions...")
        seed_banking_system(db)
        
        db.commit()
        print("✨ Database successfully populated and committed.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Critical Error during seeding: {e}", file=sys.stderr)
        sys.exit(1)
        
    finally:
        db.close()
        print("Database connection closed.")

if __name__ == '__main__':
    run_database_setup()
