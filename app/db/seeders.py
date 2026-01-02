import random
from datetime import datetime, timedelta, date
from typing import List, Final
from faker import Faker
from sqlalchemy.orm import Session

from app.db.models import (
    Customer, Branch, Account, Transaction, 
    DailyBalance, DateDim, AccountType
)

NUM_BRANCHES: Final[int] = 5
NUM_CUSTOMERS: Final[int] = 50
DAYS_OF_HISTORY: Final[int] = 30

fake: Faker = Faker()

def seed_date_dimension(db: Session) -> None:
    start_date: date = date.today() - timedelta(days=365)
    for i in range(367):
        curr: date = start_date + timedelta(days=i)
        date_entry = DateDim(
            date_key=curr,
            year=curr.year,
            quarter=(curr.month - 1) // 3 + 1,
            month=curr.month,
            day_of_week=curr.strftime('%A'),
            is_weekend=curr.weekday() >= 5
        )
        db.add(date_entry)
    print("Date Dimension populated.")

def seed_banking_system(db: Session) -> None:
    regions: List[str] = ["North", "South", "East", "West", "HQ"]
    branches: List[Branch] = []
    for _ in range(NUM_BRANCHES):
        branch = Branch(
            branch_name=f"{fake.city()} Center",
            branch_code=fake.unique.bothify(text='BR-####'),
            region=random.choice(regions)
        )
        db.add(branch)
        branches.append(branch)
    
    db.flush()

    segments: List[str] = ["Retail", "Corporate", "Wealth Management", "SME"]
    customers: List[Customer] = []
    for _ in range(NUM_CUSTOMERS):
        customer = Customer(
            full_name=fake.name(),
            email=fake.unique.email(),
            credit_score=random.randint(300, 850),
            customer_segment=random.choice(segments)
        )
        db.add(customer)
        customers.append(customer)
    
    db.flush()

    categories: List[str] = ["Groceries", "Salary", "Rent", "Dining", "Investment", "Transfer"]
    
    for cust in customers:
        for _ in range(random.randint(1, 2)):
            account = Account(
                customer_id=cust.id,
                branch_id=random.choice(branches).id,
                account_number=fake.unique.iban(),
                account_type=random.choice(list(AccountType)).value,
                is_active=True
            )
            db.add(account)
            db.flush()

            running_balance: float = random.uniform(5000.0, 20000.0)
            
            for d in range(DAYS_OF_HISTORY):
                current_date: datetime = datetime.now() - timedelta(days=d)
                
                for _ in range(random.randint(0, 4)):
                    amount: float = round(random.uniform(-1000.0, 1500.0), 2)
                    running_balance += amount
                    
                    tx = Transaction(
                        account_id=account.id,
                        amount=amount,
                        category=random.choice(categories),
                        merchant_name=fake.company(),
                        timestamp=current_date
                    )
                    db.add(tx)
                
                balance_snapshot = DailyBalance(
                    account_id=account.id,
                    balance_date=current_date.date(),
                    ending_balance=round(running_balance, 2)
                )
                db.add(balance_snapshot)

    db.commit()
    print(f"Successfully seeded {NUM_CUSTOMERS} customers and their financial history.")
