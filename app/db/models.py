from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

class AccountType(enum.Enum):
    SAVINGS = "SAVINGS"
    CHECKING = "CHECKING"

class Customer(Base):
    __tablename__ = "dim_customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    credit_score: Mapped[Optional[int]]
    customer_segment: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    accounts: Mapped[List["Account"]] = relationship(back_populates="customer")

class Branch(Base):
    __tablename__ = "dim_branches"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_name: Mapped[str] = mapped_column(String(100))
    branch_code: Mapped[str] = mapped_column(String(20), unique=True)
    region: Mapped[Optional[str]] = mapped_column(String(50))
    
    accounts: Mapped[List["Account"]] = relationship(back_populates="branch")

class Account(Base):
    __tablename__ = "dim_accounts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("dim_customers.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("dim_branches.id"))
    account_number: Mapped[str] = mapped_column(String(50), unique=True)
    account_type: Mapped[str] = mapped_column(String(50)) # e.g., Savings, Checking
    is_active: Mapped[bool] = mapped_column(default=True)
    
    customer: Mapped["Customer"] = relationship(back_populates="accounts")
    branch: Mapped["Branch"] = relationship(back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="account")

class Transaction(Base):
    __tablename__ = "fact_transactions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("dim_accounts.id"))
    amount: Mapped[float]
    category: Mapped[str] = mapped_column(String(100))
    merchant_name: Mapped[Optional[str]] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    account: Mapped["Account"] = relationship(back_populates="transactions")

class DailyBalance(Base):
    __tablename__ = "fact_daily_balances"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("dim_accounts.id"))
    balance_date: Mapped[date]
    ending_balance: Mapped[float]

class DateDim(Base):
    __tablename__ = "dim_date"
    
    date_key: Mapped[date] = mapped_column(primary_key=True)
    year: Mapped[int]
    quarter: Mapped[int]
    month: Mapped[int]
    day_of_week: Mapped[str] = mapped_column(String(10))
    is_weekend: Mapped[bool] = mapped_column(default=False)
